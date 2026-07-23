"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  FolderKanban,
  MessageSquare,
  Settings,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { hasAccess, type Role } from "@/lib/types";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  minimumRole: Role;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Chat", icon: MessageSquare, minimumRole: "viewer" },
  { href: "/conversations", label: "Conversations", icon: FolderKanban, minimumRole: "viewer" },
  { href: "/documents", label: "Knowledge base", icon: Sparkles, minimumRole: "agent" },
  { href: "/analytics", label: "Analytics", icon: BarChart3, minimumRole: "manager" },
  { href: "/admin", label: "Admin", icon: ShieldCheck, minimumRole: "admin" },
];

export function Sidebar({ role }: { role: Role }) {
  const pathname = usePathname();

  return (
    <aside className="glass glass-highlight fixed left-4 top-4 bottom-4 z-20 flex w-[76px] flex-col items-center rounded-glass py-6 shadow-glass md:w-[220px] md:items-stretch md:px-4">
      <div className="mb-8 flex items-center gap-2 px-2">
        <div className="grid h-9 w-9 flex-shrink-0 place-items-center rounded-xl bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
          <Sparkles className="h-4.5 w-4.5 text-white" />
        </div>
        <span className="hidden font-display text-sm font-semibold tracking-tight md:inline">
          Aether<span className="text-iris">Chat</span>
        </span>
      </div>

      <nav className="flex flex-1 flex-col gap-1.5">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          const allowed = hasAccess(role, item.minimumRole);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={allowed ? item.href : "#"}
              aria-disabled={!allowed}
              className={cn(
                "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-body transition-all",
                active
                  ? "bg-gradient-to-r from-iris/20 to-aqua/10 text-[var(--text-primary)] shadow-glow-iris"
                  : "text-secondary hover:bg-white/10 hover:text-[var(--text-primary)]",
                !allowed && "cursor-not-allowed opacity-35 hover:bg-transparent"
              )}
            >
              {active && (
                <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-gradient-to-b from-iris to-aqua" />
              )}
              <Icon className="h-4.5 w-4.5 flex-shrink-0" />
              <span className="hidden md:inline">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <Link
        href="/settings"
        className={cn(
          "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-body text-secondary transition-colors hover:bg-white/10 hover:text-[var(--text-primary)]",
          pathname === "/settings" && "text-[var(--text-primary)]"
        )}
      >
        <Settings className="h-4.5 w-4.5 flex-shrink-0" />
        <span className="hidden md:inline">Settings</span>
      </Link>
    </aside>
  );
}
