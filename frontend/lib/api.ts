import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { snakeToCamel, camelToSnake } from "@/lib/utils";

// Use relative base URL through Next.js rewrites proxy so browser hits same-origin (no CORS needed).
// Next.js forwards /api/v1/* to http://localhost:8000/api/v1/*.
export const BASE_URL = "/api/v1";
export const BACKEND_ABSOLUTE_BASE = "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false,
});

interface TokenRefreshResponse {
  access_token: string;
}

const STORAGE_KEYS = {
  ACCESS: "access_token",
  REFRESH: "refresh_token",
  USER: "user",
} as const;

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(STORAGE_KEYS.ACCESS);
}

function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(STORAGE_KEYS.REFRESH);
}

function setAccessToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEYS.ACCESS, token);
}

export function clearAuthStorage(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(STORAGE_KEYS.ACCESS);
  localStorage.removeItem(STORAGE_KEYS.REFRESH);
  localStorage.removeItem(STORAGE_KEYS.USER);
  // Clear zustand persist snapshots so a new user starts from a clean slate.
  localStorage.removeItem("auth-storage");
  localStorage.removeItem("ui-storage");
}

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null): void {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
}

async function performRefresh(): Promise<string> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error("No refresh token");
  }
  // Use snake_case body for backend (matches TokenRefreshRequest).
  const { data } = await axios.post<TokenRefreshResponse>(
    `${BASE_URL}/auth/refresh`,
    { refresh_token: refreshToken }
  );
  const newToken = snakeToCamel<{ accessToken: string }>(data).accessToken || data.access_token;
  setAccessToken(newToken);
  return newToken;
}

function redirectToLogin(): void {
  if (typeof window === "undefined") return;
  clearAuthStorage();
  if (!window.location.pathname.startsWith("/login") && !window.location.pathname.startsWith("/register")) {
    window.location.href = "/login";
  }
}

// Request interceptor: add auth bearer + convert camelCase JSON body to snake_case.
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Do NOT convert:
    //  - URLSearchParams bodies (OAuth2 login form)
    //  - FormData bodies (uploads)
    //  - GET/HEAD params-less bodies
    const { data } = config;
    if (
      data &&
      typeof data === "object" &&
      !(data instanceof URLSearchParams) &&
      !(typeof FormData !== "undefined" && data instanceof FormData) &&
      (config.method === "post" || config.method === "put" || config.method === "patch")
    ) {
      // Special case: don't convert auth register payload field "name" → it has alias="full_name" in backend,
      // but AdminUserCreate expects "full_name" (no alias), so for admin create user we do manual mapping.
      config.data = camelToSnake(data);
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: convert snake_case JSON responses into camelCase.
api.interceptors.response.use(
  (response) => {
    if (
      response.data != null &&
      (typeof response.data === "object" || Array.isArray(response.data))
    ) {
      response.data = snakeToCamel(response.data);
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status !== 401 || originalRequest._retry) {
      if (error.response?.status === 401 && originalRequest._retry) {
        redirectToLogin();
      }
      // Try to convert snake_case error body too, helps display messages
      if (error.response?.data && typeof error.response.data === "object") {
        error.response.data = snakeToCamel(error.response.data);
      }
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          return api(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    isRefreshing = true;

    try {
      const newToken = await performRefresh();
      processQueue(null, newToken);
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
      }
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      redirectToLogin();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

const AI_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "/agentic";

export interface ChatResponse {
  success: boolean;
  session_id: string;
  question: string;
  answer: string;
  documents_retrieved: number;
  sources: {
    source: string;
    content: string;
    metadata: Record<string, string>;
  }[];
  error: string | null;
}

export async function sendChat(
  sessionId: string,
  question: string
): Promise<ChatResponse> {
  const res = await fetch(`${AI_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      question,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json();
}

export async function ingestFile(
  file: File
): Promise<{ chunks_added: number }> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${AI_BASE}/ingest`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  return res.json();
}

export default api;