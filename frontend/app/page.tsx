"use client";

import * as React from "react";
import { AppShell } from "@/components/layout/app-shell";
import { ChatWindow } from "@/components/chat/chat-window";

export default function ChatPage() {
  return (
    <AppShell minimumRole="viewer">
      {(user) => <ChatWindow user={user} />}
    </AppShell>
  );
}
