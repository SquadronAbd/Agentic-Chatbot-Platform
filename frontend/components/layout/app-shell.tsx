"use client";

import * as React from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { AuroraField } from "@/components/layout/aurora-field";
import { AuthGuard } from "@/components/auth/auth-guard";
import { MobileDrawer } from "@/components/layout/mobile-drawer";
import type { CurrentUser, Role } from "@/lib/types";

export function AppShell({
  children,
  minimumRole,
}: {
  children: (user: CurrentUser) => React.ReactNode;
  minimumRole?: Role;
}) {
  return (
    <AuthGuard minimumRole={minimumRole}>
      {(user) => (
        <AppShellContent user={user}>
          {children(user)}
        </AppShellContent>
      )}
    </AuthGuard>
  );
}

function AppShellContent({
  user,
  children,
}: {
  user: CurrentUser;
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex h-screen w-full overflow-hidden">
      <AuroraField />

      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <Sidebar role={user.role} user={user} />
      </div>

      {/* Mobile Sidebar */}
      <MobileDrawer role={user.role} user={user} />

      {/* Main Content */}
      <main className="relative flex flex-1 flex-col overflow-hidden">
        {children}
      </main>
    </div>
  );
}