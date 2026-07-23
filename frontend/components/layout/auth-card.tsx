import { Sparkles } from "lucide-react";
import { AuroraField } from "@/components/layout/aurora-field";
import { GlassCard } from "@/components/ui/glass-card";
import { ThemeToggle } from "@/components/theme/theme-toggle";

export function AuthCard({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <div className="relative flex min-h-screen items-center justify-center px-4">
      <AuroraField />

      <div className="absolute right-6 top-6">
        <ThemeToggle />
      </div>

      <GlassCard strong className="w-full max-w-sm px-8 py-9">
        <div className="mb-6 flex flex-col items-center gap-3 text-center">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="font-display text-lg font-semibold tracking-tight">{title}</h1>
            <p className="mt-1 text-sm text-secondary">{subtitle}</p>
          </div>
        </div>

        {children}

        <div className="mt-6 text-center text-sm text-secondary">{footer}</div>
      </GlassCard>
    </div>
  );
}
