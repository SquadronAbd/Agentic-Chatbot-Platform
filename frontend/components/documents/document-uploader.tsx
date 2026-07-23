"use client";

import * as React from "react";
import { UploadCloud, FileCheck2 } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";

interface UploadJob {
  name: string;
  progress: number;
}

export function DocumentUploader({ onUploaded }: { onUploaded?: (filename: string) => void }) {
  const [isDragging, setIsDragging] = React.useState(false);
  const [jobs, setJobs] = React.useState<UploadJob[]>([]);
  const inputRef = React.useRef<HTMLInputElement>(null);

  function startUpload(files: FileList | File[]) {
    Array.from(files).forEach((file) => {
      setJobs((prev) => [...prev, { name: file.name, progress: 0 }]);
      simulateProgress(file.name);
    });
  }

  // Stands in for polling GET /documents while status is "processing".
  function simulateProgress(name: string) {
    const interval = setInterval(() => {
      setJobs((prev) =>
        prev.map((job) => {
          if (job.name !== name) return job;
          const next = Math.min(job.progress + Math.random() * 22, 100);
          return { ...job, progress: next };
        })
      );
    }, 260);

    setTimeout(() => {
      clearInterval(interval);
      setJobs((prev) => prev.map((job) => (job.name === name ? { ...job, progress: 100 } : job)));
      onUploaded?.(name);
    }, 1600);
  }

  return (
    <div className="space-y-4">
      <GlassCard
        className={cn(
          "flex flex-col items-center justify-center gap-3 rounded-glass border-2 border-dashed px-6 py-12 text-center transition-colors",
          isDragging ? "border-iris/70 bg-iris/5" : "border-transparent"
        )}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (e.dataTransfer.files.length) startUpload(e.dataTransfer.files);
        }}
      >
        <div className="grid h-12 w-12 place-items-center rounded-full bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
          <UploadCloud className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="font-display text-sm font-semibold">Drop files to add to the knowledge base</p>
          <p className="text-sm text-secondary">PDF, DOCX, or TXT — chunking and embedding start automatically</p>
        </div>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="font-display text-sm font-medium text-iris-dim underline-offset-4 hover:underline dark:text-iris-light"
        >
          Browse files
        </button>
        <input
          ref={inputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => e.target.files && startUpload(e.target.files)}
        />
      </GlassCard>

      {jobs.length > 0 && (
        <div className="space-y-2">
          {jobs.map((job) => (
            <GlassCard key={job.name} className="flex items-center gap-3 px-4 py-3">
              {job.progress >= 100 ? (
                <FileCheck2 className="h-4 w-4 flex-shrink-0 text-emerald-400" />
              ) : (
                <UploadCloud className="h-4 w-4 flex-shrink-0 text-iris-dim dark:text-iris-light" />
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-body">{job.name}</p>
                <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-white/20">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-iris to-aqua transition-all"
                    style={{ width: `${job.progress}%` }}
                  />
                </div>
              </div>
              <span className="font-mono text-xs text-secondary">
                {job.progress >= 100 ? "ready" : `${Math.round(job.progress)}%`}
              </span>
            </GlassCard>
          ))}
        </div>
      )}
    </div>
  );
}
