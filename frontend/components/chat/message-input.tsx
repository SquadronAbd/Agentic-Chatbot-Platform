"use client";

import * as React from "react";
import { SendHorizontal, Square, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";

const SUGGESTIONS = [
  "Summarize the latest uploaded documents",
  "What are the key themes in the support tickets?",
  "Draft a follow-up email for the Q3 review",
  "Explain the pricing model changes",
];

export function MessageInput({
  onSend,
  onStop,
  isStreaming,
}: {
  onSend: (text: string) => void;
  onStop?: () => void;
  isStreaming?: boolean;
}) {
  const [value, setValue] = React.useState("");
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  React.useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`;
  }, [value]);

  function submit(e?: React.FormEvent) {
    e?.preventDefault();
    const text = value.trim();
    if (!text || isStreaming) return;
    onSend(text);
    setValue("");
  }

  return (
    <div className="space-y-3">
      <motion.div
        initial={false}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: "spring", stiffness: 280, damping: 24 }}
      >
        <form onSubmit={submit}>
          <GlassCard className="flex items-end gap-3 p-3 shadow-glass-lg focus-within:shadow-glow-iris transition-shadow">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  submit(e as unknown as React.FormEvent);
                }
              }}
              placeholder="Message AetherChat…"
              rows={1}
              className="max-h-[200px] flex-1 resize-none bg-transparent px-2 py-2 text-sm font-body outline-none placeholder:text-secondary"
            />
            {isStreaming ? (
              <Button
                type="button"
                variant="danger"
                onClick={onStop}
                aria-label="Stop generation"
                size="icon"
              >
                <Square className="h-4 w-4 fill-current" />
              </Button>
            ) : (
              <Button
                type="submit"
                aria-label="Send message"
                size="icon"
                disabled={!value.trim()}
              >
                <SendHorizontal className="h-4 w-4" />
              </Button>
            )}
          </GlassCard>
        </form>
      </motion.div>

      {!isStreaming && !value && (
        <div className="flex flex-wrap items-center justify-center gap-2 px-2">
          {SUGGESTIONS.map((s, i) => (
            <motion.button
              key={s}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 * i, duration: 0.2 }}
              onClick={() => onSend(s)}
              className={cn(
                "inline-flex items-center gap-1.5 rounded-full glass px-3 py-1.5",
                "text-xs text-secondary transition-all hover:bg-white/15 hover:text-[var(--text-primary)]"
              )}
            >
              <Sparkles className="h-3 w-3 text-iris" />
              {s}
            </motion.button>
          ))}
        </div>
      )}
    </div>
  );
}
