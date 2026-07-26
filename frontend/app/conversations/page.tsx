"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import {
  MessageSquare,
  Plus,
  Trash2,
  Search,
  Calendar,
  Filter,
} from "lucide-react";
import { toast } from "sonner";
import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { EmptyState, ErrorState } from "@/components/ui/states";
import { Skeleton, TableSkeleton } from "@/components/ui/loading-skeleton";
import { ConfirmDialog } from "@/components/ui/modal";
import { Pagination } from "@/components/ui/pagination";
import { Badge } from "@/components/ui/badge";
import {
  useConversations,
  useCreateConversation,
  useDeleteConversation,
} from "@/hooks/use-api";
import { useUIStore } from "@/store/ui-store";
import { cn } from "@/lib/utils";

import type { Conversation } from "@/lib/types";

const PAGE_SIZE = 10;

export default function ConversationsPage() {
  const router = useRouter();
  const setActive = useUIStore((s) => s.setActiveConversationId);
  const { data, isLoading, error, refetch, isFetching } = useConversations();
  const createConv = useCreateConversation();
  const deleteConv = useDeleteConversation();

  const [search, setSearch] = React.useState("");
  const [page, setPage] = React.useState(1);
  const [deleteTarget, setDeleteTarget] = React.useState<Conversation | null>(null);

  // Only show real data. Never fall back to mock IDs — they would be sent
  // to the backend and cause UUID validation errors.
  const conversations = data ?? [];

  const filtered = React.useMemo(() => {
    const list = conversations ?? [];
    if (!search.trim()) return list;
    const q = search.toLowerCase();
    return list.filter((c) => c.title.toLowerCase().includes(q));
  }, [conversations, search]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  React.useEffect(() => {
    setPage(1);
  }, [search]);

  function handleOpen(id: string) {
    setActive(id);
    router.push("/");
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await deleteConv.mutateAsync(deleteTarget.id);
      toast.success("Conversation deleted");
      setDeleteTarget(null);
    } catch {
      toast.error("Failed to delete");
    }
  }

  function handleCreate() {
    createConv.mutate(
      { title: "New chat" },
      {
        onSuccess: (c) => {
          setActive(c.id);
          toast.success("Conversation created");
          router.push("/");
        },
      }
    );
  }

  return (
    <AppShell minimumRole="viewer">
      {(user) => (
        <div className="flex h-full flex-col overflow-y-auto">
          <div className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 md:px-6">
          <Topbar
            title="Conversations"
            subtitle={`${filtered.length} total`}
            breadcrumb={[{ label: "Workspace" }, { label: "Conversations" }]}
            user={user}
            actions={
              <Button
                variant="primary"
                size="sm"
                onClick={handleCreate}
                disabled={createConv.isPending}
              >
                <Plus className="h-4 w-4" />
                New chat
              </Button>
            }
          />

          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="w-full max-w-md">
              <SearchInput
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search conversations…"
              />
            </div>
            <div className="flex items-center gap-2">
              <Badge tone="iris" className="capitalize">
                {filtered.length} found
              </Badge>
              <Badge tone="outline">Total pages: {totalPages}</Badge>
            </div>
          </div>

          {isLoading && !data ? (
            <TableSkeleton rows={PAGE_SIZE} cols={4} />
          ) : error ? (
            <ErrorState
              title="Failed to load conversations"
              description={error instanceof Error ? error.message : "Please try again."}
              onRetry={() => refetch()}
            />
          ) : filtered.length === 0 ? (
            <EmptyState
              title="No conversations"
              description={
                search
                  ? "No conversations match your search. Try a different keyword."
                  : "Start your first chat to see it listed here."
              }
              action="Start a new chat"
              onAction={handleCreate}
            />
          ) : (
            <>
              <GlassCard className="overflow-hidden">
                <div className="divide-y divide-white/10">
                  {paged.map((c) => (
                    <div
                      key={c.id}
                      className="group flex items-center gap-4 px-5 py-4 transition-colors hover:bg-white/5"
                    >
                      <div className="grid h-10 w-10 flex-shrink-0 place-items-center rounded-xl bg-gradient-to-br from-iris/25 to-aqua/15">
                        <MessageSquare className="h-5 w-5 text-iris" />
                      </div>
                      <div className="min-w-0 flex-1 cursor-pointer" onClick={() => handleOpen(c.id)}>
                        <div className="flex items-center gap-2">
                          <p className="truncate font-medium">{c.title}</p>
                        </div>
                        <div className="mt-1 flex items-center gap-3 text-xs text-secondary">
                          <span className="inline-flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            {c.updatedAt}
                          </span>
                          <Badge tone="default">{c.messageCount ?? 0} messages</Badge>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 opacity-0 transition-opacity group-hover:opacity-100">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleOpen(c.id)}
                        >
                          Open
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => setDeleteTarget(c)}
                          className="text-rose-400 hover:text-rose-400"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </GlassCard>
              <div className="mt-5">
                <Pagination
                  page={page}
                  totalPages={totalPages}
                  onPageChange={setPage}
                  totalItems={filtered.length}
                  itemsPerPage={PAGE_SIZE}
                />
              </div>
            </>
          )}

          <ConfirmDialog
            open={!!deleteTarget}
            onClose={() => setDeleteTarget(null)}
            onConfirm={handleDelete}
            title="Delete conversation?"
            description={deleteTarget ? `Delete "${deleteTarget.title}"? This cannot be undone.` : ""}
            confirmLabel="Delete"
            confirmVariant="danger"
            isLoading={deleteConv.isPending}
          />
          </div>
        </div>
      )}
    </AppShell>
  );
}
