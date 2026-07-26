"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/store/ui-store";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const uiTheme = useUIStore((s) => s.theme);
  const setUITheme = useUIStore((s) => s.setTheme);
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => setMounted(true), []);

  const effective = mounted ? (theme ?? uiTheme) : uiTheme;
  const isDark = effective === "dark";

  function toggle() {
    const next = isDark ? "light" : "dark";
    setTheme(next);
    setUITheme(next);
  }

  return (
    <button
      type="button"
      role="switch"
      aria-checked={isDark}
      aria-label="Toggle day / night glass theme"
      onClick={toggle}
      className={cn(
        "glass glass-highlight relative flex h-9 w-16 items-center rounded-full px-1 transition-colors duration-500",
        "shadow-glass hover:shadow-glass-lg"
      )}
    >
      <span
        className={cn(
          "absolute inset-y-1 left-1 flex h-7 w-7 items-center justify-center rounded-full transition-all duration-500 ease-[cubic-bezier(0.65,0,0.35,1)]",
          isDark
            ? "translate-x-[28px] bg-nebula shadow-glow-iris"
            : "translate-x-0 bg-white shadow-glow-aqua"
        )}
      >
        {isDark ? (
          <Moon className="h-4 w-4 text-iris-light" strokeWidth={2} />
        ) : (
          <Sun className="h-4 w-4 text-aqua-dim" strokeWidth={2} />
        )}
      </span>
    </button>
  );
}
