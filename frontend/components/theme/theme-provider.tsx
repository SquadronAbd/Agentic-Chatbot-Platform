"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider, useTheme } from "next-themes";
import { useUIStore } from "@/store/ui-store";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const initialTheme = useUIStore((s) => s.theme);
  return (
    <NextThemesProvider
      attribute="data-theme"
      defaultTheme={initialTheme ?? "dark"}
      enableSystem={false}
      themes={["light", "dark"]}
      disableTransitionOnChange={false}
      storageKey="ui-storage"
    >
      <ThemeSyncWatcher>{children}</ThemeSyncWatcher>
    </NextThemesProvider>
  );
}

function ThemeSyncWatcher({ children }: { children: React.ReactNode }) {
  const { theme, resolvedTheme } = useTheme();
  const setUITheme = useUIStore((s) => s.setTheme);

  React.useEffect(() => {
    const effective = (resolvedTheme ?? theme) as "light" | "dark" | undefined;
    if (effective) setUITheme(effective);
  }, [theme, resolvedTheme, setUITheme]);

  return <>{children}</>;
}
