"use client";

import * as React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        refetchOnWindowFocus: false,
        retry: (failureCount, error: unknown) => {
          const err = error as { response?: { status?: number } };
          if (err.response?.status === 401 || err.response?.status === 403) return false;
          return failureCount < 2;
        },
      },
      mutations: {
        retry: false,
      },
    },
  });
}

let browserQueryClient: QueryClient | undefined;

function getQueryClient(): QueryClient {
  if (typeof window === "undefined") {
    return makeQueryClient();
  }
  if (!browserQueryClient) browserQueryClient = makeQueryClient();
  return browserQueryClient;
}

export function AppQueryProvider({ children }: { children: React.ReactNode }) {
  const client = React.useMemo(() => getQueryClient(), []);
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
