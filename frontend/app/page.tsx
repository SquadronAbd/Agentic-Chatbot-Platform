import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { ChatWindow } from "@/components/chat/chat-window";
import { MOCK_USER } from "@/lib/mock-data";

export default function ChatPage() {
  return (
    <AppShell user={MOCK_USER}>
      <Topbar title="FinRAG" user={MOCK_USER} />
      <ChatWindow initialMessages={[]} />
    </AppShell>
  );
}
