import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "glass w-full rounded-xl px-4 py-2.5 text-sm font-body text-[var(--text-primary)] placeholder:text-secondary outline-none transition-shadow focus:shadow-glow-iris",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
