"use client";

import * as React from "react";
import { Bell, LogOut, Menu, Settings as SettingsIcon, User as UserIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/ui/avatar";
import { GlassCard } from "@/components/ui/glass-card";
import { useAuthStore } from "@/store/auth-store";
import { useUIStore } from "@/store/ui-store";
import type { CurrentUser } from "@/lib/types";
import { cn } from "@/lib/utils";

export function Topbar({
  title,
  subtitle,
  breadcrumb,
  user,
  actions,
}: {
  title: string;
  subtitle?: string;
  breadcrumb?: { label: string; href?: string }[];
  user: CurrentUser;
  actions?: React.ReactNode;
}) {
  const router = useRouter();
  const logout = useAuthStore((s) => s.logout);
  const setMobile = useUIStore((s) => s.setMobileMenuOpen);
  const [menuOpen, setMenuOpen] = React.useState(false);
  const menuRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  async function handleLogout() {
    await logout();
    toast.success("Signed out");
    router.replace("/login");
  }

  const tone =
    user.role === "admin"
      ? "iris"
      : user.role === "manager"
      ? "aqua"
      : user.role === "agent"
      ? "default"
      : "outline";

  return (
    <header className="glass glass-highlight sticky top-4 z-10 mb-6 flex items-center justify-between gap-3 rounded-glass px-4 py-3 shadow-glass md:px-6 md:py-4">
      <div className="flex items-center gap-3 min-w-0">
        <button
          type="button"
          className="md:hidden rounded-xl glass p-2"
          onClick={() => setMobile(true)}
          aria-label="Open menu"
        >
          <Menu className="h-4 w-4" />
        </button>
        <div className="min-w-0">
          {breadcrumb && breadcrumb.length > 0 && (
            <div className="mb-1 flex items-center gap-1 text-[11px] font-mono text-secondary">
              {breadcrumb.map((b, i) => (
                <React.Fragment key={b.label}>
                  {i > 0 && <span>/</span>}
                  <span>{b.label}</span>
                </React.Fragment>
              ))}
            </div>
          )}
          <h1 className="truncate font-display text-lg font-semibold tracking-tight">{title}</h1>
          {subtitle && <p className="truncate text-sm text-secondary">{subtitle}</p>}
        </div>
      </div>

      <div className="flex items-center gap-2 md:gap-4">
        {actions}
        <ThemeToggle />
        <button className="relative rounded-xl glass p-2 text-secondary hover:text-[var(--text-primary)]" aria-label="Notifications">
          <Bell className="h-4 w-4" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-rose-500 ring-2 ring-[var(--page-bg-a)]" />
        </button>

        <div className="relative" ref={menuRef}>
          <button
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
            className="hidden items-center gap-2.5 sm:flex"
          >
            <Avatar name={user.name} size="sm" />
            <div className="hidden text-left leading-tight lg:block">
              <p className="text-sm font-medium">{user.name}</p>
              <Badge tone={tone as Parameters<typeof Badge>[0]["tone"]} className="mt-0.5 capitalize">
                {user.role}
              </Badge>
            </div>
          </button>
          <button
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
            className="sm:hidden"
            aria-label="Profile"
          >
            <Avatar name={user.name} size="sm" />
          </button>

          {menuOpen && (
            <GlassCard
              strong
              className={cn(
                "absolute right-0 top-full z-20 mt-2 w-56 overflow-hidden p-1.5 shadow-glass-lg",
                "sm:w-64"
              )}
            >
              <div className="flex items-center gap-3 border-b border-white/10 px-3 py-3">
                <Avatar name={user.name} size="md" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium">{user.name}</p>
                  <p className="truncate text-xs text-secondary">{user.email}</p>
                </div>
              </div>
              <div className="py-1">
                <button
                  onClick={() => {
                    setMenuOpen(false);
                    router.push("/settings");
                  }}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-white/10"
                >
                  <UserIcon className="h-4 w-4" />
                  Profile
                </button>
                <button
                  onClick={() => {
                    setMenuOpen(false);
                    router.push("/settings");
                  }}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-white/10"
                >
                  <SettingsIcon className="h-4 w-4" />
                  Settings
                </button>
              </div>
              <div className="border-t border-white/10 py-1">
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-rose-400 hover:bg-white/10"
                >
                  <LogOut className="h-4 w-4" />
                  Sign out
                </button>
              </div>
            </GlassCard>
          )}
        </div>
      </div>
    </header>
  );
}
