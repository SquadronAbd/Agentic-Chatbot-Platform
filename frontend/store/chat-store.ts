"use client";

import { create } from "zustand";
import type { Message } from "@/lib/types";

type WSStatus = "disconnected" | "connecting" | "connected" | "error";

interface ChatState {
  wsStatus: WSStatus;
  wsInstance: WebSocket | null;
  isStreaming: boolean;
  streamingMessageId: string | null;
  streamingContent: string;
  messages: Message[];
  lastPrompt: string | null;

  setWSStatus: (s: WSStatus) => void;
  setWSInstance: (ws: WebSocket | null) => void;
  setIsStreaming: (v: boolean) => void;
  setStreamingMessageId: (id: string | null) => void;
  appendStreamingContent: (chunk: string) => void;
  resetStreamingContent: () => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, patch: Partial<Message>) => void;
  removeMessage: (id: string) => void;
  clearMessages: () => void;
  setLastPrompt: (prompt: string | null) => void;
  disconnect: () => void;
}

export const useChatStore = create<ChatState>()((set, get) => ({
  wsStatus: "disconnected",
  wsInstance: null,
  isStreaming: false,
  streamingMessageId: null,
  streamingContent: "",
  messages: [],
  lastPrompt: null,

  setWSStatus: (s) => set({ wsStatus: s }),
  setWSInstance: (ws) => {
    const prev = get().wsInstance;
    if (prev && prev !== ws) {
      try {
        prev.close();
      } catch {
        // ignore
      }
    }
    set({ wsInstance: ws });
  },
  setIsStreaming: (v) => set({ isStreaming: v }),
  setStreamingMessageId: (id) => set({ streamingMessageId: id }),
  appendStreamingContent: (chunk) =>
    set({ streamingContent: get().streamingContent + chunk }),
  resetStreamingContent: () => set({ streamingContent: "", streamingMessageId: null }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set({ messages: [...get().messages, message] }),
  updateMessage: (id, patch) =>
    set({
      messages: get().messages.map((m) => (m.id === id ? { ...m, ...patch } : m)),
    }),
  removeMessage: (id) =>
    set({ messages: get().messages.filter((m) => m.id !== id) }),
  clearMessages: () => set({ messages: [], streamingContent: "", streamingMessageId: null, isStreaming: false }),
  setLastPrompt: (prompt) => set({ lastPrompt: prompt }),
  disconnect: () => {
    const ws = get().wsInstance;
    if (ws) {
      try {
        ws.close();
      } catch {
        // ignore
      }
    }
    set({ wsInstance: null, wsStatus: "disconnected", isStreaming: false });
  },
}));
