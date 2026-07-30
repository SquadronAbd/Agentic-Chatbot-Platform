"use client";

import * as React from "react";
import {
  SendHorizontal,
  Square,
  Sparkles,
  Paperclip,
  AlertCircle,
  Loader2,
  FileText,
  X,
  CheckCircle2,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";
import api from "@/lib/api";

const SUGGESTIONS = [
  "Summarize the latest uploaded documents",
  "What are the key themes in the support tickets?",
  "Draft a follow-up email for the Q3 review",
  "Explain the pricing model changes",
];

type AttachState = "uploading" | "ready" | "error";

interface AttachedFile {
  name: string;
  state: AttachState;
  chunks?: number;
  error?: string;
}

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
  const [attached, setAttached] = React.useState<AttachedFile | null>(null);

  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const fileRef = React.useRef<HTMLInputElement>(null);

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
    // Keep the chip visible — user may ask follow-up questions about the same file.
  }

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";

    setAttached({ name: file.name, state: "uploading" });

    try {
      const form = new FormData();
      form.append("file", file);
      const { data } = await api.post<{
        id: string;
        filename: string;
        status: string;
        chunk_count: number;
      }>("/documents/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setAttached({
        name: data.filename ?? file.name,
        state: "ready",
        chunks: data.chunk_count ?? 0,
      });
    } catch (err: unknown) {
      setAttached({
        name: file.name,
        state: "error",
        error: err instanceof Error ? err.message : "Upload failed",
      });
    }
  }

  return (
    <div className="space-y-3">
      <motion.div
        initial={false}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: "spring", stiffness: 280, damping: 24 }}
      >
        <form onSubmit={submit}>
          <GlassCard className="flex flex-col gap-2 p-3 shadow-glass-lg focus-within:shadow-glow-iris transition-shadow">

            {/* File chip — persists until dismissed */}
            <AnimatePresence>
              {attached && (
                <motion.div
                  key="chip"
                  initial={{ opacity: 0, scale: 0.95, y: -4 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.15 }}
                  className={cn(
                    "flex items-center gap-2 self-start rounded-xl px-3 py-2 text-xs",
                    attached.state === "uploading" && "bg-iris/10 text-secondary",
                    attached.state === "ready" && "bg-emerald-500/10 text-emerald-400",
                    attached.state === "error" && "bg-rose-500/10 text-rose-400",
                  )}
                >
                  {attached.state === "uploading" && <Loader2 className="h-3.5 w-3.5 animate-spin flex-shrink-0" />}
                  {attached.state === "ready" && <CheckCircle2 className="h-3.5 w-3.5 flex-shrink-0" />}
                  {attached.state === "error" && <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" />}
                  <FileText className="h-3.5 w-3.5 flex-shrink-0" />
                  <span className="max-w-[200px] truncate font-mono">
                    {attached.name}
                  </span>
                  {attached.state === "uploading" && (
                    <span className="text-secondary">Ingesting…</span>
                  )}
                  {attached.state === "ready" && attached.chunks !== undefined && (
                    <span className="text-emerald-500/70">
                      {attached.chunks > 0 ? `${attached.chunks} chunks` : "processing…"}
                    </span>
                  )}
                  {attached.state === "error" && (
                    <span className="truncate">{attached.error}</span>
                  )}
                  <button
                    type="button"
                    onClick={() => setAttached(null)}
                    className="ml-1 rounded-full p-0.5 opacity-60 hover:opacity-100 transition-opacity"
                    aria-label="Remove attachment"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="flex items-end gap-3">
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                disabled={attached?.state === "uploading"}
                title="Upload document"
                className="flex-shrink-0 rounded-lg p-2 text-secondary transition-colors hover:bg-white/10 hover:text-primary disabled:opacity-40"
              >
                {attached?.state === "uploading" ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Paperclip className="h-4 w-4" />
                )}
              </button>

              <input
                ref={fileRef}
                type="file"
                accept=".pdf,.txt,.md,.docx,.csv"
                className="hidden"
                onChange={handleFile}
              />

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
                placeholder="Message FinRAG…"
                rows={1}
                className="max-h-[200px] flex-1 resize-none bg-transparent px-2 py-2 text-sm font-body outline-none placeholder:text-secondary"
              />

              {isStreaming ? (
                <Button
                  type="button"
                  variant="danger"
                  onClick={onStop}
                  size="icon"
                  aria-label="Stop generation"
                >
                  <Square className="h-4 w-4 fill-current" />
                </Button>
              ) : (
                <Button
                  type="submit"
                  size="icon"
                  disabled={!value.trim()}
                  aria-label="Send message"
                >
                  <SendHorizontal className="h-4 w-4" />
                </Button>
              )}
            </div>
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
              transition={{ delay: i * 0.05, duration: 0.2 }}
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
