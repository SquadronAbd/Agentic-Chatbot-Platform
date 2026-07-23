import { FileText, Trash2 } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import type { KnowledgeDocument } from "@/lib/types";

const STATUS_TONE = {
  ready: "success",
  processing: "warning",
  error: "danger",
} as const;

export function DocumentList({ documents }: { documents: KnowledgeDocument[] }) {
  return (
    <GlassCard className="overflow-hidden">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-[var(--glass-border)] text-secondary">
            <th className="px-5 py-3 font-display font-medium">File</th>
            <th className="px-5 py-3 font-display font-medium">Status</th>
            <th className="px-5 py-3 font-display font-medium">Chunks</th>
            <th className="px-5 py-3 font-display font-medium">Uploaded</th>
            <th className="px-5 py-3" />
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id} className="border-b border-[var(--glass-border)] last:border-0 hover:bg-white/5">
              <td className="flex items-center gap-2.5 px-5 py-3.5">
                <FileText className="h-4 w-4 flex-shrink-0 text-secondary" />
                <span className="truncate font-body">{doc.filename}</span>
                <span className="font-mono text-xs text-secondary">{doc.sizeKb} KB</span>
              </td>
              <td className="px-5 py-3.5">
                <Badge tone={STATUS_TONE[doc.status]}>{doc.status}</Badge>
              </td>
              <td className="px-5 py-3.5 font-mono text-xs text-secondary">{doc.chunkCount}</td>
              <td className="px-5 py-3.5 font-mono text-xs text-secondary">{doc.uploadedAt}</td>
              <td className="px-5 py-3.5 text-right">
                <button
                  aria-label={`Delete ${doc.filename}`}
                  className="rounded-lg p-1.5 text-secondary transition-colors hover:bg-rose-500/15 hover:text-rose-400"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </GlassCard>
  );
}
