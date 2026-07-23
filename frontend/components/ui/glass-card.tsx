import * as React from "react";
import { cn } from "@/lib/utils";

export function GlassCard({
  className,
  strong,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & { strong?: boolean }) {
  return (
    <div
      className={cn(
        "glass-highlight rounded-glass",
        strong ? "glass-strong" : "glass",
        className
      )}
      {...props}
    />
  );
}
