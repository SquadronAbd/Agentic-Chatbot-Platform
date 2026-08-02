"use client";

import { create } from "zustand";
import { persist, type StorageValue } from "zustand/middleware";

// Safe localStorage wrapper — swallows QuotaExceededError instead of crashing.
// On quota exceeded, evicts non-critical keys to make room and retries once.
const _KEEP_KEYS = new Set(["auth-storage", "access_token", "refresh_token", "user"]);
const safeStorage = {
  getItem: (name: string): StorageValue<unknown> | null => {
    try {
      const raw = localStorage.getItem(name);
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  },
  setItem: (name: string, value: StorageValue<unknown>): void => {
    const serialized = JSON.stringify(value);
    try {
      localStorage.setItem(name, serialized);
    } catch (e) {
      if (e instanceof DOMException && (e.name === "QuotaExceededError" || e.code === 22)) {
        try {
          // Evict stale non-auth keys to free space, then retry.
          Object.keys(localStorage)
            .filter((k) => !_KEEP_KEYS.has(k) && k !== name)
            .forEach((k) => localStorage.removeItem(k));
          localStorage.setItem(name, serialized);
        } catch { /* give up silently — theme won't persist this session */ }
      }
    }
  },
  removeItem: (name: string): void => {
    try { localStorage.removeItem(name); } catch { /* ignore */ }
  },
};

type Theme = "light" | "dark";

interface UIState {
  theme: Theme;
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  mobileMenuOpen: boolean;
  notifications: Array<{ id: string; title: string; description?: string; type: "info" | "success" | "warning" | "error" }>;
  activeConversationId: string | null;

  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setMobileMenuOpen: (open: boolean) => void;
  addNotification: (n: Omit<UIState["notifications"][number], "id">) => void;
  removeNotification: (id: string) => void;
  setActiveConversationId: (id: string | null) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      theme: "dark",
      sidebarOpen: true,
      sidebarCollapsed: false,
      mobileMenuOpen: false,
      notifications: [],
      activeConversationId: null,

      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set({ theme: get().theme === "light" ? "dark" : "light" }),
      toggleSidebar: () => set({ sidebarOpen: !get().sidebarOpen }),
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      setMobileMenuOpen: (open) => set({ mobileMenuOpen: open }),
      addNotification: (n) => {
        const id = `notif_${Date.now()}`;
        set({ notifications: [...get().notifications, { ...n, id }] });
        window.setTimeout(() => {
          set({ notifications: get().notifications.filter((x) => x.id !== id) });
        }, 5000);
      },
      removeNotification: (id) => set({ notifications: get().notifications.filter((n) => n.id !== id) }),
      setActiveConversationId: (id) => set({ activeConversationId: id }),
    }),
    {
      name: "ui-storage",
      storage: safeStorage,
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        // activeConversationId is NOT persisted — it belongs to a session,
        // not a user. Persisting it caused stale conversation IDs to appear
        // after logout or after messages were sent with conversationId=null.
      }),
    }
  )
);
