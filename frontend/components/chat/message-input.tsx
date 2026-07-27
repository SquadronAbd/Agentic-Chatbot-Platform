"use client";

import * as React from "react";
import {
  SendHorizontal,
  Square,
  Sparkles,
  Paperclip,
  FileCheck2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";
import { ingestFile } from "@/lib/api";

const SUGGESTIONS = [
  "Summarize the latest uploaded documents",
  "What are the key themes in the support tickets?",
  "Draft a follow-up email for the Q3 review",
  "Explain the pricing model changes",
];

type UploadState = "idle" | "uploading" | "done" | "error";

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

  const [uploadState, setUploadState] =
    React.useState<UploadState>("idle");
  const [uploadMsg, setUploadMsg] = React.useState("");

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
  }

  async function handleFile(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = e.target.files?.[0];

    if (!file) return;

    e.target.value = "";

    setUploadState("uploading");
    setUploadMsg(file.name);

    try {
      const res = await ingestFile(file);

      setUploadState("done");
      setUploadMsg(
        `${file.name} — ${res.chunks_added} chunks added`
      );

      setTimeout(() => {
        setUploadState("idle");
        setUploadMsg("");
      }, 4000);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Upload failed";

      setUploadState("error");
      setUploadMsg(msg);

      setTimeout(() => {
        setUploadState("idle");
        setUploadMsg("");
      }, 5000);
    }
  }

  return (
    <div className="space-y-3">
      {uploadState !== "idle" && (
        <div
          className={cn(
            "flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-mono",
            uploadState === "done" &&
              "bg-emerald-500/10 text-emerald-400",
            uploadState === "error" &&
              "bg-red-500/10 text-red-400",
            uploadState === "uploading" &&
              "bg-iris/10 text-secondary"
          )}
        >
          {uploadState === "uploading" && (
            <Loader2 className="h-3 w-3 animate-spin" />
          )}

          {uploadState === "done" && (
            <FileCheck2 className="h-3 w-3" />
          )}

          {uploadState === "error" && (
            <AlertCircle className="h-3 w-3" />
          )}

          {uploadMsg}
        </div>
      )}

      <motion.div
        initial={false}
        animate={{ y: 0, opacity: 1 }}
        transition={{
          type: "spring",
          stiffness: 280,
          damping: 24,
        }}
      >
        <form onSubmit={submit}>
          <GlassCard className="flex items-end gap-3 p-3 shadow-glass-lg focus-within:shadow-glow-iris transition-shadow">
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              disabled={uploadState === "uploading"}
              title="Upload document"
              className="flex-shrink-0 rounded-lg p-2 text-secondary transition-colors hover:bg-white/10 hover:text-primary disabled:opacity-40"
            >
              {uploadState === "uploading" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Paperclip className="h-4 w-4" />
              )}
            </button>

            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.txt,.md"
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
              transition={{
                delay: i * 0.05,
                duration: 0.2,
              }}
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