"use client";

import * as React from "react";
import type { Message } from "@/lib/types";
import { useChatStore } from "@/store/chat-store";
import { useAuthStore } from "@/store/auth-store";

const BACKEND_ABSOLUTE_BASE =
  (typeof process !== "undefined" && (process.env as { NEXT_PUBLIC_BACKEND_URL?: string })?.NEXT_PUBLIC_BACKEND_URL) ||
  "http://localhost:8000/api/v1";

function buildWsUrl(token: string, conversationId: string | null): string {
  if (typeof window === "undefined") return "";
  // Prefer same-host WS (goes through Next.js rewrites to backend) so we
  // avoid browser SSL/Mixed-Content warnings and bypass CORS on WS upgrade.
  const browserScheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  const sameHost = `${browserScheme}//${window.location.host}/api/v1/chat/stream`;
  const qs = new URLSearchParams();
  qs.set("token", token);
  if (conversationId) qs.set("conversation_id", conversationId);
  const same = `${sameHost}?${qs.toString()}`;
  // Fallback to direct backend WS if rewrites don't support upgrade on
  // self-hosted. Backend URL constructed by http(s) → ws(s) prefix swap.
  try {
    const fallback = new URL(BACKEND_ABSOLUTE_BASE);
    fallback.protocol = fallback.protocol === "https:" ? "wss:" : "ws:";
    fallback.pathname = `${fallback.pathname.replace(/\/$/, "")}/chat/stream`;
    fallback.search = `?${qs.toString()}`;
    void same;
    return fallback.toString();
  } catch {
    return same;
  }
}

export function useChatStream(conversationId: string | null) {
  const accessToken = useAuthStore((s) => s.accessToken);
  const wsStatus = useChatStore((s) => s.wsStatus);
  const wsInstance = useChatStore((s) => s.wsInstance);
  const isStreaming = useChatStore((s) => s.isStreaming);
  const streamingContent = useChatStore((s) => s.streamingContent);
  const streamingMessageId = useChatStore((s) => s.streamingMessageId);
  const messages = useChatStore((s) => s.messages);
  const lastPrompt = useChatStore((s) => s.lastPrompt);

  const setWSStatus = useChatStore((s) => s.setWSStatus);
  const setWSInstance = useChatStore((s) => s.setWSInstance);
  const setIsStreaming = useChatStore((s) => s.setIsStreaming);
  const setStreamingMessageId = useChatStore((s) => s.setStreamingMessageId);
  const appendStreamingContent = useChatStore((s) => s.appendStreamingContent);
  const resetStreamingContent = useChatStore((s) => s.resetStreamingContent);
  const addMessage = useChatStore((s) => s.addMessage);
  const updateMessage = useChatStore((s) => s.updateMessage);
  const setMessages = useChatStore((s) => s.setMessages);
  const clearMessages = useChatStore((s) => s.clearMessages);
  const setLastPrompt = useChatStore((s) => s.setLastPrompt);
  const disconnect = useChatStore((s) => s.disconnect);

  const manuallyOpenRef = React.useRef(false);
  const finalizeTimerRef = React.useRef<number | null>(null);
  const connectedOnceRef = React.useRef(false);
  const isStreamingRef = React.useRef<boolean>(false);

  React.useEffect(() => {
    isStreamingRef.current = isStreaming;
  }, [isStreaming]);

  const finalizeCurrent = React.useCallback(() => {
    const state = useChatStore.getState();
    const finalContent = state.streamingContent;
    const msgId = state.streamingMessageId;
    if (msgId && finalContent != null) {
      updateMessage(msgId, { content: finalContent });
    }
    resetStreamingContent();
    setIsStreaming(false);
    isStreamingRef.current = false;
  }, [updateMessage, resetStreamingContent, setIsStreaming]);

  const scheduleFinalize = React.useCallback(() => {
    if (finalizeTimerRef.current != null) {
      window.clearTimeout(finalizeTimerRef.current);
    }
    // Treat 500ms of silence as end-of-stream in case [DONE] is missed.
    finalizeTimerRef.current = window.setTimeout(() => {
      finalizeCurrent();
      finalizeTimerRef.current = null;
    }, 500);
  }, [finalizeCurrent]);

  React.useEffect(() => {
    if (typeof window === "undefined") return;
    if (!accessToken) return;
    if (wsInstance) return;

    let cancelled = false;
    let ws: WebSocket | undefined;

    function connect() {
      try {
        const token = accessToken ?? "";
        const url = buildWsUrl(token, conversationId);
        ws = new WebSocket(url);
      } catch {
        setWSStatus("error");
        return;
      }

      setWSStatus("connecting");
      setWSInstance(ws);

      ws.onopen = () => {
        if (cancelled) return;
        setWSStatus("connected");
        connectedOnceRef.current = true;
      };

      ws.onmessage = (event: MessageEvent) => {
        if (cancelled) return;
        const raw = typeof event.data === "string" ? event.data : "";

        const content = raw;

        if (!content || content === "\n") {
          scheduleFinalize();
          return;
        }
        if (content === "[DONE]") {
          if (finalizeTimerRef.current != null) {
            window.clearTimeout(finalizeTimerRef.current);
            finalizeTimerRef.current = null;
          }
          finalizeCurrent();
          return;
        }

        if (!isStreamingRef.current) {
          const id = `m_${Date.now()}`;
          const assistantMessage: Message = {
            id,
            role: "assistant",
            content: "",
            createdAt: new Date().toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
            conversationId: conversationId ?? undefined,
          };
          addMessage(assistantMessage);
          setStreamingMessageId(id);
          setIsStreaming(true);
          isStreamingRef.current = true;
        }
        appendStreamingContent(content);
        scheduleFinalize();
      };

      ws.onerror = () => {
        if (cancelled) return;
        setWSStatus("error");
      };

      ws.onclose = () => {
        if (cancelled) return;
        setWSStatus("disconnected");
        // Finalize any pending stream on unexpected close.
        if (isStreamingRef.current) {
          try {
            finalizeCurrent();
          } catch {
            // ignore
          }
        }
        if (manuallyOpenRef.current && !cancelled) {
          window.setTimeout(connect, 1500);
        }
      };
    }

    manuallyOpenRef.current = true;
    connect();

    return () => {
      cancelled = true;
      manuallyOpenRef.current = false;
      if (finalizeTimerRef.current != null) {
        window.clearTimeout(finalizeTimerRef.current);
        finalizeTimerRef.current = null;
      }
      disconnect();
      setWSInstance(null);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken]);

  const send = React.useCallback(
    (prompt: string) => {
      if (!wsInstance || wsInstance.readyState !== WebSocket.OPEN) {
        throw new Error("WebSocket not connected");
      }
      const userMessage: Message = {
        id: `m_${Date.now()}`,
        role: "user",
        content: prompt,
        createdAt: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        conversationId: conversationId ?? undefined,
      };
      addMessage(userMessage);
      setLastPrompt(prompt);
      resetStreamingContent();
      wsInstance.send(prompt);
      isStreamingRef.current = true;
    },
    [
      wsInstance,
      conversationId,
      addMessage,
      setLastPrompt,
      resetStreamingContent,
    ]
  );

  const stop = React.useCallback(() => {
    if (finalizeTimerRef.current != null) {
      window.clearTimeout(finalizeTimerRef.current);
      finalizeTimerRef.current = null;
    }
    if (wsInstance) {
      try {
        wsInstance.send("[STOP]");
      } catch {
        // ignore
      }
    }
    const currentId = streamingMessageId;
    const finalContent = streamingContent;
    if (currentId && finalContent) {
      updateMessage(currentId, { content: finalContent });
    }
    resetStreamingContent();
    setIsStreaming(false);
    isStreamingRef.current = false;
  }, [
    wsInstance,
    streamingMessageId,
    streamingContent,
    updateMessage,
    resetStreamingContent,
    setIsStreaming,
  ]);

  const regenerate = React.useCallback(() => {
    const prompt = lastPrompt;
    if (!prompt) return;
    const lastAssistantId = [...messages]
      .reverse()
      .find((m) => m.role === "assistant")?.id;
    if (lastAssistantId) {
      updateMessage(lastAssistantId, { content: "" });
    }
    resetStreamingContent();
    if (wsInstance?.readyState === WebSocket.OPEN) {
      wsInstance.send(prompt);
      setIsStreaming(true);
      isStreamingRef.current = true;
      if (lastAssistantId) setStreamingMessageId(lastAssistantId);
      scheduleFinalize();
    }
  }, [
    lastPrompt,
    messages,
    wsInstance,
    updateMessage,
    resetStreamingContent,
    setIsStreaming,
    setStreamingMessageId,
    scheduleFinalize,
  ]);

  return {
    send,
    stop,
    regenerate,
    disconnect,
    setMessages,
    clearMessages,
    updateMessage,
    wsStatus,
    isStreaming,
    streamingContent,
    streamingMessageId,
    messages,
  };
}
