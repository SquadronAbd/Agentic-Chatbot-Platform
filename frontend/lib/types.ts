export type Role = "admin" | "manager" | "agent" | "viewer";

export interface CurrentUser {
  id: string;
  name: string;
  email: string;
  role: Role;
  isActive?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  tokens?: number;
  createdAt: string;
  conversationId?: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  updatedAt: string;
  createdAt: string;
  messageCount?: number;
  userId?: string;
}

export type DocumentStatus = "processing" | "ready" | "error";

export interface KnowledgeDocument {
  id: string;
  filename: string;
  status: DocumentStatus;
  chunkCount: number;
  uploadedAt: string;
  sizeKb?: number;
  ownerId?: string;
  contentType?: string;
  userId?: string;
}

export interface DailyMetric {
  date: string;
  messages: number;
  activeUsers: number;
  avgLatencyMs: number;
  conversations?: number;
  apiCalls?: number;
}

export interface AnalyticsSummary {
  totalMessages: number;
  totalActiveUsers: number;
  totalConversations: number;
  totalDocuments: number;
  totalApiUsage: number;
  avgLatencyMs: number;
}

export interface ManagedUser {
  id: string;
  name: string;
  email: string;
  role: Role;
  lastActive?: string;
  createdAt?: string;
  isActive?: boolean;
}

export interface ApiKey {
  id: string;
  label: string | null;
  name: string | null;
  prefix?: string;
  createdAt: string;
  lastUsed?: string | null;
  key?: string;
}

export interface CreateApiKeyRequest {
  label?: string;
}

export interface CreateApiKeyResponse {
  id: string;
  key: string;
  label: string | null;
  createdAt: string;
}

export interface AgentTool {
  id: string;
  name: string;
  description: string | null;
  enabled: boolean;
  config?: Record<string, unknown> | null;
  type?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface CreateAgentToolRequest {
  name: string;
  description?: string;
  config?: Record<string, unknown>;
  enabled?: boolean;
}

export interface UpdateAgentToolRequest {
  description?: string;
  config?: Record<string, unknown>;
  enabled?: boolean;
}

export interface CreateUserRequest {
  email: string;
  password: string;
  fullName?: string;
  name?: string;
  role: Role;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  access_token?: string;
  refresh_token?: string;
}

export interface LoginResponse extends AuthTokens {
  tokenType?: string;
}

export interface RegisterResponse {
  user: {
    id: string;
    email: string;
    fullName?: string | null;
    full_name?: string | null;
    name?: string | null;
    role: Role;
    isActive?: boolean;
    createdAt?: string;
  };
  accessToken: string;
  tokenType?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface CreateConversationRequest {
  title?: string;
}

export interface CreateMessageRequest {
  role: "user" | "assistant";
  content: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export const ROLE_RANK: Record<Role, number> = {
  viewer: 0,
  agent: 1,
  manager: 2,
  admin: 3,
};

export function hasAccess(userRole: Role, minimumRole: Role): boolean {
  return ROLE_RANK[userRole] >= ROLE_RANK[minimumRole];
}
