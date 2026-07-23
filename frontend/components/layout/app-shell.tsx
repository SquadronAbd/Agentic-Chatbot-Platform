import { Sidebar } from "@/components/layout/sidebar";
import { AuroraField } from "@/components/layout/aurora-field";
import type { CurrentUser } from "@/lib/types";

export function AppShell({ user, children }: { user: CurrentUser; children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen">
      <AuroraField />
      <Sidebar role={user.role} />
      <main className="min-h-screen pl-[100px] pr-4 pt-4 md:pl-[248px] md:pr-6">
        <div className="mx-auto max-w-6xl pb-10">{children}</div>
      </main>
    </div>
  );
}
