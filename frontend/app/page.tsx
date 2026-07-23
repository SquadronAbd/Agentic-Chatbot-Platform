import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { ChatWindow } from "@/components/chat/chat-window";
import { MOCK_MESSAGES, MOCK_USER } from "@/lib/mock-data";

export default function ChatPage() {
  return (
    <AppShell user={MOCK_USER}>
      <Topbar title="Chat" subtitle="Q3 churn analysis" user={MOCK_USER} />
      <ChatWindow initialMessages={MOCK_MESSAGES} />
    </AppShell>
  );
}
