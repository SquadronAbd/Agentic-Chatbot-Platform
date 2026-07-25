"use client";

import * as React from "react";
import { User } from "lucide-react";
import { GlassCard } from "@/components/ui/glass-card";
import { StreamingMessage } from "@/components/chat/streaming-message";
import { MessageInput } from "@/components/chat/message-input";
import { sendChat } from "@/lib/api";
import type { Message } from "@/lib/types";

function formatInline(text: string) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`(.+?)`/g, '<code class="rounded bg-white/20 px-1 py-0.5 font-mono text-[13px]">$1</code>');
}

const SESSION_ID = `session_${Math.random().toString(36).slice(2, 10)}`;

export function ChatWindow({ initialMessages }: { initialMessages: Message[] }) {
  const [messages, setMessages] = React.useState(initialMessages);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(text: string) {
    const userMessage: Message = {
      id: `m_${Date.now()}`,
      role: "user",
      content: text,
      createdAt: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    try {
      const res = await sendChat(SESSION_ID, text);
      if (!res.success || res.error) throw new Error(res.error ?? "Unknown error");

      const assistantMessage: Message = {
        id: `m_${Date.now()}_a`,
        role: "assistant",
        content: res.answer,
        tokens: res.documents_retrieved,
        createdAt: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to reach backend";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-4">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto pr-1">
        {messages.map((message) =>
          message.role === "user" ? (
            <div key={message.id} className="flex items-start justify-end gap-3">
              <GlassCard strong className="max-w-[75%] bg-gradient-to-br from-iris/25 to-aqua/10 px-4 py-3">
                <p
                  className="text-sm leading-relaxed font-body"
                  dangerouslySetInnerHTML={{ __html: formatInline(message.content) }}
                />
                <p className="mt-1 font-mono text-[11px] text-secondary">{message.createdAt}</p>
              </GlassCard>
              <div className="mt-1 grid h-7 w-7 flex-shrink-0 place-items-center rounded-full bg-white/30">
                <User className="h-3.5 w-3.5" />
              </div>
            </div>
          ) : (
            <StreamingContentBubble key={message.id} content={message.content} tokens={message.tokens} />
          )
        )}

        {loading && <StreamingMessage fullText="Thinking..." tokens={0} />}

        {error && (
          <div className="rounded-lg border border-red-400/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}
      </div>

      <MessageInput onSend={handleSend} disabled={loading} />
    </div>
  );
}

function StreamingContentBubble({ content, tokens }: { content: string; tokens?: number }) {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-1 grid h-7 w-7 flex-shrink-0 place-items-center rounded-full bg-gradient-to-br from-iris to-aqua shadow-glow-iris">
        <span className="font-display text-[10px] font-bold text-white">AI</span>
      </div>
      <GlassCard className="max-w-[75%] px-4 py-3">
        <p
          className="text-sm leading-relaxed font-body"
          dangerouslySetInnerHTML={{ __html: formatInline(content) }}
        />
        {tokens !== undefined && tokens > 0 && (
          <p className="mt-2 font-mono text-[11px] text-secondary">{tokens} docs retrieved</p>
        )}
      </GlassCard>
    </div>
  );
}
