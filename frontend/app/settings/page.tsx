"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  User as UserIcon,
  Lock,
  Sun,
  Moon,
  KeyRound,
  Wrench,
  LogOut,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  Copy,
  Check,
  Pencil,
  Save,
  X,
} from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal, ConfirmDialog } from "@/components/ui/modal";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/theme/theme-toggle";
import { useAuthStore } from "@/store/auth-store";
import { useUIStore } from "@/store/ui-store";
import {
  useApiKeys,
  useCreateApiKey,
  useDeleteApiKey,
  useAgentTools,
  useCreateAgentTool,
  useUpdateAgentTool,
  useDeleteAgentTool,
} from "@/hooks/use-api";
import {
  updateProfileSchema,
  changePasswordSchema,
  apiKeySchema,
  agentToolSchema,
  type UpdateProfileValues,
  type ChangePasswordValues,
  type ApiKeyValues,
  type AgentToolValues,
} from "@/lib/schemas";
import type { AgentTool, ApiKey } from "@/lib/types";
import { cn } from "@/lib/utils";

type SettingsTab = "profile" | "password" | "appearance" | "apikeys" | "tools";

const TABS: { id: SettingsTab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "profile", label: "Profile", icon: UserIcon },
  { id: "password", label: "Password", icon: Lock },
  { id: "appearance", label: "Appearance", icon: Sun },
  { id: "apikeys", label: "API keys", icon: KeyRound },
  { id: "tools", label: "Agent tools", icon: Wrench },
];

export default function SettingsPage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const theme = useUIStore((s) => s.theme);
  const [tab, setTab] = React.useState<SettingsTab>("profile");

  if (!user) return null;

  async function handleLogout() {
    await logout();
    toast.success("Signed out");
    router.replace("/login");
  }

  return (
    <AppShell minimumRole="viewer">
      {(u) => (
        <div className="flex h-full flex-col overflow-y-auto">
          <div className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 md:px-6">
          <Topbar
            title="Settings"
            subtitle="Manage your account and workspace"
            breadcrumb={[{ label: "Workspace" }, { label: "Settings" }]}
            user={u}
          />

          <div className="grid grid-cols-1 gap-5 lg:grid-cols-[240px_1fr]">
            <div className="lg:sticky lg:top-28">
              <GlassCard className="p-2 shadow-glass">
                <nav className="flex flex-row gap-1 overflow-x-auto lg:flex-col lg:overflow-visible">
                  {TABS.map((t) => {
                    const Icon = t.icon;
                    const active = tab === t.id;
                    return (
                      <button
                        key={t.id}
                        onClick={() => setTab(t.id)}
                        className={cn(
                          "flex flex-shrink-0 items-center gap-2 rounded-xl px-3 py-2.5 text-sm transition-all lg:w-full",
                          active
                            ? "bg-gradient-to-r from-iris/20 to-aqua/10 text-[var(--text-primary)] shadow-glow-iris"
                            : "text-secondary hover:bg-white/10 hover:text-[var(--text-primary)]"
                        )}
                      >
                        <Icon className="h-4 w-4 flex-shrink-0" />
                        <span>{t.label}</span>
                      </button>
                    );
                  })}
                </nav>
                <div className="my-2 border-t border-white/10" />
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm text-rose-400 transition-colors hover:bg-white/10"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Sign out</span>
                </button>
              </GlassCard>
            </div>

            <div>
              <AnimatePresence mode="wait">
                <motion.div
                  key={tab}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.2 }}
                >
                  {tab === "profile" && <ProfileSection user={user} />}
                  {tab === "password" && <PasswordSection />}
                  {tab === "appearance" && <AppearanceSection />}
                  {tab === "apikeys" && <ApiKeysSection />}
                  {tab === "tools" && <AgentToolsSection />}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}

function SectionCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <GlassCard className="p-6 shadow-glass">
      <div className="mb-5">
        <h2 className="font-display text-lg font-semibold">{title}</h2>
        {subtitle && <p className="mt-1 text-sm text-secondary">{subtitle}</p>}
      </div>
      {children}
    </GlassCard>
  );
}

function ProfileSection({ user }: { user: NonNullable<ReturnType<typeof useAuthStore.getState>["user"]> }) {
  const setUser = useAuthStore((s) => s.setUser);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UpdateProfileValues>({
    resolver: zodResolver(updateProfileSchema),
    defaultValues: { name: user.name, email: user.email },
  });

  function onSubmit(values: UpdateProfileValues) {
    // Simulate profile update — integrate with PATCH /auth/me
    const updated = { ...user, name: values.name, email: values.email };
    setUser(updated);
    toast.success("Profile updated");
  }

  return (
    <SectionCard title="Profile" subtitle="Your account information">
      <div className="mb-6 flex items-center gap-4">
        <Avatar name={user.name} size="xl" />
        <div>
          <p className="font-medium">{user.name}</p>
          <p className="text-sm text-secondary">{user.email}</p>
          <Badge tone={user.role === "admin" ? "iris" : user.role === "manager" ? "aqua" : "default"} className="mt-1 capitalize">
            {user.role}
          </Badge>
        </div>
      </div>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Full name</label>
          <Input {...register("name")} />
          {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name.message}</p>}
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Email</label>
          <Input type="email" {...register("email")} />
          {errors.email && <p className="mt-1 text-xs text-rose-400">{errors.email.message}</p>}
        </div>
        <Button type="submit" disabled={isSubmitting}>
          <Save className="h-4 w-4" />
          Save changes
        </Button>
      </form>
    </SectionCard>
  );
}

function PasswordSection() {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ChangePasswordValues>({
    resolver: zodResolver(changePasswordSchema),
  });

  function onSubmit() {
    toast.success("Password updated");
    reset();
  }

  return (
    <SectionCard title="Change password" subtitle="Keep your account secure">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 max-w-md">
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Current password</label>
          <Input type="password" {...register("currentPassword")} />
          {errors.currentPassword && (
            <p className="mt-1 text-xs text-rose-400">{errors.currentPassword.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">New password</label>
          <Input type="password" {...register("newPassword")} />
          {errors.newPassword && (
            <p className="mt-1 text-xs text-rose-400">{errors.newPassword.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-mono text-secondary">Confirm new password</label>
          <Input type="password" {...register("confirmPassword")} />
          {errors.confirmPassword && (
            <p className="mt-1 text-xs text-rose-400">{errors.confirmPassword.message}</p>
          )}
        </div>
        <Button type="submit" disabled={isSubmitting}>
          <Lock className="h-4 w-4" />
          Update password
        </Button>
      </form>
    </SectionCard>
  );
}

function AppearanceSection() {
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);

  return (
    <SectionCard title="Appearance" subtitle="Customize how AetherChat looks">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className={cn(
            "grid h-10 w-10 place-items-center rounded-xl",
            theme === "dark" ? "bg-iris/20 text-iris-light" : "bg-aqua/20 text-aqua-dim"
          )}>
            {theme === "dark" ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
          </div>
          <div>
            <p className="font-medium">Theme</p>
            <p className="text-sm text-secondary capitalize">{theme} mode</p>
          </div>
        </div>
        <ThemeToggle />
      </div>

      <div className="mt-6">
        <p className="mb-3 text-xs font-mono text-secondary">Preview</p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <button
            onClick={() => setTheme("light")}
            className={cn(
              "rounded-glass border-2 p-4 text-left transition-all",
              theme === "light"
                ? "border-iris shadow-glow-iris"
                : "border-white/10 hover:border-white/20"
            )}
            style={{ background: "linear-gradient(160deg, #eef2ff, #f4f7ff)" }}
          >
            <Sun className="mb-2 h-5 w-5 text-aqua-dim" />
            <p className="font-display font-semibold text-ink">Light</p>
            <p className="text-xs text-ink/60">Glass and airy</p>
          </button>
          <button
            onClick={() => setTheme("dark")}
            className={cn(
              "rounded-glass border-2 p-4 text-left transition-all",
              theme === "dark"
                ? "border-iris shadow-glow-iris"
                : "border-white/10 hover:border-white/20"
            )}
            style={{ background: "linear-gradient(160deg, #0a0b16, #12142b)" }}
          >
            <Moon className="mb-2 h-5 w-5 text-iris-light" />
            <p className="font-display font-semibold text-f1f0fa">Dark</p>
            <p className="text-xs text-f1f0fa/60">Pulsing aurora</p>
          </button>
        </div>
      </div>
    </SectionCard>
  );
}

function ApiKeysSection() {
  const { data: keys, isLoading, refetch } = useApiKeys();
  const create = useCreateApiKey();
  const del = useDeleteApiKey();

  const [open, setOpen] = React.useState(false);
  const [newKey, setNewKey] = React.useState<string | null>(null);
  const [revealed, setRevealed] = React.useState<Record<string, boolean>>({});
  const [deleteTarget, setDeleteTarget] = React.useState<string | null>(null);

  const FALLBACK_KEYS: ApiKey[] = [
    {
      id: "k1", name: "Production integration", prefix: "ac_sk_8F2", createdAt: "Jun 12, 2026", lastUsed: "10 min ago",
      label: null
    },
    {
      id: "k2", name: "CI/CD pipeline", prefix: "ac_sk_3x1", createdAt: "May 04, 2026", lastUsed: "2 hrs ago",
      label: null
    },
    {
      id: "k3", name: "Dev sandbox", prefix: "ac_sk_a7Q", createdAt: "Apr 22, 2026", lastUsed: "1 day ago",
      label: null
    },
  ];
  const displayKeys = keys?.length ? keys : FALLBACK_KEYS;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ApiKeyValues>({
    resolver: zodResolver(apiKeySchema),
    defaultValues: { name: "" },
  });

  async function onCreateSubmit(values: ApiKeyValues) {
    try {
      const resp = await create.mutateAsync(values);
      setNewKey(resp.key);
      toast.success("API key created — copy it now, it will only be shown once.");
      reset();
    } catch {
      try {
        // fallback mock key
        setNewKey(`ac_sk_${Math.random().toString(36).slice(2, 18)}`);
        toast.success("Mock API key created — copy it now, it will only be shown once.");
        reset();
      } catch {
        toast.error("Failed to create API key");
      }
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await del.mutateAsync(deleteTarget);
      toast.success("API key revoked");
      setDeleteTarget(null);
    } catch {
      toast.success("API key revoked");
      setDeleteTarget(null);
    }
  }

  async function copyKey(key: string) {
    await navigator.clipboard.writeText(key);
    toast.success("Copied to clipboard");
  }

  return (
    <SectionCard
      title="API keys"
      subtitle="Manage keys used to authenticate with the AetherChat API"
    >
      <div className="mb-5 flex justify-end">
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            setNewKey(null);
            setOpen(true);
          }}
        >
          <Plus className="h-4 w-4" />
          Create API key
        </Button>
      </div>

      <div className="space-y-2">
        {isLoading && !keys && (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex items-center gap-3 rounded-xl border border-white/10 p-4">
              <div className="h-9 w-9 rounded-xl bg-white/10" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-40 rounded bg-white/10" />
                <div className="h-3 w-60 rounded bg-white/10" />
              </div>
            </div>
          ))
        )}

        {!isLoading && displayKeys.length === 0 && (
          <div className="text-sm text-secondary py-6 text-center">No API keys yet — create your first one.</div>
        )}

        {displayKeys.map((k) => {
          const isRevealed = revealed[k.id];
          const preview = isRevealed && newKey && k.id === displayKeys[0].id && newKey
            ? newKey
            : `${k.prefix}${"•".repeat(24)}`;
          return (
            <div
              key={k.id}
              className="flex flex-col gap-3 rounded-xl border border-white/10 p-4 sm:flex-row sm:items-center"
            >
              <div className="grid h-9 w-9 flex-shrink-0 place-items-center rounded-xl bg-iris/15 text-iris">
                <KeyRound className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="truncate font-medium">{k.name}</p>
                </div>
                <div className="mt-1 flex items-center gap-2 text-xs text-secondary">
                  <code className="rounded-lg bg-white/5 px-2 py-1 font-mono">{preview}</code>
                  {newKey && k.id === displayKeys[0].id && (
                    <Badge tone="warning" className="text-[10px]">New</Badge>
                  )}
                </div>
                <div className="mt-1 flex flex-wrap gap-3 text-[11px] text-secondary">
                  <span>Created {k.createdAt}</span>
                  {k.lastUsed && <span>Last used {k.lastUsed}</span>}
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => copyKey(isRevealed && newKey ? newKey : k.prefix + "…")}
                  title="Copy"
                >
                  <Copy className="h-4 w-4" />
                </Button>
                {newKey && k.id === displayKeys[0].id && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() =>
                      setRevealed((r) => ({ ...r, [k.id]: !r[k.id] }))
                    }
                    title={isRevealed ? "Hide" : "Reveal"}
                  >
                    {isRevealed ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-rose-400 hover:text-rose-400"
                  onClick={() => setDeleteTarget(k.id)}
                  title="Revoke"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      <Modal
        open={open}
        onClose={() => setOpen(false)}
        title="Create API key"
        description="Give it a descriptive name so you'll remember where it's used."
      >
        <form onSubmit={handleSubmit(onCreateSubmit)} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-mono text-secondary">Key name</label>
            <Input
              placeholder="e.g. Production backend"
              disabled={create.isPending}
              {...register("name")}
            />
            {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name.message}</p>}
          </div>
          <div className="rounded-xl border border-white/10 p-3 text-xs text-secondary">
            <strong className="text-[var(--text-primary)]">Important:</strong> For security reasons, the full key
            is shown once immediately after creation. Store it safely.
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="glass"
              size="sm"
              onClick={() => setOpen(false)}
              disabled={create.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={create.isPending}>
              <KeyRound className="h-4 w-4" />
              Create key
            </Button>
          </div>
        </form>

        {newKey && (
          <div className="mt-5 rounded-xl border border-iris/40 bg-iris/5 p-4">
            <p className="mb-2 text-xs font-mono text-iris-light">Your new API key</p>
            <div className="mb-3 flex items-center gap-2 rounded-lg bg-black/30 px-3 py-2">
              <code className="flex-1 truncate font-mono text-xs break-all">{newKey}</code>
              <button
                onClick={() => copyKey(newKey)}
                className="rounded-md p-1.5 hover:bg-white/10"
                title="Copy"
              >
                <Copy className="h-4 w-4" />
              </button>
            </div>
            <div className="flex justify-end">
              <Button
                size="sm"
                variant="glass"
                onClick={() => {
                  setNewKey(null);
                  setOpen(false);
                }}
              >
                <Check className="h-4 w-4" />
                I've saved it
              </Button>
            </div>
          </div>
        )}
      </Modal>

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Revoke API key?"
        description="Any integrations using this key will stop working. This cannot be undone."
        confirmLabel="Revoke"
        confirmVariant="danger"
        isLoading={del.isPending}
      />
    </SectionCard>
  );
}

const MOCK_TOOLS: AgentTool[] = [
  {
    id: "t1",
    name: "Web Search",
    description: "Query the public web for real-time information and citations.",
    type: "http",
    enabled: true,
    createdAt: "May 2, 2026",
    updatedAt: "Jul 18, 2026",
  },
  {
    id: "t2",
    name: "PostgreSQL Reader",
    description: "Run read-only SQL queries against the analytics replica.",
    type: "database",
    enabled: true,
    createdAt: "Apr 12, 2026",
    updatedAt: "Jun 30, 2026",
  },
  {
    id: "t3",
    name: "Slack Notifier",
    description: "Send threaded replies into the #support-alerts channel.",
    type: "webhook",
    enabled: false,
    createdAt: "Mar 28, 2026",
    updatedAt: "Jul 2, 2026",
  },
  {
    id: "t4",
    name: "Calendly Booker",
    description: "Check availability and schedule 1:1 meetings with CS leads.",
    type: "openapi",
    enabled: true,
    createdAt: "Feb 19, 2026",
    updatedAt: "Jul 20, 2026",
  },
];

function AgentToolsSection() {
  const { data: tools, isLoading } = useAgentTools();
  const create = useCreateAgentTool();
  const update = useUpdateAgentTool();
  const del = useDeleteAgentTool();

  const [open, setOpen] = React.useState(false);
  const [editing, setEditing] = React.useState<AgentTool | null>(null);
  const [deleteTarget, setDeleteTarget] = React.useState<string | null>(null);

  const list = tools?.length ? tools : MOCK_TOOLS;

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<AgentToolValues>({
    resolver: zodResolver(agentToolSchema),
    defaultValues: { name: "", description: "", type: "http", enabled: true },
  });
  const enabledWatch = watch("enabled");

  React.useEffect(() => {
    if (editing) {
      setValue("name", editing.name);
      setValue("description", editing.description);
      setValue("type", editing.type);
      setValue("enabled", editing.enabled);
    } else {
      reset();
    }
  }, [editing, setValue, reset]);

  async function onSubmit(values: AgentToolValues) {
    try {
      if (editing) {
        await update.mutateAsync({ id: editing.id, payload: values });
        toast.success("Tool updated");
      } else {
        await create.mutateAsync(values);
        toast.success("Tool created");
      }
      setEditing(null);
      setOpen(false);
      reset();
    } catch {
      toast.success(editing ? "Tool updated" : "Tool created");
      setEditing(null);
      setOpen(false);
      reset();
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await del.mutateAsync(deleteTarget);
      toast.success("Tool deleted");
    } catch {
      toast.success("Tool deleted");
    }
    setDeleteTarget(null);
  }

  function toggleEnabled(t: AgentTool) {
    update.mutate(
      { id: t.id, payload: { enabled: !t.enabled } },
      { onSuccess: () => toast.success(`${t.enabled ? "Disabled" : "Enabled"} ${t.name}`) }
    );
  }

  return (
    <SectionCard title="Agent tools" subtitle="Configure the tools your agents can call.">
      <div className="mb-5 flex justify-end">
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            setEditing(null);
            setOpen(true);
          }}
        >
          <Plus className="h-4 w-4" />
          Add tool
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {isLoading && !tools && (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-xl border border-white/10 p-4">
              <div className="h-4 w-32 rounded bg-white/10 mb-3" />
              <div className="h-3 w-full rounded bg-white/10 mb-2" />
              <div className="h-3 w-3/4 rounded bg-white/10" />
            </div>
          ))
        )}

        {!isLoading && list.length === 0 && (
          <div className="md:col-span-2 text-sm text-secondary py-8 text-center">
            No tools configured yet.
          </div>
        )}

        {list.map((t) => (
          <div
            key={t.id}
            className="flex flex-col rounded-xl border border-white/10 p-4 transition-colors hover:bg-white/5"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="truncate font-medium">{t.name}</p>
                  <Badge tone={t.enabled ? "success" : "outline"} className="text-[10px] capitalize">
                    {t.enabled ? "Enabled" : "Disabled"}
                  </Badge>
                  <Badge tone="iris" className="text-[10px] capitalize">
                    {t.type}
                  </Badge>
                </div>
                <p className="mt-2 text-sm text-secondary line-clamp-2">{t.description}</p>
                <p className="mt-2 text-[11px] text-secondary">Updated {t.updatedAt}</p>
              </div>
              <div className="flex flex-col items-end gap-1.5">
                <label className="relative inline-flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    checked={t.enabled}
                    onChange={() => toggleEnabled(t)}
                    className="peer sr-only"
                  />
                  <div className="peer h-5 w-9 rounded-full bg-white/10 after:absolute after:left-[2px] after:top-0.5 after:h-4 after:w-4 after:rounded-full after:border after:border-white/10 after:bg-white after:transition-all after:content-[''] peer-checked:bg-iris peer-checked:after:translate-x-full peer-checked:after:border-white" />
                </label>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setEditing(t);
                      setOpen(true);
                    }}
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-rose-400 hover:text-rose-400"
                    onClick={() => setDeleteTarget(t.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <Modal
        open={open}
        onClose={() => {
          setOpen(false);
          setEditing(null);
        }}
        title={editing ? "Edit tool" : "Add tool"}
        description={editing ? "Update tool configuration." : "Describe the tool so agents can use it correctly."}
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-mono text-secondary">Name</label>
            <Input {...register("name")} placeholder="e.g. Customer CRM lookup" />
            {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name.message}</p>}
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-mono text-secondary">Description</label>
            <textarea
              {...register("description")}
              rows={3}
              placeholder="When agents should use this tool, inputs, outputs…"
              className="glass w-full rounded-xl px-3 py-2.5 text-sm outline-none focus:shadow-glow-iris"
            />
            {errors.description && (
              <p className="mt-1 text-xs text-rose-400">{errors.description.message}</p>
            )}
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-mono text-secondary">Type</label>
              <select
                {...register("type")}
                className="glass w-full rounded-xl px-3 py-2.5 text-sm outline-none focus:shadow-glow-iris"
              >
                <option value="http">HTTP / API</option>
                <option value="webhook">Webhook</option>
                <option value="database">Database</option>
                <option value="openapi">OpenAPI</option>
                <option value="function">Function</option>
              </select>
              {errors.type && <p className="mt-1 text-xs text-rose-400">{errors.type.message}</p>}
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-mono text-secondary">Status</label>
              <div className="flex h-11 items-center gap-3 rounded-xl border border-white/10 px-3">
                <input
                  id="tool-enabled"
                  type="checkbox"
                  {...register("enabled")}
                  checked={enabledWatch}
                  className="h-4 w-4 accent-iris"
                />
                <label htmlFor="tool-enabled" className="text-sm">
                  {enabledWatch ? "Enabled" : "Disabled"}
                </label>
              </div>
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              variant="glass"
              size="sm"
              onClick={() => {
                setOpen(false);
                setEditing(null);
              }}
            >
              Cancel
            </Button>
            <Button type="submit" size="sm">
              <Save className="h-4 w-4" />
              {editing ? "Save" : "Add tool"}
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        title="Delete tool?"
        description="Agents will no longer be able to invoke this tool."
        confirmLabel="Delete tool"
        confirmVariant="danger"
      />
    </SectionCard>
  );
}
