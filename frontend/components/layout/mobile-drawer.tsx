"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  BarChart3,
  FolderKanban,
  MessageSquare,
  Settings,
  ShieldCheck,
  Sparkles,
  X,
  LogOut,
} from "lucide-react";
import { toast } from "sonner";
import { cn, hasAccess, type CurrentUser, type Role } from "@/lib";
import { useUIStore } from "@/store/ui-store";
import { useAuthStore } from "@/store/auth-store";
import { Avatar } from "@/components/ui/avatar";

const NAV_ITEMS = [
  { href: "/", label: "Chat", icon: MessageSquare, minimumRole: "viewer" as Role },
  { href: "/conversations", label: "Conversations", icon: FolderKanban, minimumRole: "viewer" as Role },
  { href: "/documents", label: "Knowledge base", icon: Sparkles, minimumRole: "agent" as Role },
  { href: "/analytics", label: "Analytics", icon: BarChart3, minimumRole: "manager" as Role },
  { href: "/admin", label: "Admin", icon: ShieldCheck, minimumRole: "admin" as Role },
];

export function MobileDrawer({ role, user }: { role: Role; user: CurrentUser }) {
  const pathname = usePathname();
  const router = useRouter();
  const open = useUIStore((s) => s.mobileMenuOpen);
  const setOpen = useUIStore((s) => s.setMobileMenuOpen);
  const setActive = useUIStore((s) => s.setActiveConversationId);
  const logout = useAuthStore((s) => s.logout);

  async function handleLogout() {
    await logout();
    toast.success("Signed out");
    setOpen(false);
    router.replace("/login");
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(false)}
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm md:hidden"
          />
          <motion.aside
            initial={{ x: "-110%" }}
            animate={{ x: 0 }}
            exit={{ x: "-110%" }}
            transition={{ type: "spring", damping: 25, stiffness: 260 }}
            className="glass glass-highlight fixed left-0 top-0 bottom-0 z-50 flex w-[85%] max-w-[320px] flex-col rounded-r-glass p-4 shadow-glass-lg md:hidden"
          >
            <div className="mb-5 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <span className="font-display text-sm font-semibold tracking-tight">
                  Aether<span className="text-iris">Chat</span>
                </span>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="rounded-xl glass p-2"
                aria-label="Close menu"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <nav className="flex flex-1 flex-col gap-1">
              {NAV_ITEMS.map((item) => {
                const active = pathname === item.href;
                const allowed = hasAccess(role, item.minimumRole);
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={allowed ? item.href : "/403"}
                    onClick={() => {
                      if (item.href === "/") setActive(null);
                      setOpen(false);
                    }}
                    className={cn(
                      "flex items-center gap-3 rounded-xl px-3 py-3 text-sm",
                      active ? "bg-gradient-to-r from-iris/20 to-aqua/10" : "hover:bg-white/10",
                      !allowed && "opacity-35 cursor-not-allowed"
                    )}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
              <Link
                href="/settings"
                onClick={() => setOpen(false)}
                className={cn(
                  "mt-2 flex items-center gap-3 rounded-xl px-3 py-3 text-sm hover:bg-white/10",
                  pathname === "/settings" && "bg-white/10"
                )}
              >
                <Settings className="h-5 w-5 flex-shrink-0" />
                <span>Settings</span>
              </Link>
            </nav>

            <div className="border-t border-white/10 pt-4">
              <div className="mb-3 flex items-center gap-3 px-2">
                <Avatar name={user.name} size="md" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{user.name}</p>
                  <p className="truncate text-xs text-secondary">{user.email}</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm text-rose-400 hover:bg-white/10"
              >
                <LogOut className="h-5 w-5 flex-shrink-0" />
                <span>Sign out</span>
              </button>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
