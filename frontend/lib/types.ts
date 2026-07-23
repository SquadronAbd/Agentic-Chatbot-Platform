export type Role = "admin" | "manager" | "agent" | "viewer";

export interface CurrentUser {
  id: string;
  name: string;
  email: string;
  role: Role;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  tokens?: number;
  createdAt: string;
}

export interface Conversation {
  id: string;
  title: string;
  updatedAt: string;
  messageCount: number;
}

export type DocumentStatus = "processing" | "ready" | "error";

export interface KnowledgeDocument {
  id: string;
  filename: string;
  status: DocumentStatus;
  chunkCount: number;
  uploadedAt: string;
  sizeKb: number;
}

export interface DailyMetric {
  date: string;
  messages: number;
  activeUsers: number;
  avgLatencyMs: number;
}

export interface ManagedUser {
  id: string;
  name: string;
  email: string;
  role: Role;
  lastActive: string;
}

/** Ordered lowest -> highest privilege, used for "Role+" access checks. */
export const ROLE_RANK: Record<Role, number> = {
  viewer: 0,
  agent: 1,
  manager: 2,
  admin: 3,
};

export function hasAccess(userRole: Role, minimumRole: Role): boolean {
  return ROLE_RANK[userRole] >= ROLE_RANK[minimumRole];
}
