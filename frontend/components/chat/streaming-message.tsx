"use client";

import * as React from "react";
import { Bot, Check, Copy, RefreshCw, Square } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { GlassCard } from "@/components/ui/glass-card";
import { MarkdownViewer } from "@/components/ui/markdown-viewer";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";

export function StreamingMessage({
  content,
  isStreaming,
  tokens,
  timestamp,
  onCopy,
  onRegenerate,
  onStop,
}: {
  content: string;
  isStreaming?: boolean;
  tokens?: number;
  timestamp?: string;
  onCopy?: () => void;
  onRegenerate?: () => void;
  onStop?: () => void;
}) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    void navigator.clipboard.writeText(content);
    setCopied(true);
    onCopy?.();
    window.setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
      className="group flex items-start gap-3"
    >
      <div className="mt-1 grid h-8 w-8 flex-shrink-0 place-items-center rounded-full bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
        {isStreaming ? (
          <Spinner size="sm" className="text-white" />
        ) : (
          <Bot className="h-3.5 w-3.5 text-white" />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <GlassCard className={cn("max-w-[80%] px-4 py-3", !content && isStreaming && "min-h-[60px]")}>
          {content ? (
            <MarkdownViewer content={content} animate={false} />
          ) : (
            <div className="flex items-center gap-2 text-secondary">
              <span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-iris" />
              <span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-iris [animation-delay:120ms]" />
              <span className="inline-flex h-2 w-2 animate-pulse rounded-full bg-iris [animation-delay:240ms]" />
            </div>
          )}
          {isStreaming && content && (
            <span className="ml-1 inline-block h-4 w-1 animate-pulse bg-iris-light align-middle" />
          )}
        </GlassCard>

        <div className="mt-2 flex items-center gap-1 pl-1 opacity-0 transition-opacity group-hover:opacity-100">
          <AnimatePresence>
            {isStreaming ? (
              <motion.button
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                onClick={onStop}
                className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-secondary hover:bg-white/10 hover:text-[var(--text-primary)]"
              >
                <Square className="h-3 w-3 fill-current" />
                Stop
              </motion.button>
            ) : (
              content && (
                <>
                  <motion.button
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    onClick={handleCopy}
                    className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-secondary hover:bg-white/10 hover:text-[var(--text-primary)]"
                  >
                    {copied ? (
                      <>
                        <Check className="h-3 w-3 text-emerald-400" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3" />
                        Copy
                      </>
                    )}
                  </motion.button>
                  {onRegenerate && (
                    <motion.button
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      onClick={onRegenerate}
                      className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-secondary hover:bg-white/10 hover:text-[var(--text-primary)]"
                    >
                      <RefreshCw className="h-3 w-3" />
                      Regenerate
                    </motion.button>
                  )}
                </>
              )
            )}
          </AnimatePresence>
          {timestamp && <span className="ml-auto font-mono text-[11px] text-secondary">{timestamp}</span>}
          {!isStreaming && tokens != null && tokens > 0 && (
            <span className="font-mono text-[11px] text-secondary">{tokens} tokens</span>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function UserMessage({
  content,
  timestamp,
  name,
}: {
  content: string;
  timestamp?: string;
  name: string;
}) {
  const [copied, setCopied] = React.useState(false);
  const initials = React.useMemo(() => {
    return name
      .split(" ")
      .map((p) => p[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
  }, [name]);

  const copy = () => {
    void navigator.clipboard.writeText(content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
      className="group flex items-start justify-end gap-3"
    >
      <div className="min-w-0 max-w-[80%]">
        <GlassCard strong className="bg-gradient-to-br from-iris/25 to-aqua/10 px-4 py-3">
          <MarkdownViewer content={content} animate={false} />
        </GlassCard>
        <div className="mt-2 flex items-center justify-end gap-2 pr-1 opacity-0 transition-opacity group-hover:opacity-100">
          {timestamp && <span className="font-mono text-[11px] text-secondary">{timestamp}</span>}
          <button
            onClick={copy}
            className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs text-secondary hover:bg-white/10 hover:text-[var(--text-primary)]"
          >
            {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
          </button>
        </div>
      </div>
      <div className="mt-1 grid h-8 w-8 flex-shrink-0 place-items-center rounded-full bg-white/30">
        <span className="font-display text-[10px] font-bold">{initials}</span>
      </div>
    </motion.div>
  );
}
