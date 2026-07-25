"use client";

import * as React from "react";
import { SendHorizontal, Paperclip, FileCheck2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { ingestFile } from "@/lib/api";

type UploadState = "idle" | "uploading" | "done" | "error";

export function MessageInput({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  const [value, setValue] = React.useState("");
  const [uploadState, setUploadState] = React.useState<UploadState>("idle");
  const [uploadMsg, setUploadMsg] = React.useState("");
  const fileRef = React.useRef<HTMLInputElement>(null);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    onSend(value.trim());
    setValue("");
  }

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";
    setUploadState("uploading");
    setUploadMsg(file.name);
    try {
      const res = await ingestFile(file);
      setUploadState("done");
      setUploadMsg(`${file.name} — ${res.chunks_added} chunks added`);
      setTimeout(() => { setUploadState("idle"); setUploadMsg(""); }, 4000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Upload failed";
      setUploadState("error");
      setUploadMsg(msg);
      setTimeout(() => { setUploadState("idle"); setUploadMsg(""); }, 5000);
    }
  }

  return (
    <div className="space-y-2">
      {uploadState !== "idle" && (
        <div className={`flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-mono
          ${uploadState === "done" ? "bg-emerald-500/10 text-emerald-400" : ""}
          ${uploadState === "error" ? "bg-red-500/10 text-red-400" : ""}
          ${uploadState === "uploading" ? "bg-iris/10 text-secondary" : ""}
        `}>
          {uploadState === "uploading" && <Loader2 className="h-3 w-3 animate-spin" />}
          {uploadState === "done" && <FileCheck2 className="h-3 w-3" />}
          {uploadState === "error" && <AlertCircle className="h-3 w-3" />}
          {uploadMsg}
        </div>
      )}

      <form onSubmit={submit}>
        <GlassCard className="flex items-end gap-2 p-3">
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            disabled={uploadState === "uploading"}
            title="Upload a document"
            className="flex-shrink-0 rounded-lg p-2 text-secondary transition-colors hover:bg-white/10 hover:text-primary disabled:opacity-40"
          >
            {uploadState === "uploading"
              ? <Loader2 className="h-4 w-4 animate-spin" />
              : <Paperclip className="h-4 w-4" />
            }
          </button>

          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.md,.txt"
            className="hidden"
            onChange={handleFile}
          />

          <textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit(e);
              }
            }}
            disabled={disabled}
            placeholder={disabled ? "Thinking..." : "Ask the agent anything about your knowledge base..."}
            rows={1}
            className="max-h-32 flex-1 resize-none bg-transparent px-2 py-2 text-sm font-body outline-none placeholder:text-secondary disabled:opacity-50"
          />

          <Button type="submit" disabled={disabled} aria-label="Send message" className="h-10 w-10 p-0">
            <SendHorizontal className="h-4 w-4" />
          </Button>
        </GlassCard>
      </form>
    </div>
  );
}
