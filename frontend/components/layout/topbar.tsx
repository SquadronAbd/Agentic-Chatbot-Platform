import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Badge } from "@/components/ui/badge";
import type { CurrentUser } from "@/lib/types";

export function Topbar({ title, subtitle, user }: { title: string; subtitle?: string; user: CurrentUser }) {
  return (
    <header className="glass glass-highlight sticky top-4 z-10 mb-6 flex items-center justify-between rounded-glass px-6 py-4 shadow-glass">
      <div>
        <h1 className="font-display text-lg font-semibold tracking-tight">{title}</h1>
        {subtitle && <p className="text-sm text-secondary">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        <ThemeToggle />
        <div className="hidden items-center gap-2.5 sm:flex">
          <div className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-iris to-aqua font-display text-xs font-semibold text-white">
            {user.name
              .split(" ")
              .map((p) => p[0])
              .join("")}
          </div>
          <div className="leading-tight">
            <p className="text-sm font-medium">{user.name}</p>
            <Badge tone="iris" className="mt-0.5">
              {user.role}
            </Badge>
          </div>
        </div>
      </div>
    </header>
  );
}
