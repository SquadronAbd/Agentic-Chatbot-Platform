"use client";

import * as React from "react";
import {
  UploadCloud,
  Trash2,
  FileText,
  FileSpreadsheet,
  File,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { EmptyState, ErrorState } from "@/components/ui/states";
import { TableSkeleton } from "@/components/ui/loading-skeleton";
import { ConfirmDialog } from "@/components/ui/modal";
import { Badge } from "@/components/ui/badge";
import { useDocuments, useUploadDocument, useDeleteDocument } from "@/hooks/use-api";

import type { KnowledgeDocument, DocumentStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

function iconForDoc(name: string) {
  const n = name.toLowerCase();
  if (n.endsWith(".pdf")) return FileText;
  if (n.match(/\.(csv|xlsx|xls|sheet)$/)) return FileSpreadsheet;
  return File;
}

function toneForStatus(status: DocumentStatus): Parameters<typeof Badge>[0]["tone"] {
  switch (status) {
    case "ready":
      return "success";
    case "processing":
      return "warning";
    case "error":
      return "danger";
  }
}

function formatSize(kb: number) {
  if (kb < 1024) return `${kb} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

export default function DocumentsPage() {
  const { data, isLoading, error, refetch } = useDocuments();
  const uploader = useUploadDocument();
  const deleter = useDeleteDocument();

  const [search, setSearch] = React.useState("");
  const [deleteTarget, setDeleteTarget] = React.useState<KnowledgeDocument | null>(null);
  const [dragOver, setDragOver] = React.useState(false);
  const [uploadProgress, setUploadProgress] = React.useState<{ name: string; pct: number } | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const documents = data ?? [];
  const filtered = React.useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return documents;
    return documents.filter((d) => d.filename.toLowerCase().includes(q));
  }, [documents, search]);

  async function handleFiles(files: FileList | File[]) {
    const arr = Array.from(files);
    for (const f of arr) {
      setUploadProgress({ name: f.name, pct: 0 });
      try {
        await uploader.mutateAsync({
          file: f,
          onProgress: (p) => setUploadProgress({ name: f.name, pct: p }),
        });
        toast.success(`Uploaded "${f.name}"`);
      } catch {
        toast.error(`Failed to upload "${f.name}"`);
      } finally {
        setUploadProgress(null);
      }
    }
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.length) {
      void handleFiles(e.dataTransfer.files);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await deleter.mutateAsync(deleteTarget.id);
      toast.success("Document deleted");
      setDeleteTarget(null);
    } catch {
      toast.error("Failed to delete document");
    }
  }

  function pickFiles() {
    fileInputRef.current?.click();
  }

  return (
    <AppShell minimumRole="agent">
      {(user) => (
        <div className="flex h-full flex-col overflow-y-auto">
          <div className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 md:px-6">
          <Topbar
            title="Knowledge base"
            subtitle={`${filtered.length} document${filtered.length === 1 ? "" : "s"}`}
            breadcrumb={[{ label: "Workspace" }, { label: "Knowledge base" }]}
            user={user}
            actions={
              <Button
                variant="primary"
                size="sm"
                onClick={pickFiles}
                disabled={uploader.isPending}
              >
                {uploader.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <UploadCloud className="h-4 w-4" />
                )}
                Upload
              </Button>
            }
          />

          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={cn(
              "mb-5 rounded-glass border-2 border-dashed transition-all",
              dragOver
                ? "border-iris bg-iris/10 shadow-glow-iris"
                : "border-white/15 bg-transparent"
            )}
          >
            <button
              type="button"
              onClick={pickFiles}
              className="flex w-full flex-col items-center justify-center gap-3 rounded-glass px-6 py-8 text-center transition-colors hover:bg-white/5"
            >
              <div className="grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-iris/25 to-aqua/20 shadow-glow-iris">
                <UploadCloud className="h-7 w-7 text-iris-light" />
              </div>
              <div>
                <p className="font-display font-semibold">Drop files here or click to upload</p>
                <p className="mt-1 text-xs text-secondary">
                  PDFs, CSVs, DOCX, TXT — up to 50MB each
                </p>
              </div>
              {uploadProgress && (
                <div className="w-full max-w-md">
                  <div className="mb-1 flex justify-between text-xs text-secondary">
                    <span className="truncate">{uploadProgress.name}</span>
                    <span>{uploadProgress.pct}%</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${uploadProgress.pct}%` }}
                      transition={{ duration: 0.2 }}
                      className="h-full rounded-full bg-gradient-to-r from-iris to-aqua"
                    />
                  </div>
                </div>
              )}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              hidden
              onChange={(e) => e.target.files && void handleFiles(e.target.files)}
            />
          </div>

          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="w-full max-w-md">
              <SearchInput
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search documents…"
              />
            </div>
            <div className="flex items-center gap-2">
              <Badge tone="aqua">{filtered.length} results</Badge>
              <Button
                variant="glass"
                size="sm"
                onClick={() => refetch()}
                disabled={isLoading}
              >
                <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
                Refresh
              </Button>
            </div>
          </div>

          {isLoading && !data ? (
            <TableSkeleton rows={6} cols={5} />
          ) : error ? (
            <ErrorState
              title="Failed to load documents"
              description={error instanceof Error ? error.message : "Try again later."}
              onRetry={() => refetch()}
            />
          ) : filtered.length === 0 ? (
            <EmptyState
              title="No documents yet"
              description={
                search
                  ? "No documents match your search."
                  : "Upload your first document to enable RAG-powered answers."
              }
              icon={Sparkles}
              action="Upload document"
              onAction={pickFiles}
            />
          ) : (
            <GlassCard className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-white/10 bg-white/5">
                    <tr>
                      <th className="px-5 py-3 font-semibold">Name</th>
                      <th className="px-5 py-3 font-semibold">Status</th>
                      <th className="px-5 py-3 font-semibold">Size</th>
                      <th className="px-5 py-3 font-semibold">Chunks</th>
                      <th className="px-5 py-3 font-semibold">Uploaded</th>
                      <th className="w-24 px-5 py-3" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    <AnimatePresence initial={false}>
                      {filtered.map((d) => {
                        const Icon = iconForDoc(d.filename);
                        return (
                          <motion.tr
                            key={d.id}
                            layout
                            initial={{ opacity: 0, y: 4 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            className="transition-colors hover:bg-white/5"
                          >
                            <td className="px-5 py-4">
                              <div className="flex items-center gap-3">
                                <div className="grid h-9 w-9 flex-shrink-0 place-items-center rounded-xl bg-gradient-to-br from-iris/15 to-aqua/10">
                                  <Icon className="h-5 w-5 text-iris" />
                                </div>
                                <div className="min-w-0">
                                  <p className="truncate font-medium">{d.filename}</p>
                                </div>
                              </div>
                            </td>
                            <td className="px-5 py-4">
                              <Badge tone={toneForStatus(d.status)}>
                                {d.status === "processing" && (
                                  <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                                )}
                                {d.status === "ready" && (
                                  <CheckCircle2 className="mr-1 h-3 w-3" />
                                )}
                                {d.status === "error" && (
                                  <AlertTriangle className="mr-1 h-3 w-3" />
                                )}
                                <span className="capitalize">{d.status}</span>
                              </Badge>
                            </td>
                            <td className="px-5 py-4 text-sm text-secondary">
                              {formatSize(d.sizeKb ?? 0)}
                            </td>
                            <td className="px-5 py-4 text-sm text-secondary">
                              {d.chunkCount}
                            </td>
                            <td className="px-5 py-4 text-sm text-secondary">
                              {d.uploadedAt}
                            </td>
                            <td className="px-5 py-4 text-right">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setDeleteTarget(d)}
                                className="text-rose-400 hover:text-rose-400"
                                aria-label="Delete"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </td>
                          </motion.tr>
                        );
                      })}
                    </AnimatePresence>
                  </tbody>
                </table>
              </div>
            </GlassCard>
          )}

          <ConfirmDialog
            open={!!deleteTarget}
            onClose={() => setDeleteTarget(null)}
            onConfirm={handleDelete}
            title="Delete document?"
            description={
              deleteTarget
                ? `Delete "${deleteTarget.filename}"? This will remove the file record. Existing embeddings in the knowledge base are retained.`
                : ""
            }
            confirmLabel="Delete"
            confirmVariant="danger"
            isLoading={deleter.isPending}
          />
          </div>
        </div>
      )}
    </AppShell>
  );
}
