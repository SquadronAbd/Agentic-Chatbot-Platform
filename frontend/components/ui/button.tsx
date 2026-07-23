import * as React from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "glass" | "ghost" | "danger";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-gradient-to-r from-iris to-aqua text-white shadow-glow-iris hover:brightness-110",
  glass: "glass hover:shadow-glass-lg text-[var(--text-primary)]",
  ghost: "bg-transparent hover:bg-white/10 text-[var(--text-primary)]",
  danger: "bg-rose-500/90 text-white hover:bg-rose-500 shadow-glow-iris",
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium font-display transition-all duration-300 disabled:opacity-40 disabled:pointer-events-none",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}
