import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Badge } from "@/components/ui/badge";
import type { CurrentUser } from "@/lib/types";

export function Topbar({ title, subtitle, user }: { title: string; subtitle?: string; user: CurrentUser }) {
  return (
    <header className="glass glass-highlight z-10 mb-4 flex flex-shrink-0 items-center justify-between rounded-glass px-6 py-4 shadow-glass" style={{position: "relative"}}>
      <div>
        <h1 className="font-display text-lg font-semibold tracking-tight">{title}</h1>
        {subtitle && <p className="text-sm text-secondary">{subtitle}</p>}
      </div>

      <ThemeToggle />
    </header>
  );
}
