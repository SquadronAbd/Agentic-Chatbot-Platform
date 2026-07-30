"use client";

import * as React from "react";
import { Trash2, Sparkles, Menu, PenLine } from "lucide-react";
import { toast } from "sonner";
import { StreamingMessage, UserMessage } from "@/components/chat/streaming-message";
import { MessageInput } from "@/components/chat/message-input";
import { ChatSkeleton } from "@/components/ui/loading-skeleton";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/modal";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { Avatar } from "@/components/ui/avatar";
import { useChatStream } from "@/hooks/use-chat-stream";
import { useChatStore } from "@/store/chat-store";
import { useMessages, useCreateConversation, useDeleteConversation, useConversations } from "@/hooks/use-api";
import { useUIStore } from "@/store/ui-store";
import { useAuthStore } from "@/store/auth-store";
import { cn } from "@/lib/utils";
import type { CurrentUser } from "@/lib/types";

export function ChatWindow({ user }: { user: CurrentUser }) {
  const activeConversationId = useUIStore((s) => s.activeConversationId);
  const setActive = useUIStore((s) => s.setActiveConversationId);
  const setMobile = useUIStore((s) => s.setMobileMenuOpen);
  const logout = useAuthStore((s) => s.logout);

  const { data: apiMessages, isLoading: messagesLoading } = useMessages(activeConversationId);
  const { data: convs } = useConversations();
  const createConv = useCreateConversation();
  const deleteConv = useDeleteConversation();

  const activeTitle = React.useMemo(() => {
    if (!activeConversationId) return "New chat";
    return convs?.find((c) => c.id === activeConversationId)?.title ?? "Chat";
  }, [convs, activeConversationId]);

  const {
    send,
    stop,
    regenerate,
    clearMessages,
    updateMessage,
    isStreaming,
    streamingContent,
    streamingMessageId,
    messages,
    setMessages,
    wsStatus,
  } = useChatStream(activeConversationId);

  const [showClearConfirm, setShowClearConfirm] = React.useState(false);

  const displayMessages = React.useMemo(() => {
    if (messages.length > 0) return messages;
    if (apiMessages && apiMessages.length > 0) return apiMessages;
    return [];
  }, [messages, apiMessages]);

  React.useEffect(() => {
    // Don't override in-flight streaming messages with a DB refetch.
    if (useChatStore.getState().isStreaming) return;
    if (apiMessages && apiMessages.length > 0) {
      setMessages(apiMessages);
    }
  }, [apiMessages, setMessages]);

  const scrollRef = React.useRef<HTMLDivElement>(null);
  React.useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [displayMessages, streamingContent, isStreaming]);

  async function handleSend(prompt: string) {
    let convId = activeConversationId;
    if (!convId) {
      try {
        const conv = await createConv.mutateAsync({ title: prompt.slice(0, 60) });
        convId = conv.id;
        setActive(conv.id);
        // Poll the store directly (avoids stale closure) until WS connects or 2s elapses.
        for (let i = 0; i < 20; i++) {
          if (useChatStore.getState().wsStatus === "connected") break;
          await new Promise((r) => setTimeout(r, 100));
        }
      } catch {
        toast.error("Could not create conversation");
        return;
      }
    }
    try {
      send(prompt);
    } catch {
      toast.error("Not connected to chat stream");
    }
  }

  const visibleMessages = React.useMemo(() => {
    if (!streamingMessageId) return displayMessages;
    return displayMessages.map((m) =>
      m.id === streamingMessageId && streamingContent ? { ...m, content: streamingContent } : m
    );
  }, [displayMessages, streamingMessageId, streamingContent]);

  const lastAssistantIdx = React.useMemo(
    () => [...visibleMessages].reverse().findIndex((m) => m.role === "assistant"),
    [visibleMessages]
  );

  const isEmpty = visibleMessages.length === 0;

  // WS status indicator colour
  const wsColor =
    wsStatus === "connected" ? "bg-emerald-400" :
    wsStatus === "connecting" ? "bg-amber-400 animate-pulse" :
    wsStatus === "error" ? "bg-rose-500" : "bg-white/20";

  return (
    <div className="flex h-full flex-col">
      {/* ── Header ─────────────────────────────────────────── */}
      <header className="flex flex-shrink-0 items-center justify-between border-b border-white/8 px-4 py-3">
        <div className="flex items-center gap-3">
          {/* Mobile hamburger */}
          <button
            type="button"
            className="rounded-xl p-1.5 text-secondary hover:bg-white/10 hover:text-[var(--text-primary)] md:hidden"
            onClick={() => setMobile(true)}
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>

          <div className="flex items-center gap-2">
            <span className="font-display text-sm font-semibold tracking-tight truncate max-w-[160px] sm:max-w-xs">
              {activeTitle}
            </span>
            {/* WS connection dot */}
            <span title={`WebSocket: ${wsStatus}`} className={cn("inline-block h-2 w-2 rounded-full", wsColor)} />
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <Button
            variant="ghost"
            size="sm"
            className="gap-1.5 text-xs"
            onClick={() => { setActive(null); clearMessages(); }}
          >
            <PenLine className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">New chat</span>
          </Button>

          {!isEmpty && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowClearConfirm(true)}
              className="text-secondary hover:text-rose-400"
              title="Clear conversation"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}

          <ThemeToggle />

          {/* User avatar */}
          <button
            type="button"
            onClick={() => logout().then(() => window.location.replace("/login"))}
            title="Sign out"
            className="ml-1"
          >
            <Avatar name={user.name} size="sm" />
          </button>
        </div>
      </header>

      {/* ── Messages scroll area ───────────────────────────── */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-6 space-y-1"
      >
        {messagesLoading && !messages.length ? (
          <ChatSkeleton messages={3} />
        ) : isEmpty ? (
          <EmptyWelcome user={user} onSuggestion={handleSend} />
        ) : (
          <div className="mx-auto w-full max-w-3xl space-y-6">
            {visibleMessages.map((m, idx) =>
              m.role === "user" ? (
                <UserMessage
                  key={m.id}
                  content={m.content}
                  timestamp={m.createdAt}
                  name={user.name}
                />
              ) : (
                <StreamingMessage
                  key={m.id}
                  content={m.content}
                  tokens={m.tokens}
                  timestamp={m.createdAt}
                  isStreaming={m.id === streamingMessageId && isStreaming}
                  onStop={stop}
                  onRegenerate={
                    lastAssistantIdx !== -1 && idx === visibleMessages.length - 1 - lastAssistantIdx
                      ? () => {
                          try { regenerate(); } catch { toast.error("Nothing to regenerate"); }
                        }
                      : undefined
                  }
                />
              )
            )}
          </div>
        )}
      </div>


      {/* ── Input area ─────────────────────────────────────── */}
      <div className="flex-shrink-0 border-t border-white/8 bg-[var(--page-bg-a)]/60 backdrop-blur-md px-4 py-4">
        <div className="mx-auto w-full max-w-3xl">
          <MessageInput onSend={handleSend} onStop={stop} isStreaming={isStreaming} />
          <p className="mt-2 text-center text-[11px] text-secondary">
            FinRAG can make mistakes. Consider checking important information.
          </p>
        </div>
      </div>

      {/* ── Confirm clear dialog ───────────────────────────── */}
      <ConfirmDialog
        open={showClearConfirm}
        onClose={() => setShowClearConfirm(false)}
        onConfirm={() => {
          clearMessages();
          if (activeConversationId) {
            deleteConv.mutate(activeConversationId, {
              onSuccess: () => {
                setActive(null);
                toast.success("Conversation cleared");
              },
            });
          }
          setShowClearConfirm(false);
        }}
        title="Clear conversation?"
        description="This cannot be undone. All messages in this chat will be deleted."
        confirmLabel="Clear"
        confirmVariant="danger"
        isLoading={deleteConv.isPending}
      />
    </div>
  );
}

const SUGGESTIONS = [
  { label: "Summarize the latest uploaded documents", emoji: "📄" },
  { label: "What are the key themes in the support tickets?", emoji: "🔍" },
  { label: "Draft a follow-up email for the Q3 review", emoji: "✉️" },
  { label: "Explain the pricing model changes", emoji: "💡" },
];

function EmptyWelcome({ user, onSuggestion }: { user: CurrentUser; onSuggestion: (s: string) => void }) {
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div className="flex h-full flex-col items-center justify-center gap-8 px-4 py-12">
      {/* Avatar + greeting */}
      <div className="flex flex-col items-center gap-3 text-center">
        <div className="grid h-16 w-16 place-items-center rounded-2xl bg-gradient-to-br from-iris/40 to-aqua/25 shadow-glow-iris">
          <Sparkles className="h-8 w-8 text-iris-light" />
        </div>
        <div>
          <h2 className="font-display text-2xl font-semibold tracking-tight">
            {greeting}, {user.name.split(" ")[0]}
          </h2>
          <p className="mt-1 text-sm text-secondary">
            How can FinRAG help you today?
          </p>
        </div>
      </div>

      {/* Suggestion grid */}
      <div className="grid w-full max-w-2xl grid-cols-1 gap-3 sm:grid-cols-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s.label}
            onClick={() => onSuggestion(s.label)}
            className={cn(
              "group flex items-start gap-3 rounded-xl border border-white/8 bg-white/5 p-4 text-left",
              "transition-all hover:border-iris/30 hover:bg-white/10 hover:shadow-glow-iris"
            )}
          >
            <span className="text-xl leading-none">{s.emoji}</span>
            <span className="text-sm text-secondary group-hover:text-[var(--text-primary)] transition-colors">
              {s.label}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
