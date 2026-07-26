import * as React from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "glass" | "ghost" | "danger";
type Size = "sm" | "md" | "lg" | "icon";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-gradient-to-r from-iris to-aqua text-white shadow-glow-iris hover:brightness-110",
  glass: "glass hover:shadow-glass-lg text-[var(--text-primary)]",
  ghost: "bg-transparent hover:bg-white/10 text-[var(--text-primary)]",
  danger: "bg-rose-500/90 text-white hover:bg-rose-500 shadow-glow-iris",
};

const sizeClasses: Record<Size, string> = {
  sm: "h-8 px-3 text-xs rounded-lg",
  md: "h-10 px-4 text-sm rounded-xl",
  lg: "h-12 px-6 text-base rounded-xl",
  icon: "h-10 w-10 p-0 rounded-xl",
};

export function Button({ className, variant = "primary", size = "md", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 font-display font-medium transition-all duration-300 disabled:opacity-40 disabled:pointer-events-none",
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    />
  );
}
