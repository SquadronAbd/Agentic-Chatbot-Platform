import * as React from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-xl bg-white/10 dark:bg-white/5",
        className
      )}
      {...props}
    />
  );
}

export function CardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("glass glass-highlight rounded-glass p-6 shadow-glass", className)}>
      <Skeleton className="mb-4 h-5 w-1/3" />
      <div className="space-y-3">
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-2/3" />
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="glass glass-highlight overflow-hidden rounded-glass shadow-glass">
      <div className="grid gap-4 border-b border-white/10 p-4" style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}>
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} className="h-4 w-3/4" />
        ))}
      </div>
      <div className="divide-y divide-white/10">
        {Array.from({ length: rows }).map((_, ri) => (
          <div
            key={ri}
            className="grid gap-4 p-4"
            style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
          >
            {Array.from({ length: cols }).map((_, ci) => (
              <Skeleton key={ci} className="h-4 w-5/6" />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export function ChatSkeleton({ messages = 3 }: { messages?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: messages }).map((_, i) => (
        <div key={i} className={cn("flex gap-3", i % 2 === 0 ? "" : "justify-end")}>
          <Skeleton className={cn("h-8 w-8 flex-shrink-0 rounded-full", i % 2 === 0 ? "" : "order-last")} />
          <div className="space-y-2">
            <Skeleton className="h-4 w-[480px] max-w-[75vw]" />
            <Skeleton className="h-4 w-[380px] max-w-[60vw]" />
            <Skeleton className="h-4 w-[300px] max-w-[50vw]" />
          </div>
        </div>
      ))}
    </div>
  );
}
