import Link from "next/link";
import { MessageSquare, MoreHorizontal } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { MOCK_CONVERSATIONS, MOCK_USER } from "@/lib/mock-data";

export default function ConversationsPage() {
  return (
    <AppShell user={MOCK_USER}>
      <Topbar title="Conversations" subtitle={`${MOCK_CONVERSATIONS.length} threads`} user={MOCK_USER} />

      <div className="mb-4 flex justify-end">
        <Button variant="primary">New conversation</Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {MOCK_CONVERSATIONS.map((c) => (
          <Link key={c.id} href="/">
            <GlassCard className="flex items-start justify-between gap-3 px-5 py-4 transition-transform hover:-translate-y-0.5">
              <div className="flex items-start gap-3">
                <div className="mt-0.5 grid h-9 w-9 flex-shrink-0 place-items-center rounded-xl bg-gradient-to-br from-iris/25 to-aqua/15">
                  <MessageSquare className="h-4 w-4 text-iris-dim dark:text-iris-light" />
                </div>
                <div>
                  <p className="font-display text-sm font-semibold">{c.title}</p>
                  <p className="text-xs text-secondary">
                    {c.messageCount} messages · updated {c.updatedAt}
                  </p>
                </div>
              </div>
              <button aria-label="More options" className="rounded-lg p-1.5 text-secondary hover:bg-white/10">
                <MoreHorizontal className="h-4 w-4" />
              </button>
            </GlassCard>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
