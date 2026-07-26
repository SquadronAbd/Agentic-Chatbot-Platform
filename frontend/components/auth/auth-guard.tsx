"use client";

import * as React from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";
import { hasAccess, type Role, type CurrentUser } from "@/lib/types";
import { Spinner } from "@/components/ui/spinner";
import { GlassCard } from "@/components/ui/glass-card";

const PUBLIC_PATHS = ["/login", "/register", "/403", "/404"];

export function AuthGuard({
  children,
  minimumRole,
}: {
  children: (user: CurrentUser) => React.ReactNode;
  minimumRole?: Role;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const accessToken = useAuthStore((s) => s.accessToken);
  const fetchMe = useAuthStore((s) => s.fetchMe);
  const checkedRef = React.useRef(false);

  React.useEffect(() => {
    if (checkedRef.current) return;
    const path = pathname ?? "";
    const isPublic = PUBLIC_PATHS.some((p) => path.startsWith(p));

    if (isPublic) {
      checkedRef.current = true;
      return;
    }

    if (!isAuthenticated && !accessToken) {
      router.replace("/login");
      return;
    }

    if (isAuthenticated && user) {
      checkedRef.current = true;
      return;
    }

    if (accessToken && !user) {
      void fetchMe().finally(() => {
        checkedRef.current = true;
      });
    } else {
      checkedRef.current = true;
    }
  }, [pathname, isAuthenticated, user, accessToken, fetchMe, router]);

  const path = pathname ?? "";
  const isPublic = PUBLIC_PATHS.some((p) => path.startsWith(p));

  if (isPublic) {
    return <>{typeof children === "function" ? null : children}</>;
  }

  if (isLoading || (!isAuthenticated && accessToken && !user)) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <GlassCard className="flex flex-col items-center gap-4 px-12 py-10">
          <Spinner size="lg" />
          <p className="font-body text-sm text-secondary">Loading workspace…</p>
        </GlassCard>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  if (minimumRole && !hasAccess(user.role, minimumRole)) {
    router.replace("/403");
    return null;
  }

  return <>{children(user)}</>;
}
