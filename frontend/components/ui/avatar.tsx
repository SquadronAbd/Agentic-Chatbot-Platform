import * as React from "react";
import { cn } from "@/lib/utils";

type Size = "xs" | "sm" | "md" | "lg" | "xl";

const sizeClasses: Record<Size, string> = {
  xs: "h-6 w-6 text-[10px]",
  sm: "h-8 w-8 text-xs",
  md: "h-10 w-10 text-sm",
  lg: "h-12 w-12 text-base",
  xl: "h-16 w-16 text-lg",
};

export function Avatar({
  name,
  size = "md",
  className,
  src,
}: {
  name?: string;
  size?: Size;
  className?: string;
  src?: string;
}) {
  const initials = React.useMemo(() => {
    if (!name) return "?";
    return name
      .split(" ")
      .map((p) => p[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
  }, [name]);

  if (src) {
    return (
      <img
        src={src}
        alt={name ?? "Avatar"}
        className={cn("rounded-full object-cover", sizeClasses[size], className)}
      />
    );
  }

  return (
    <div
      className={cn(
        "grid place-items-center rounded-full bg-gradient-to-br from-iris to-aqua font-display font-semibold text-white shadow-glow-iris",
        sizeClasses[size],
        className
      )}
    >
      {initials}
    </div>
  );
}
