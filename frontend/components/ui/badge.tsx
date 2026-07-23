import * as React from "react";
import { cn } from "@/lib/utils";

const tones = {
  neutral: "bg-white/40 dark:bg-white/10 text-[var(--text-primary)]",
  iris: "bg-iris/15 text-iris-dim dark:text-iris-light",
  aqua: "bg-aqua/15 text-aqua-dim dark:text-aqua-light",
  success: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-300",
  warning: "bg-amber-500/15 text-amber-600 dark:text-amber-300",
  danger: "bg-rose-500/15 text-rose-600 dark:text-rose-300",
} as const;

export function Badge({
  className,
  tone = "neutral",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { tone?: keyof typeof tones }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-mono font-medium tracking-wide",
        tones[tone],
        className
      )}
      {...props}
    />
  );
}
