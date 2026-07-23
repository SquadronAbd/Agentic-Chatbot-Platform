"use client";

import * as React from "react";
import { Bot } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";

/**
 * Consumes an SSE-style stream and appends tokens in real time. In this
 * standalone frontend (no live /chat/stream backend yet) it simulates the
 * stream by revealing `fullText` word-by-word, so the component's contract
 * matches what `useChat` from the Vercel AI SDK would drive in production.
 */
export function StreamingMessage({ fullText, tokens }: { fullText: string; tokens?: number }) {
  const words = React.useMemo(() => fullText.split(" "), [fullText]);
  const [visibleCount, setVisibleCount] = React.useState(0);

  React.useEffect(() => {
    setVisibleCount(0);
    const interval = setInterval(() => {
      setVisibleCount((count) => {
        if (count >= words.length) {
          clearInterval(interval);
          return count;
        }
        return count + 1;
      });
    }, 28);
    return () => clearInterval(interval);
  }, [words]);

  const isDone = visibleCount >= words.length;

  return (
    <div className="flex items-start gap-3">
      <div className="mt-1 grid h-7 w-7 flex-shrink-0 place-items-center rounded-full bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
        <Bot className="h-3.5 w-3.5 text-white" />
      </div>
      <GlassCard className="max-w-[75%] px-4 py-3">
        <p className="whitespace-pre-wrap text-sm leading-relaxed font-body">
          {words.slice(0, visibleCount).join(" ")}
          {!isDone && <span className="ml-0.5 inline-block h-3.5 w-1.5 animate-pulse bg-iris-light align-middle" />}
        </p>
        {isDone && tokens && (
          <p className="mt-2 font-mono text-[11px] text-secondary">{tokens} tokens</p>
        )}
      </GlassCard>
    </div>
  );
}
