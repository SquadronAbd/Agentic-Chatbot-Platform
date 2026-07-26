"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BarChart3,
  FolderKanban,
  MessageSquare,
  Settings,
  ShieldCheck,
  Sparkles,
  Plus,
  Trash2,
  Loader2,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { hasAccess, type CurrentUser, type Role } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/loading-skeleton";
import {
  useConversations,
  useCreateConversation,
  useDeleteConversation,
} from "@/hooks/use-api";
import { useUIStore } from "@/store/ui-store";

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

export function Sidebar({ role, user }: { role: Role; user: CurrentUser }) {
  const pathname = usePathname();
  const router = useRouter();
  const activeId = useUIStore((s) => s.activeConversationId);
  const setActive = useUIStore((s) => s.setActiveConversationId);

  const { data: conversations, isLoading } = useConversations();
  const createConv = useCreateConversation();
  const deleteConv = useDeleteConversation();

  async function handleNewChat() {
    setActive(null);
    try {
      if (pathname !== "/") router.push("/");
    } catch {
      // ignore
    }
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    try {
      await deleteConv.mutateAsync(id);
      if (activeId === id) setActive(null);
      toast.success("Conversation deleted");
    } catch {
      toast.error("Failed to delete");
    }
  }

  function handleCreate() {
    createConv.mutate(
      { title: "New chat" },
      {
        onSuccess: (c) => {
          setActive(c.id);
          if (pathname !== "/") router.push("/");
        },
      }
    );
  }

  const initials = user.name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <aside className="glass glass-highlight relative z-20 flex h-full w-[240px] flex-shrink-0 flex-col p-3 shadow-glass border-r border-white/5">
      <div className="mb-4 flex items-center justify-between px-2 pt-1">
        <div className="flex items-center gap-2">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
            <Sparkles className="h-4.5 w-4.5 text-white" />
          </div>
          <span className="font-display text-sm font-semibold tracking-tight">
            Aether<span className="text-iris">Chat</span>
          </span>
        </div>
      </div>

      <Button variant="primary" size="sm" className="mb-4 w-full justify-start gap-2" onClick={handleCreate}>
        <Plus className="h-4 w-4" />
        New conversation
      </Button>

      <nav className="mb-3 flex flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          const allowed = hasAccess(role, item.minimumRole);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={allowed ? item.href : "/403"}
              aria-disabled={!allowed}
              className={cn(
                "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all",
                active
                  ? "bg-gradient-to-r from-iris/25 to-aqua/15 text-[var(--text-primary)] shadow-glow-iris"
                  : "text-secondary hover:bg-white/10 hover:text-[var(--text-primary)]",
                !allowed && "cursor-not-allowed opacity-35 hover:bg-transparent"
              )}
            >
              {active && (
                <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-gradient-to-b from-iris to-aqua" />
              )}
              <Icon className="h-4.5 w-4.5 flex-shrink-0" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="mb-2 flex items-center justify-between px-2">
        <span className="text-[10px] font-mono uppercase tracking-widest text-secondary">
          Recent
        </span>
      </div>

      <div className="flex-1 overflow-y-auto pr-1 -mr-1">
        {isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-9 w-full rounded-xl" />
            ))}
          </div>
        ) : conversations && conversations.length > 0 ? (
          <div className="space-y-1">
            {conversations.slice(0, 14).map((c) => (
              <div
                key={c.id}
                className={cn(
                  "group relative flex items-center gap-2 rounded-xl px-2.5 py-2 text-sm transition-colors cursor-pointer",
                  activeId === c.id
                    ? "bg-white/10 text-[var(--text-primary)]"
                    : "text-secondary hover:bg-white/10 hover:text-[var(--text-primary)]"
                )}
                onClick={() => {
                  setActive(c.id);
                  if (pathname !== "/") router.push("/");
                }}
              >
                <MessageSquare className="h-3.5 w-3.5 flex-shrink-0 opacity-70" />
                <span className="flex-1 truncate text-xs">{c.title}</span>
                <button
                  onClick={(e) => handleDelete(c.id, e)}
                  className="ml-1 rounded-md p-1 opacity-0 transition-opacity hover:bg-white/10 group-hover:opacity-100"
                  aria-label="Delete conversation"
                >
                  {deleteConv.variables === c.id && deleteConv.isPending ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Trash2 className="h-3 w-3" />
                  )}
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="px-2 py-3 text-xs text-secondary">No conversations yet</div>
        )}
      </div>

      <div className="mt-3 border-t border-white/10 pt-3">
        <Link
          href="/settings"
          className={cn(
            "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-secondary transition-colors hover:bg-white/10 hover:text-[var(--text-primary)]",
            pathname === "/settings" && "bg-white/10 text-[var(--text-primary)]"
          )}
        >
          <Settings className="h-4.5 w-4.5 flex-shrink-0" />
          <div className="flex min-w-0 flex-1 items-center justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate text-xs font-medium">{user.name}</p>
              <p className="truncate text-[10px] text-secondary">{user.email}</p>
            </div>
            <div className="grid h-7 w-7 flex-shrink-0 place-items-center rounded-full bg-gradient-to-br from-iris to-aqua font-display text-[10px] font-bold text-white shadow-glow-iris">
              {initials}
            </div>
          </div>
        </Link>
      </div>
    </aside>
  );
}
