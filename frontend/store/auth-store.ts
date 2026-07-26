"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import api, { clearAuthStorage } from "@/lib/api";
import type {
  CurrentUser,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  Role,
} from "@/lib/types";

interface AuthState {
  user: CurrentUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<void>;
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: CurrentUser) => void;
  clearError: () => void;
  reset: () => void;
}

function storeTokens(access: string, refresh: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  }
}

function pickName(u: {
  name?: string | null;
  fullName?: string | null;
  full_name?: string | null;
  email?: string;
}): string {
  return (u.name || u.fullName || u.full_name || u.email || "User") as string;
}

function normalizeUser(
  raw:
    | CurrentUser
    | ({ id: string; email: string } & Record<string, unknown>)
): CurrentUser {
  const r = raw as Record<string, unknown>;
  return {
    id: String(r.id ?? ""),
    email: String(r.email ?? ""),
    name: pickName({
      name: r.name as string | null | undefined,
      fullName: r.fullName as string | null | undefined,
      full_name: r.full_name as string | null | undefined,
      email: r.email as string | undefined,
    }),
    role: (r.role as Role) || ("viewer" as Role),
    isActive: typeof r.isActive === "boolean" ? r.isActive : true,
    createdAt: typeof r.createdAt === "string" ? r.createdAt : undefined,
    updatedAt: typeof r.updatedAt === "string" ? r.updatedAt : undefined,
  };
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const form = new URLSearchParams();
          form.append("username", email);
          form.append("password", password);

          const { data } = await api.post<LoginResponse>("/auth/login", form, {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
          });

          const access =
            data.accessToken ||
            (data as unknown as { access_token: string }).access_token ||
            "";
          const refresh =
            data.refreshToken ||
            (data as unknown as { refresh_token: string }).refresh_token ||
            "";

          storeTokens(access, refresh);

          set({
            accessToken: access,
            refreshToken: refresh,
            isAuthenticated: !!(access && refresh),
            isLoading: false,
          });

          // Fetch /me to populate user info (login endpoint doesn't return it)
          try {
            await get().fetchMe();
          } catch {
            // Ignore: user might not be in DB yet, we still have tokens.
          }
        } catch (err: unknown) {
          const error = err as {
            response?: { data?: { detail?: string; message?: string } };
          };
          const detail =
            error.response?.data?.detail ||
            (error.response?.data as unknown as { message?: string })?.message ||
            "Login failed. Please check your credentials.";
          set({
            error: detail,
            isLoading: false,
          });
          throw err;
        }
      },

      register: async (input: RegisterRequest) => {
        set({ isLoading: true, error: null });
        try {
          // Backend UserCreate accepts alias `name` -> `full_name`.
          const payload = { email: input.email, password: input.password, name: input.name };
          const { data } = await api.post<RegisterResponse>("/auth/register", payload);

          // RegisterResponse only has user + access_token (no refresh_token).
          // To get a refresh token we immediately login with the same credentials.
          const accessFromRegister =
            data.accessToken ||
            (data as unknown as { access_token: string }).access_token ||
            "";

          if (data.user) {
            set({ user: normalizeUser(data.user as unknown as CurrentUser) });
          }

          try {
            const form = new URLSearchParams();
            form.append("username", input.email);
            form.append("password", input.password);
            const { data: loginData } = await api.post<LoginResponse>(
              "/auth/login",
              form,
              { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
            );

            const access =
              loginData.accessToken ||
              (loginData as unknown as { access_token: string }).access_token ||
              accessFromRegister;
            const refresh =
              loginData.refreshToken ||
              (loginData as unknown as { refresh_token: string }).refresh_token ||
              "";

            storeTokens(access, refresh);
            set({
              accessToken: access,
              refreshToken: refresh,
              isAuthenticated: !!access,
            });
          } catch (loginErr) {
            // Fall back to register's access token if login fails (rare).
            if (accessFromRegister) {
              storeTokens(accessFromRegister, "");
              set({
                accessToken: accessFromRegister,
                refreshToken: "",
                isAuthenticated: true,
              });
            } else {
              throw loginErr;
            }
          }

          try {
            await get().fetchMe();
          } catch {
            // ignore
          }

          set({ isLoading: false });
        } catch (err: unknown) {
          const error = err as {
            response?: { data?: { detail?: string; message?: string; email?: string[] } };
          };
          const detail =
            error.response?.data?.detail ||
            (error.response?.data as unknown as { message?: string })?.message ||
            (Array.isArray((error.response?.data as unknown as { email?: string[] })?.email)
              ? (error.response?.data as unknown as { email: string[] }).email.join(", ")
              : null) ||
            "Registration failed. Please try again.";
          set({
            error: detail,
            isLoading: false,
          });
          throw err;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          const refresh = get().refreshToken;
          if (refresh) {
            await api.post("/auth/logout", { refreshToken: refresh });
          }
        } catch {
          // ignore on client — backend might be down, still clear locally.
        } finally {
          clearAuthStorage();
          get().reset();
          set({ isLoading: false });
        }
      },

      fetchMe: async () => {
        set({ isLoading: true });
        try {
          const { data } = await api.get<CurrentUser>("/auth/me");
          const user = normalizeUser(data as unknown as CurrentUser);
          set({ user, isAuthenticated: true, isLoading: false });
          if (typeof window !== "undefined") {
            localStorage.setItem("user", JSON.stringify(user));
          }
        } catch {
          clearAuthStorage();
          get().reset();
          set({ isLoading: false });
        }
      },

      setTokens: (access: string, refresh: string) => {
        storeTokens(access, refresh);
        set({ accessToken: access, refreshToken: refresh });
      },

      setUser: (user: CurrentUser) => {
        set({ user });
        if (typeof window !== "undefined") {
          localStorage.setItem("user", JSON.stringify(user));
        }
      },

      clearError: () => set({ error: null }),

      reset: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        }),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
