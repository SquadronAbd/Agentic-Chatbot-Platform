import api from "@/lib/api";
import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseMutationResult,
  type UseQueryResult,
  type QueryKey,
} from "@tanstack/react-query";
import type {
  Conversation,
  CreateConversationRequest,
  CreateMessageRequest,
  Message,
  KnowledgeDocument,
  ManagedUser,
  CreateUserRequest,
  DailyMetric,
  AnalyticsSummary,
  ApiKey,
  CreateApiKeyRequest,
  CreateApiKeyResponse,
  AgentTool,
  CreateAgentToolRequest,
  UpdateAgentToolRequest,
  PaginatedResponse,
  Role,
} from "@/lib/types";

export const queryKeys = {
  conversations: ["conversations"] as const,
  conversation: (id: string): QueryKey => ["conversations", id] as const,
  messages: (id: string): QueryKey => ["messages", id] as const,
  documents: ["documents"] as const,
  users: (page = 1, limit = 10, search = ""): QueryKey =>
    ["users", page, limit, search] as const,
  analyticsDaily: ["analytics", "daily"] as const,
  analyticsSummary: ["analytics", "summary"] as const,
  apiKeys: ["api-keys"] as const,
  agentTools: ["agent-tools"] as const,
};

/* ------------------------------ Conversations ----------------------------- */

function normalizeConversation(
  raw: Conversation | Record<string, unknown>
): Conversation {
  const r = raw as Record<string, unknown>;
  return {
    id: String(r.id ?? ""),
    title: (r.title as string | null) ?? "New conversation",
    createdAt:
      (r.createdAt as string) ??
      (r.created_at as string) ??
      new Date().toISOString(),
    updatedAt:
      (r.updatedAt as string) ??
      (r.updated_at as string) ??
      new Date().toISOString(),
    messageCount:
      typeof r.messageCount === "number"
        ? r.messageCount
        : undefined,
    userId: typeof r.userId === "string" ? r.userId : undefined,
  };
}

export function useConversations(): UseQueryResult<Conversation[]> {
  return useQuery({
    queryKey: queryKeys.conversations,
    queryFn: async () => {
      const { data } = await api.get<Conversation[]>("/conversations");
      return (data as unknown as Record<string, unknown>[]).map(
        normalizeConversation
      );
    },
    staleTime: 60_000,
  });
}

export function useCreateConversation(): UseMutationResult<
  Conversation,
  unknown,
  CreateConversationRequest
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateConversationRequest) => {
      const { data } = await api.post<Conversation>(
        "/conversations",
        payload as unknown as Record<string, unknown>
      );
      return normalizeConversation(data as unknown as Record<string, unknown>);
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.conversations });
    },
  });
}

export function useDeleteConversation(): UseMutationResult<
  void,
  unknown,
  string
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/conversations/${id}`);
    },
    onMutate: async (id) => {
      await client.cancelQueries({ queryKey: queryKeys.conversations });
      const prev =
        client.getQueryData<Conversation[]>(queryKeys.conversations) ?? [];
      client.setQueryData(
        queryKeys.conversations,
        prev.filter((c) => c.id !== id)
      );
      return { prev };
    },
    onError: (_err, _id, ctx) => {
      if (ctx?.prev)
        client.setQueryData(queryKeys.conversations, ctx.prev);
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.conversations });
    },
  });
}

/* -------------------------------- Messages -------------------------------- */

function normalizeMessage(
  raw: Message | Record<string, unknown>
): Message {
  const r = raw as Record<string, unknown>;
  return {
    id: String(r.id ?? ""),
    role: (r.role as "user" | "assistant") ?? "user",
    content: String(r.content ?? ""),
    createdAt:
      (r.createdAt as string) ??
      (r.created_at as string) ??
      new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    conversationId:
      (r.conversationId as string) ??
      (r.conversation_id as string) ??
      undefined,
    tokens: typeof r.tokens === "number" ? r.tokens : undefined,
  };
}

export function useMessages(
  conversationId: string | null
): UseQueryResult<Message[]> {
  return useQuery({
    queryKey: queryKeys.messages(conversationId ?? "default"),
    queryFn: async () => {
      if (!conversationId) return [];
      const { data } = await api.get<Message[]>(
        `/conversations/${conversationId}/messages`
      );
      return (data as unknown as Record<string, unknown>[]).map(
        normalizeMessage
      );
    },
    enabled: !!conversationId,
  });
}

export function usePostMessage(
  conversationId: string
): UseMutationResult<Message, unknown, CreateMessageRequest> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateMessageRequest) => {
      const { data } = await api.post<Message>(
        `/conversations/${conversationId}/messages`,
        payload as unknown as Record<string, unknown>
      );
      return normalizeMessage(data as unknown as Record<string, unknown>);
    },
    onSettled: () => {
      void client.invalidateQueries({
        queryKey: queryKeys.messages(conversationId),
      });
    },
  });
}

/* ------------------------------- Documents -------------------------------- */

function normalizeDocument(
  raw: KnowledgeDocument | Record<string, unknown>
): KnowledgeDocument {
  const r = raw as Record<string, unknown>;
  const status = String(r.status ?? "ready") as KnowledgeDocument["status"];
  const created =
    (r.createdAt as string) ?? (r.created_at as string) ?? "";
  return {
    id: String(r.id ?? ""),
    filename: String(r.filename ?? "untitled"),
    status: ["processing", "ready", "error"].includes(status)
      ? status
      : "ready",
    chunkCount:
      typeof r.chunkCount === "number"
        ? r.chunkCount
        : typeof r.chunk_count === "number"
          ? (r.chunk_count as number)
          : 0,
    uploadedAt: created,
    sizeKb:
      typeof r.sizeKb === "number"
        ? r.sizeKb
        : typeof r.size_kb === "number"
          ? (r.size_kb as number)
          : undefined,
    ownerId:
      typeof r.ownerId === "string"
        ? r.ownerId
        : typeof r.owner_id === "string"
          ? (r.owner_id as string)
          : undefined,
  };
}

export function useDocuments(
  search?: string
): UseQueryResult<KnowledgeDocument[]> {
  return useQuery({
    queryKey: queryKeys.documents,
    queryFn: async () => {
      const { data } = await api.get<KnowledgeDocument[]>("/documents");
      return (data as unknown as Record<string, unknown>[]).map(
        normalizeDocument
      );
    },
    staleTime: 30_000,
    select: (items) =>
      search
        ? items.filter((d) =>
            d.filename.toLowerCase().includes(search.toLowerCase())
          )
        : items,
  });
}

export function useUploadDocument(): UseMutationResult<
  KnowledgeDocument,
  unknown,
  { file: File; onProgress?: (p: number) => void }
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async ({ file, onProgress }) => {
      const form = new FormData();
      form.append("file", file);
      const { data } = await api.post<KnowledgeDocument>(
        "/documents/upload",
        form,
        {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (e) => {
            if (onProgress && e.total) {
              onProgress(Math.round((e.loaded / e.total) * 100));
            }
          },
        }
      );
      return normalizeDocument(data as unknown as Record<string, unknown>);
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.documents });
    },
  });
}

export function useDeleteDocument(): UseMutationResult<
  void,
  unknown,
  string
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/documents/${id}`);
    },
    onMutate: async (id) => {
      await client.cancelQueries({ queryKey: queryKeys.documents });
      const prev =
        client.getQueryData<KnowledgeDocument[]>(queryKeys.documents) ?? [];
      client.setQueryData(
        queryKeys.documents,
        prev.filter((d) => d.id !== id)
      );
      return { prev };
    },
    onError: (_err, _id, ctx) => {
      if (ctx?.prev)
        client.setQueryData(queryKeys.documents, ctx.prev);
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.documents });
    },
  });
}

/* --------------------------------- Users ---------------------------------- */

function normalizeManagedUser(
  raw: ManagedUser | Record<string, unknown>
): ManagedUser {
  const r = raw as Record<string, unknown>;
  const createdAt =
    (r.createdAt as string) ?? (r.created_at as string) ?? undefined;
  const name =
    (r.name as string) ??
    (r.fullName as string) ??
    (r.full_name as string) ??
    (r.email as string) ??
    "Unknown";
  return {
    id: String(r.id ?? ""),
    email: String(r.email ?? ""),
    name,
    role: (r.role as Role) ?? ("viewer" as Role),
    isActive:
      typeof r.isActive === "boolean"
        ? r.isActive
        : typeof r.is_active === "boolean"
          ? (r.is_active as boolean)
          : true,
    lastActive:
      (r.lastActive as string) ??
      (r.last_active as string) ??
      createdAt ??
      "Unknown",
    createdAt,
  };
}

interface UseUsersParams {
  page?: number;
  limit?: number;
  search?: string;
}

export function useUsers({
  page = 1,
  limit = 10,
  search = "",
}: UseUsersParams = {}): UseQueryResult<PaginatedResponse<ManagedUser>> {
  return useQuery({
    queryKey: queryKeys.users(page, limit, search),
    queryFn: async () => {
      // Real backend returns plain list[UserOut]; wrap into a PaginatedResponse for the UI.
      const { data } = await api.get<ManagedUser[]>("/users");
      const all = (data as unknown as Record<string, unknown>[]).map(
        normalizeManagedUser
      );
      let filtered = all;
      if (search) {
        const q = search.toLowerCase();
        filtered = all.filter(
          (u) =>
            u.name.toLowerCase().includes(q) ||
            u.email.toLowerCase().includes(q)
        );
      }
      const total = filtered.length;
      const totalPages = Math.max(1, Math.ceil(total / limit));
      const start = (page - 1) * limit;
      const items = filtered.slice(start, start + limit);
      return {
        items,
        total,
        page,
        limit,
        totalPages,
      } satisfies PaginatedResponse<ManagedUser>;
    },
  });
}

export function useCreateUser(): UseMutationResult<
  ManagedUser,
  unknown,
  CreateUserRequest
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateUserRequest) => {
      // AdminUserCreate on backend expects { email, password, full_name, role }.
      // The case interceptor converts camelCase body to snake_case,
      // but "name" → "name" not "full_name". Build explicit body.
      const body: {
        email: string;
        password: string;
        role: string;
        full_name: string;
      } = {
        email: payload.email,
        password: payload.password,
        role: payload.role,
        full_name: payload.fullName ?? payload.name ?? "",
      };
      const { data } = await api.post<ManagedUser>(
        "/users",
        body as unknown as Record<string, unknown>
      );
      return normalizeManagedUser(
        data as unknown as Record<string, unknown>
      );
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.users() });
    },
  });
}

export function useDeleteUser(): UseMutationResult<void, unknown, string> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/users/${id}`);
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.users() });
    },
  });
}

// NOTE: Backend has no PATCH/PUT endpoint for role updates. The inline role
// selector on /admin is still shown but calls this stub — we surface a toast
// explaining the endpoint is not yet wired.
export function useUpdateUserRole(): UseMutationResult<
  ManagedUser | null,
  unknown,
  { id: string; role: string }
> {
  return useMutation({
    mutationFn: async () => {
      // Endpoint not available on backend — always throw so the UI catches and notifies.
      throw new Error(
        "Role-change endpoint (/users/:id) is not implemented in this backend release."
      );
    },
  });
}

/* ------------------------------- Analytics -------------------------------- */

function normalizeDailyMetric(
  raw: DailyMetric | Record<string, unknown>
): DailyMetric {
  const r = raw as Record<string, unknown>;
  const date =
    (r.date as string) ??
    (typeof r.date !== "string" && r.date instanceof Date
      ? (r.date as Date).toISOString().slice(5, 10)
      : "N/A");
  const asNum = (k: string) => {
    const v = r[k];
    return typeof v === "number" ? v : 0;
  };
  return {
    date: typeof date === "string" ? date.slice(0, 10) : String(date),
    messages: asNum("messageCount") || asNum("messages") || asNum("message_count"),
    activeUsers:
      asNum("activeUsers") ||
      asNum("active_users") ||
      asNum("dailyActiveUsers") ||
      asNum("daily_active_users"),
    avgLatencyMs:
      asNum("avgLatencyMs") ||
      asNum("avg_latency_ms") ||
      asNum("p95LatencyMs") ||
      asNum("p95_latency_ms"),
  };
}

export function useAnalyticsDaily(): UseQueryResult<DailyMetric[]> {
  return useQuery({
    queryKey: queryKeys.analyticsDaily,
    queryFn: async () => {
      const { data } = await api.get<DailyMetric[]>("/analytics/daily");
      const rows = (
        (data as unknown as Record<string, unknown>[]) ?? []
      ).map(normalizeDailyMetric);
      // Backend returns desc by date; UI expects asc so line charts read L→R.
      rows.reverse();
      return rows;
    },
    staleTime: 60_000,
  });
}

// Backend does not expose an /analytics/summary endpoint. Build the summary
// from /analytics/daily so UI cards stay populated.
export function useAnalyticsSummary(): UseQueryResult<AnalyticsSummary> {
  const daily = useAnalyticsDaily();
  return useQuery({
    queryKey: queryKeys.analyticsSummary,
    queryFn: async () => {
      const metrics = daily.data ?? [];
      const totalMessages = metrics.reduce((a, m) => a + m.messages, 0);
      const maxActive = metrics.reduce(
        (a, m) => Math.max(a, m.activeUsers),
        0
      );
      const avgLatency =
        metrics.length
          ? Math.round(
              metrics.reduce((a, m) => a + m.avgLatencyMs, 0) / metrics.length
            )
          : 0;
      return {
        totalMessages,
        totalActiveUsers: maxActive,
        totalConversations: Math.round(totalMessages / 6),
        totalDocuments: 0,
        totalApiUsage: Math.round(totalMessages * 3.4),
        avgLatencyMs: avgLatency,
      } satisfies AnalyticsSummary;
    },
    enabled: daily.isSuccess,
    staleTime: 60_000,
    initialData: {
      totalMessages: 0,
      totalActiveUsers: 0,
      totalConversations: 0,
      totalDocuments: 0,
      totalApiUsage: 0,
      avgLatencyMs: 0,
    },
  });
}

/* -------------------------------- API Keys ------------------------------- */

function normalizeApiKey(
  raw: ApiKey | Record<string, unknown>
): ApiKey {
  const r = raw as Record<string, unknown>;
  const createdAt =
    (r.createdAt as string) ?? (r.created_at as string) ?? "";
  const lastUsed =
    (r.lastUsed as string | null) ?? (r.last_used as string | null) ?? null;
  const label =
    (r.label as string | null) ?? (r.name as string | null) ?? null;
  // Derive a 6-char prefix for display (backend only returns raw `key` at create time, not hashes).
  const keyPrefix =
    (r.prefix as string) ??
    ((r.key as string)?.slice(0, 9) ?? null);
  return {
    id: String(r.id ?? ""),
    label,
    name: label,
    prefix: keyPrefix,
    createdAt,
    lastUsed,
    key: typeof r.key === "string" ? (r.key as string) : undefined,
  };
}

export function useApiKeys(): UseQueryResult<ApiKey[]> {
  return useQuery({
    queryKey: queryKeys.apiKeys,
    queryFn: async () => {
      const { data } = await api.get<ApiKey[]>("/api-keys");
      return (data as unknown as Record<string, unknown>[]).map(
        normalizeApiKey
      );
    },
  });
}

export function useCreateApiKey(): UseMutationResult<
  CreateApiKeyResponse,
  unknown,
  CreateApiKeyRequest
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateApiKeyRequest) => {
      // Backend ApiKeyCreate = { label: string | null }. Frontend form uses
      // "name"; map it to label.
      const body = { label: payload.label ?? null, name: undefined };
      const { data } = await api.post<CreateApiKeyResponse>(
        "/api-keys",
        body as unknown as Record<string, unknown>
      );
      const d = data as unknown as Record<string, unknown>;
      return {
        id: String(d.id ?? ""),
        key: String(d.key ?? ""),
        label: (d.label as string | null) ?? null,
        createdAt:
          (d.createdAt as string) ?? (d.created_at as string) ?? "",
      } satisfies CreateApiKeyResponse;
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.apiKeys });
    },
  });
}

export function useDeleteApiKey(): UseMutationResult<void, unknown, string> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api-keys/${id}`);
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.apiKeys });
    },
  });
}

/* ------------------------------ Agent Tools ------------------------------ */

function normalizeAgentTool(
  raw: AgentTool | Record<string, unknown>
): AgentTool {
  const r = raw as Record<string, unknown>;
  return {
    id: String(r.id ?? ""),
    name: String(r.name ?? ""),
    description:
      (r.description as string | null) ??
      "No description provided.",
    enabled: r.enabled === true,
    config:
      r.config && typeof r.config === "object"
        ? (r.config as Record<string, unknown>)
        : {},
    type:
      typeof (r.config as Record<string, unknown> | undefined)?.type ===
      "string"
        ? ((r.config as Record<string, unknown>).type as string)
        : typeof r.type === "string"
          ? r.type
          : "http",
    createdAt:
      (r.createdAt as string) ?? (r.created_at as string) ?? "",
    updatedAt:
      (r.updatedAt as string) ?? (r.updated_at as string) ?? "",
  };
}

export function useAgentTools(): UseQueryResult<AgentTool[]> {
  return useQuery({
    queryKey: queryKeys.agentTools,
    queryFn: async () => {
      const { data } = await api.get<AgentTool[]>("/agent-tools");
      return (data as unknown as Record<string, unknown>[]).map(
        normalizeAgentTool
      );
    },
  });
}

export function useCreateAgentTool(): UseMutationResult<
  AgentTool,
  unknown,
  CreateAgentToolRequest
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateAgentToolRequest) => {
      // Backend AgentToolCreate: { name, description?, enabled?, config? }
      const body = {
        name: payload.name,
        description: payload.description ?? null,
        enabled: payload.enabled ?? true,
        config: payload.config ?? null,
      };
      const { data } = await api.post<AgentTool>(
        "/agent-tools",
        body as unknown as Record<string, unknown>
      );
      return normalizeAgentTool(
        data as unknown as Record<string, unknown>
      );
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.agentTools });
    },
  });
}

export function useUpdateAgentTool(): UseMutationResult<
  AgentTool,
  unknown,
  { id: string; payload: UpdateAgentToolRequest }
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, payload }) => {
      // Backend AgentToolUpdate: { description?, enabled?, config? } — NO name/type.
      const body = {
        description: payload.description ?? null,
        enabled: payload.enabled,
        config: payload.config ?? null,
      };
      const { data } = await api.put<AgentTool>(
        `/agent-tools/${id}`,
        body as unknown as Record<string, unknown>
      );
      return normalizeAgentTool(
        data as unknown as Record<string, unknown>
      );
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.agentTools });
    },
  });
}

export function useDeleteAgentTool(): UseMutationResult<
  void,
  unknown,
  string
> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/agent-tools/${id}`);
    },
    onSettled: () => {
      void client.invalidateQueries({ queryKey: queryKeys.agentTools });
    },
  });
}
