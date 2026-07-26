"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { UserPlus, Search, Shield } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/ui/search-input";
import { EmptyState, ErrorState } from "@/components/ui/states";
import { TableSkeleton } from "@/components/ui/loading-skeleton";
import { Modal, ConfirmDialog } from "@/components/ui/modal";
import { Pagination } from "@/components/ui/pagination";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Avatar } from "@/components/ui/avatar";
import { createUserSchema, type CreateUserValues } from "@/lib/schemas";
import {
  useUsers,
  useCreateUser,
  useDeleteUser,
  useUpdateUserRole,
} from "@/hooks/use-api";

import type { ManagedUser, Role } from "@/lib/types";
import { cn } from "@/lib/utils";

const PAGE_SIZE = 10;

const ROLE_OPTIONS: Role[] = ["viewer", "agent", "manager", "admin"];

function roleTone(r: Role): Parameters<typeof Badge>[0]["tone"] {
  switch (r) {
    case "admin":
      return "iris";
    case "manager":
      return "aqua";
    case "agent":
      return "default";
    case "viewer":
      return "outline";
  }
}

export default function AdminPage() {
  const [page, setPage] = React.useState(1);
  const [search, setSearch] = React.useState("");
  const [roleFilter, setRoleFilter] = React.useState<Role | "all">("all");
  const [createOpen, setCreateOpen] = React.useState(false);
  const [deleteTarget, setDeleteTarget] = React.useState<ManagedUser | null>(null);

  const {
    data: paginated,
    isLoading,
    error,
    refetch,
  } = useUsers({ page, limit: PAGE_SIZE, search });
  const createUser = useCreateUser();
  const deleteUser = useDeleteUser();
  const updateRole = useUpdateUserRole();

  const users = paginated?.items ?? [];
  const filtered = React.useMemo(() => {
    let list = users;
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(
        (u) =>
          u.name.toLowerCase().includes(q) ||
          u.email.toLowerCase().includes(q)
      );
    }
    if (roleFilter !== "all") {
      list = list.filter((u) => u.role === roleFilter);
    }
    return list;
  }, [users, search, roleFilter]);

  const total = paginated?.total ?? 0;
  const totalPages = paginated?.totalPages ?? 1;
  const paged = paginated
    ? filtered
    : filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  React.useEffect(() => {
    setPage(1);
  }, [search, roleFilter]);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateUserValues>({
    resolver: zodResolver(createUserSchema),
    defaultValues: { name: "", email: "", password: "", role: "viewer" },
  });

  async function onCreateSubmit(values: CreateUserValues) {
    try {
      await createUser.mutateAsync(values);
      toast.success("User created");
      setCreateOpen(false);
      reset();
    } catch {
      toast.error("Failed to create user");
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await deleteUser.mutateAsync(deleteTarget.id);
      toast.success("User deleted");
      setDeleteTarget(null);
    } catch {
      toast.error("Failed to delete user");
    }
  }

  function handleRoleChange(user: ManagedUser, role: Role) {
    void user;
    void role;
    toast.info(
      "Role updates via the inline selector are not yet available in this backend release."
    );
  }

  return (
    <AppShell minimumRole="admin">
      {(user) => (
        <div className="flex h-full flex-col overflow-y-auto">
          <div className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 md:px-6">
          <Topbar
            title="Users"
            subtitle={paginated ? `${paginated.total} total users` : "Users"}
            breadcrumb={[{ label: "Admin" }, { label: "Users" }]}
            user={user}
            actions={
              <Button
                variant="primary"
                size="sm"
                onClick={() => setCreateOpen(true)}
                disabled={createUser.isPending}
              >
                <UserPlus className="h-4 w-4" />
                Add user
              </Button>
            }
          />

          <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex flex-col gap-3 sm:flex-row">
              <div className="w-full max-w-sm">
                <SearchInput
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search users…"
                />
              </div>
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value as Role | "all")}
                className="glass w-full rounded-xl px-3 py-2.5 text-sm outline-none sm:w-[160px] focus:shadow-glow-iris"
              >
                <option value="all">All roles</option>
                {ROLE_OPTIONS.map((r) => (
                  <option key={r} value={r}>
                    {r.charAt(0).toUpperCase() + r.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center gap-2">
              <Badge tone="iris">{filtered.length} found</Badge>
              <Badge tone="outline">
                <Shield className="mr-1 h-3 w-3 inline" />
                Admin panel
              </Badge>
            </div>
          </div>

          {isLoading && !paginated ? (
            <TableSkeleton rows={PAGE_SIZE} cols={5} />
          ) : error ? (
            <ErrorState
              title="Failed to load users"
              description={error instanceof Error ? error.message : "Please try again."}
              onRetry={() => refetch()}
            />
          ) : paged.length === 0 ? (
            <EmptyState
              title="No users match"
              description={search || roleFilter !== "all" ? "Try adjusting filters." : "Create the first user."}
              action="Add user"
              onAction={() => setCreateOpen(true)}
            />
          ) : (
            <>
              <GlassCard className="overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="border-b border-white/10 bg-white/5">
                      <tr>
                        <th className="px-5 py-3 font-semibold">User</th>
                        <th className="px-5 py-3 font-semibold">Role</th>
                        <th className="px-5 py-3 font-semibold">Last active</th>
                        <th className="w-32 px-5 py-3 text-right font-semibold">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {paged.map((u, idx) => (
                        <motion.tr
                          key={u.id}
                          initial={{ opacity: 0, y: 6 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.04 }}
                          className="transition-colors hover:bg-white/5"
                        >
                          <td className="px-5 py-4">
                            <div className="flex items-center gap-3">
                              <Avatar name={u.name} size="sm" />
                              <div className="min-w-0">
                                <p className="truncate font-medium">{u.name}</p>
                                <p className="truncate text-xs text-secondary">{u.email}</p>
                              </div>
                            </div>
                          </td>
                          <td className="px-5 py-4">
                            <div
                              className="inline-flex cursor-not-allowed items-center gap-2"
                              title="Backend role-update endpoint not implemented in this release"
                            >
                              <select
                                value={u.role}
                                onChange={(e) => handleRoleChange(u, e.target.value as Role)}
                                disabled
                                className={cn(
                                  "rounded-lg px-2.5 py-1 text-xs font-medium capitalize outline-none",
                                  "glass cursor-not-allowed opacity-80"
                                )}
                              >
                                {ROLE_OPTIONS.map((r) => (
                                  <option key={r} value={r} className="bg-nebula">
                                    {r.charAt(0).toUpperCase() + r.slice(1)}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </td>
                          <td className="px-5 py-4 text-sm text-secondary">{u.lastActive}</td>
                          <td className="px-5 py-4 text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setDeleteTarget(u)}
                              className="text-rose-400 hover:text-rose-400"
                              disabled={deleteUser.variables === u.id && deleteUser.isPending}
                            >
                              Delete
                            </Button>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </GlassCard>
              <div className="mt-5">
                <Pagination
                  page={page}
                  totalPages={totalPages}
                  onPageChange={setPage}
                  totalItems={total}
                  itemsPerPage={PAGE_SIZE}
                />
              </div>
            </>
          )}

          <Modal
            open={createOpen}
            onClose={() => setCreateOpen(false)}
            title="Add new user"
            description="Invite a team member to AetherChat"
          >
            <form onSubmit={handleSubmit(onCreateSubmit)} className="space-y-3.5">
              <div>
                <label className="mb-1.5 block text-xs font-mono text-secondary">Name</label>
                <Input placeholder="Jane Doe" disabled={createUser.isPending} {...register("name")} />
                {errors.name && <p className="mt-1 text-xs text-rose-400">{errors.name.message}</p>}
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-mono text-secondary">Email</label>
                <Input
                  type="email"
                  placeholder="jane@company.com"
                  disabled={createUser.isPending}
                  {...register("email")}
                />
                {errors.email && <p className="mt-1 text-xs text-rose-400">{errors.email.message}</p>}
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-mono text-secondary">Temporary password</label>
                <Input
                  type="password"
                  placeholder="At least 8 characters"
                  disabled={createUser.isPending}
                  {...register("password")}
                />
                {errors.password && (
                  <p className="mt-1 text-xs text-rose-400">{errors.password.message}</p>
                )}
              </div>
              <div>
                <label className="mb-1.5 block text-xs font-mono text-secondary">Role</label>
                <select
                  {...register("role")}
                  className="glass w-full rounded-xl px-3 py-2.5 text-sm outline-none focus:shadow-glow-iris"
                  disabled={createUser.isPending}
                >
                  {ROLE_OPTIONS.map((r) => (
                    <option key={r} value={r} className="bg-nebula">
                      {r.charAt(0).toUpperCase() + r.slice(1)}
                    </option>
                  ))}
                </select>
                {errors.role && <p className="mt-1 text-xs text-rose-400">{errors.role.message}</p>}
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button
                  type="button"
                  variant="glass"
                  size="sm"
                  onClick={() => setCreateOpen(false)}
                  disabled={createUser.isPending}
                >
                  Cancel
                </Button>
                <Button type="submit" size="sm" disabled={createUser.isPending}>
                  {createUser.isPending ? "Creating…" : "Create user"}
                </Button>
              </div>
            </form>
          </Modal>

          <ConfirmDialog
            open={!!deleteTarget}
            onClose={() => setDeleteTarget(null)}
            onConfirm={handleDelete}
            title="Delete user?"
            description={
              deleteTarget
                ? `Remove ${deleteTarget.name} (${deleteTarget.email})? This removes their access permanently.`
                : ""
            }
            confirmLabel="Delete user"
            confirmVariant="danger"
            isLoading={deleteUser.isPending}
          />
          </div>
        </div>
      )}
    </AppShell>
  );
}
