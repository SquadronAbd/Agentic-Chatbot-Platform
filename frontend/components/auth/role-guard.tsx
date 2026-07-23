"use client";

import { ShieldAlert } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { hasAccess, type Role } from "@/lib/types";

/**
 * Gates its children behind a minimum role. Mirrors the backend's RBAC
 * matrix (spec section 5.1) on the client for immediate UI feedback —
 * the API Gateway's own RBAC guards remain the actual source of truth.
 */
export function RoleGuard({
  userRole,
  minimumRole,
  children,
}: {
  userRole: Role;
  minimumRole: Role;
  children: React.ReactNode;
}) {
  if (!hasAccess(userRole, minimumRole)) {
    return (
      <GlassCard className="flex flex-col items-center gap-3 px-8 py-16 text-center">
        <div className="grid h-12 w-12 place-items-center rounded-full bg-rose-500/15">
          <ShieldAlert className="h-6 w-6 text-rose-400" />
        </div>
        <h2 className="font-display text-lg font-semibold">403 — Not authorized</h2>
        <p className="max-w-sm text-sm text-secondary">
          This area needs the <span className="font-mono">{minimumRole}</span> role or higher.
          Your current role is <span className="font-mono">{userRole}</span>. Ask an admin to
          adjust your access if you believe this is wrong.
        </p>
      </GlassCard>
    );
  }

  return <>{children}</>;
}
