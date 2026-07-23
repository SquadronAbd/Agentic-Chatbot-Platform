"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import type { ManagedUser, Role } from "@/lib/types";

const ROLES: Role[] = ["viewer", "agent", "manager", "admin"];
const PAGE_SIZE = 4;

const ROLE_TONE: Record<Role, "neutral" | "iris" | "aqua"> = {
  viewer: "neutral",
  agent: "aqua",
  manager: "iris",
  admin: "iris",
};

export function UserTable({ users }: { users: ManagedUser[] }) {
  const [page, setPage] = React.useState(0);
  const [roleOverrides, setRoleOverrides] = React.useState<Record<string, Role>>({});

  const totalPages = Math.max(1, Math.ceil(users.length / PAGE_SIZE));
  const visible = users.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  function changeRole(userId: string, role: Role) {
    setRoleOverrides((prev) => ({ ...prev, [userId]: role }));
  }

  return (
    <GlassCard className="overflow-hidden">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-[var(--glass-border)] text-secondary">
            <th className="px-5 py-3 font-display font-medium">User</th>
            <th className="px-5 py-3 font-display font-medium">Role</th>
            <th className="px-5 py-3 font-display font-medium">Last active</th>
          </tr>
        </thead>
        <tbody>
          {visible.map((user) => {
            const role = roleOverrides[user.id] ?? user.role;
            return (
              <tr key={user.id} className="border-b border-[var(--glass-border)] last:border-0 hover:bg-white/5">
                <td className="px-5 py-3.5">
                  <p className="font-body font-medium">{user.name}</p>
                  <p className="text-xs text-secondary">{user.email}</p>
                </td>
                <td className="px-5 py-3.5">
                  <div className="relative inline-block">
                    <select
                      value={role}
                      onChange={(e) => changeRole(user.id, e.target.value as Role)}
                      className="glass cursor-pointer appearance-none rounded-lg py-1.5 pl-3 pr-8 font-mono text-xs outline-none"
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                  </div>
                  <Badge tone={ROLE_TONE[role]} className="ml-2 align-middle">
                    live
                  </Badge>
                </td>
                <td className="px-5 py-3.5 font-mono text-xs text-secondary">{user.lastActive}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      <div className="flex items-center justify-between border-t border-[var(--glass-border)] px-5 py-3">
        <p className="text-xs text-secondary">
          Page {page + 1} of {totalPages}
        </p>
        <div className="flex gap-1.5">
          <button
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            className="rounded-lg p-1.5 text-secondary transition-colors hover:bg-white/10 disabled:opacity-30"
            aria-label="Previous page"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            disabled={page >= totalPages - 1}
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            className="rounded-lg p-1.5 text-secondary transition-colors hover:bg-white/10 disabled:opacity-30"
            aria-label="Next page"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </GlassCard>
  );
}
