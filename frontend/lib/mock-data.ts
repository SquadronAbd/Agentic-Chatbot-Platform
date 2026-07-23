import type {
  Conversation,
  CurrentUser,
  DailyMetric,
  KnowledgeDocument,
  ManagedUser,
  Message,
} from "./types";

export const MOCK_USER: CurrentUser = {
  id: "u_01",
  name: "Sana Raza",
  email: "sana.raza@example.com",
  role: "admin",
};

export const MOCK_MESSAGES: Message[] = [
  {
    id: "m1",
    role: "user",
    content: "Summarize the Q3 churn drivers from the uploaded report.",
    createdAt: "09:12",
  },
  {
    id: "m2",
    role: "assistant",
    content:
      "Three drivers stand out: pricing friction on the annual plan, a support-response regression in week 6, and a competitor launch in the SMB segment. Want the breakdown by region?",
    tokens: 187,
    createdAt: "09:12",
  },
  {
    id: "m3",
    role: "user",
    content: "Yes, region breakdown please, and flag anything above 5% churn.",
    createdAt: "09:13",
  },
];

export const MOCK_CONVERSATIONS: Conversation[] = [
  { id: "c1", title: "Q3 churn analysis", updatedAt: "2 min ago", messageCount: 12 },
  { id: "c2", title: "Onboarding flow rewrite", updatedAt: "1 hr ago", messageCount: 34 },
  { id: "c3", title: "Vendor contract review", updatedAt: "Yesterday", messageCount: 8 },
  { id: "c4", title: "RAG eval harness ideas", updatedAt: "2 days ago", messageCount: 21 },
];

export const MOCK_DOCUMENTS: KnowledgeDocument[] = [
  { id: "d1", filename: "q3-board-deck.pdf", status: "ready", chunkCount: 142, uploadedAt: "Jul 18", sizeKb: 3420 },
  { id: "d2", filename: "support-transcripts-week6.docx", status: "ready", chunkCount: 88, uploadedAt: "Jul 19", sizeKb: 980 },
  { id: "d3", filename: "vendor-msa-draft.pdf", status: "processing", chunkCount: 0, uploadedAt: "Jul 22", sizeKb: 210 },
  { id: "d4", filename: "legacy-pricing-sheet.csv", status: "error", chunkCount: 0, uploadedAt: "Jul 20", sizeKb: 44 },
];

export const MOCK_DAILY_METRICS: DailyMetric[] = [
  { date: "Jul 17", messages: 812, activeUsers: 64, avgLatencyMs: 940 },
  { date: "Jul 18", messages: 940, activeUsers: 71, avgLatencyMs: 905 },
  { date: "Jul 19", messages: 1102, activeUsers: 78, avgLatencyMs: 1020 },
  { date: "Jul 20", messages: 860, activeUsers: 59, avgLatencyMs: 880 },
  { date: "Jul 21", messages: 1210, activeUsers: 88, avgLatencyMs: 960 },
  { date: "Jul 22", messages: 1340, activeUsers: 95, avgLatencyMs: 875 },
  { date: "Jul 23", messages: 990, activeUsers: 80, avgLatencyMs: 845 },
];

export const MOCK_USERS: ManagedUser[] = [
  { id: "u1", name: "Sana Raza", email: "sana.raza@example.com", role: "admin", lastActive: "Just now" },
  { id: "u2", name: "Imran Qureshi", email: "imran.q@example.com", role: "manager", lastActive: "12 min ago" },
  { id: "u3", name: "Ayesha Malik", email: "ayesha.m@example.com", role: "agent", lastActive: "1 hr ago" },
  { id: "u4", name: "Bilal Ahmed", email: "bilal.a@example.com", role: "agent", lastActive: "3 hr ago" },
  { id: "u5", name: "Hira Shah", email: "hira.shah@example.com", role: "viewer", lastActive: "1 day ago" },
];
