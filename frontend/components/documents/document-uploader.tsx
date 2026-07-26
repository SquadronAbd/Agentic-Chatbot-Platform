"use client";

import * as React from "react";
import { UploadCloud, FileCheck2, AlertCircle } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { ingestFile } from "@/lib/api";
import { cn } from "@/lib/utils";

type JobStatus = "uploading" | "done" | "error";

interface UploadJob {
  name: string;
  status: JobStatus;
  chunks?: number;
  error?: string;
}

export function DocumentUploader({ onUploaded }: { onUploaded?: (filename: string) => void }) {
  const [isDragging, setIsDragging] = React.useState(false);
  const [jobs, setJobs] = React.useState<UploadJob[]>([]);
  const inputRef = React.useRef<HTMLInputElement>(null);

  function updateJob(name: string, patch: Partial<UploadJob>) {
    setJobs((prev) => prev.map((j) => (j.name === name ? { ...j, ...patch } : j)));
  }

  async function startUpload(files: FileList | File[]) {
    const fileArray = Array.from(files);
    // Add all as uploading first so the UI responds immediately
    setJobs((prev) => [
      ...prev,
      ...fileArray.map((f) => ({ name: f.name, status: "uploading" as JobStatus })),
    ]);

    await Promise.all(
      fileArray.map(async (file) => {
        try {
          const res = await ingestFile(file);
          updateJob(file.name, { status: "done", chunks: res.chunks_added });
          onUploaded?.(file.name);
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : "Upload failed";
          updateJob(file.name, { status: "error", error: msg });
        }
      })
    );
  }

  return (
    <div className="space-y-4">
      <GlassCard
        className={cn(
          "flex flex-col items-center justify-center gap-3 rounded-glass border-2 border-dashed px-6 py-12 text-center transition-colors cursor-pointer",
          isDragging ? "border-iris/70 bg-iris/5" : "border-transparent"
        )}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files.length) startUpload(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
      >
        <div className="grid h-12 w-12 place-items-center rounded-full bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
          <UploadCloud className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="font-display text-sm font-semibold">Drop files to add to the knowledge base</p>
          <p className="text-sm text-secondary">PDF, MD, or TXT — chunked and embedded automatically</p>
        </div>
        <span className="font-display text-sm font-medium text-iris-dim underline-offset-4 hover:underline dark:text-iris-light">
          Browse files
        </span>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.md,.txt"
          className="hidden"
          onClick={(e) => e.stopPropagation()}
          onChange={(e) => e.target.files && startUpload(e.target.files)}
        />
      </GlassCard>

      {jobs.length > 0 && (
        <div className="space-y-2">
          {jobs.map((job) => (
            <GlassCard key={job.name} className="flex items-center gap-3 px-4 py-3">
              {job.status === "done" && <FileCheck2 className="h-4 w-4 flex-shrink-0 text-emerald-400" />}
              {job.status === "error" && <AlertCircle className="h-4 w-4 flex-shrink-0 text-red-400" />}
              {job.status === "uploading" && (
                <UploadCloud className="h-4 w-4 flex-shrink-0 animate-pulse text-iris-dim dark:text-iris-light" />
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-body">{job.name}</p>
                {job.status === "uploading" && (
                  <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-white/20">
                    <div className="h-full w-full animate-pulse rounded-full bg-gradient-to-r from-iris to-aqua" />
                  </div>
                )}
                {job.status === "error" && (
                  <p className="mt-0.5 text-xs text-red-400">{job.error}</p>
                )}
              </div>
              <span className="font-mono text-xs text-secondary">
                {job.status === "uploading" && "uploading…"}
                {job.status === "done" && `${job.chunks ?? 0} chunks`}
                {job.status === "error" && "failed"}
              </span>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
}
