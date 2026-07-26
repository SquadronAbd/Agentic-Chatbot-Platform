import * as React from "react";
import { cn } from "@/lib/utils";

type Size = "sm" | "md" | "lg" | "xl";

const sizeClasses: Record<Size, string> = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-8 w-8 border-[3px]",
  xl: "h-12 w-12 border-4",
};

export function Spinner({ size = "md", className }: { size?: Size; className?: string }) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn("animate-spin rounded-full border-transparent border-t-current text-iris", sizeClasses[size], className)}
    />
  );
}
