"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

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
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        activeConversationId: state.activeConversationId,
      }),
    }
  )
);
