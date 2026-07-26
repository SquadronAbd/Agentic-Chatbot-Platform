"use client";

import * as React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { motion } from "framer-motion";
import {
  MessageSquare,
  Users,
  Clock,
  FileText,
  Activity,
  MessageCircle,
  TrendingUp,
  Zap,
} from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import { Skeleton, CardSkeleton } from "@/components/ui/loading-skeleton";
import { ErrorState } from "@/components/ui/states";
import { useAnalyticsDaily, useAnalyticsSummary } from "@/hooks/use-api";
import { MOCK_DAILY_METRICS } from "@/lib/mock-data";
import type { AnalyticsSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

const PIE_COLORS = ["#6C5CE7", "#22D3EE", "#F59E0B", "#EF4444", "#10B981"];

function StatCard({
  label,
  value,
  icon: Icon,
  delta,
  tone,
  loading,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  delta?: string;
  tone: "iris" | "aqua" | "success" | "warning" | "default";
  loading?: boolean;
}) {
  const toneClass = cn(
    "bg-gradient-to-br",
    tone === "iris" && "from-iris/30 to-iris/10 text-iris",
    tone === "aqua" && "from-aqua/30 to-aqua/10 text-aqua",
    tone === "success" && "from-emerald-500/20 to-emerald-500/5 text-emerald-400",
    tone === "warning" && "from-amber-500/20 to-amber-500/5 text-amber-400",
    tone === "default" && "from-white/20 to-white/5 text-[var(--text-primary)]"
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 260, damping: 24 }}
    >
      <GlassCard className="p-5 shadow-glass">
        {loading ? (
          <>
            <Skeleton className="mb-3 h-10 w-10 rounded-xl" />
            <Skeleton className="mb-2 h-7 w-24" />
            <Skeleton className="h-4 w-32" />
          </>
        ) : (
          <>
            <div className={cn("mb-3 grid h-10 w-10 place-items-center rounded-xl", toneClass)}>
              <Icon className="h-5 w-5" />
            </div>
            <p className="font-display text-2xl font-bold tracking-tight">{value}</p>
            <div className="mt-1 flex items-center gap-2">
              <p className="text-xs text-secondary">{label}</p>
              {delta && <Badge tone={tone === "aqua" ? "success" : "aqua"}>{delta}</Badge>}
            </div>
          </>
        )}
      </GlassCard>
    </motion.div>
  );
}

const FALLBACK_SUMMARY: AnalyticsSummary = {
  totalMessages: 8264,
  totalActiveUsers: 94,
  totalConversations: 1820,
  totalDocuments: 312,
  totalApiUsage: 28150,
  avgLatencyMs: 940,
};

export default function AnalyticsPage() {
  const { data: daily, isLoading: loadingDaily, error: errorDaily, refetch: refetchDaily } = useAnalyticsDaily();
  const { data: summary, isLoading: loadingSummary } = useAnalyticsSummary();

  const metrics = daily && daily.length > 0 ? daily : MOCK_DAILY_METRICS;
  const stats = summary ?? FALLBACK_SUMMARY;

  const roleDist = [
    { name: "Admin", value: 2 },
    { name: "Manager", value: 6 },
    { name: "Agent", value: 18 },
    { name: "Viewer", value: 68 },
  ];

  if (errorDaily) {
    return (
      <AppShell minimumRole="manager">
        {(user) => (
          <div className="flex h-full flex-col overflow-y-auto">
            <div className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 md:px-6">
              <Topbar
                title="Analytics"
                subtitle="Workspace performance"
                breadcrumb={[{ label: "Workspace" }, { label: "Analytics" }]}
                user={user}
              />
              <ErrorState
                title="Could not load analytics"
                description={errorDaily instanceof Error ? errorDaily.message : undefined}
                onRetry={() => refetchDaily()}
              />
            </div>
          </div>
        )}
      </AppShell>
    );
  }

  return (
    <AppShell minimumRole="manager">
      {(user) => (
        <div className="flex h-full flex-col overflow-y-auto">
          <div className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 md:px-6">
          <Topbar
            title="Analytics"
            subtitle="Workspace performance overview"
            breadcrumb={[{ label: "Workspace" }, { label: "Analytics" }]}
            user={user}
            actions={
              <Badge tone="aqua" className="gap-1">
                <TrendingUp className="h-3 w-3" />
                Live
              </Badge>
            }
          />

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 mb-5">
            <StatCard
              label="Total messages"
              value={stats.totalMessages.toLocaleString()}
              icon={MessageSquare}
              delta="+12.3%"
              tone="iris"
              loading={loadingSummary}
            />
            <StatCard
              label="Active users"
              value={stats.totalActiveUsers}
              icon={Users}
              delta="+4.1%"
              tone="aqua"
              loading={loadingSummary}
            />
            <StatCard
              label="Conversations"
              value={stats.totalConversations.toLocaleString()}
              icon={MessageCircle}
              delta="+8.2%"
              tone="success"
              loading={loadingSummary}
            />
            <StatCard
              label="Documents"
              value={stats.totalDocuments}
              icon={FileText}
              delta="3 new today"
              tone="default"
              loading={loadingSummary}
            />
            <StatCard
              label="API calls"
              value={stats.totalApiUsage.toLocaleString()}
              icon={Zap}
              delta="+18.7%"
              tone="warning"
              loading={loadingSummary}
            />
            <StatCard
              label="Avg latency"
              value={`${stats.avgLatencyMs}ms`}
              icon={Clock}
              delta="-62ms"
              tone="iris"
              loading={loadingSummary}
            />
          </div>

          <div className="grid grid-cols-1 gap-5 lg:grid-cols-3 mb-5">
            <GlassCard className="lg:col-span-2 p-5 shadow-glass">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h3 className="font-display text-base font-semibold">Daily messages & active users</h3>
                  <p className="text-xs text-secondary">Last 7 days</p>
                </div>
                <Badge tone="iris"><Activity className="h-3 w-3 mr-1" /> Live</Badge>
              </div>
              {loadingDaily ? (
                <div className="h-[320px] grid place-items-center">
                  <Skeleton className="h-full w-full rounded-xl" />
                </div>
              ) : (
                <div className="h-[320px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={metrics} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="msgLine" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#6C5CE7" stopOpacity={0.4} />
                          <stop offset="100%" stopColor="#6C5CE7" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" vertical={false} />
                      <XAxis
                        dataKey="date"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 11, fill: "currentColor", opacity: 0.6 }}
                      />
                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 11, fill: "currentColor", opacity: 0.6 }}
                        width={36}
                      />
                      <Tooltip
                        cursor={{ stroke: "rgba(108,92,231,0.2)", strokeWidth: 2 }}
                        contentStyle={{
                          background: "rgba(18, 20, 43, 0.9)",
                          backdropFilter: "blur(12px)",
                          border: "1px solid rgba(255,255,255,0.08)",
                          borderRadius: 12,
                          fontSize: 12,
                        }}
                      />
                      <Legend wrapperStyle={{ fontSize: 12 }} />
                      <Line
                        type="monotone"
                        dataKey="messages"
                        name="Messages"
                        stroke="#6C5CE7"
                        strokeWidth={3}
                        dot={{ r: 3, strokeWidth: 2 }}
                        activeDot={{ r: 5 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="activeUsers"
                        name="Active users"
                        stroke="#22D3EE"
                        strokeWidth={3}
                        dot={{ r: 3, strokeWidth: 2 }}
                        activeDot={{ r: 5 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </GlassCard>

            <GlassCard className="p-5 shadow-glass">
              <div className="mb-4">
                <h3 className="font-display text-base font-semibold">Role distribution</h3>
                <p className="text-xs text-secondary">User base breakdown</p>
              </div>
              <div className="h-[320px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={roleDist}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {roleDist.map((_, idx) => (
                        <Cell key={`c-${idx}`} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        background: "rgba(18, 20, 43, 0.9)",
                        border: "1px solid rgba(255,255,255,0.08)",
                        borderRadius: 12,
                        fontSize: 12,
                      }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      wrapperStyle={{ fontSize: 12, paddingTop: 12 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </GlassCard>
          </div>

          <GlassCard className="p-5 shadow-glass">
            <div className="mb-4">
              <h3 className="font-display text-base font-semibold">Average latency (ms)</h3>
              <p className="text-xs text-secondary">Response time over the last 7 days</p>
            </div>
            {loadingDaily ? (
              <Skeleton className="h-[260px] w-full rounded-xl" />
            ) : (
              <div className="h-[260px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={metrics} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" vertical={false} />
                    <XAxis
                      dataKey="date"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 11, fill: "currentColor", opacity: 0.6 }}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 11, fill: "currentColor", opacity: 0.6 }}
                      width={48}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "rgba(18, 20, 43, 0.9)",
                        border: "1px solid rgba(255,255,255,0.08)",
                        borderRadius: 12,
                        fontSize: 12,
                      }}
                    />
                    <Bar dataKey="avgLatencyMs" name="Latency (ms)" radius={[8, 8, 0, 0]} fill="#22D3EE" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </GlassCard>
          </div>
        </div>
      )}
    </AppShell>
  );
}
