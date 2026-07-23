"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { GlassCard } from "@/components/ui/glass-card";
import type { DailyMetric } from "@/lib/types";

function GlassTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass rounded-lg px-3 py-2 text-xs font-mono shadow-glass">
      <p className="mb-1 text-secondary">{label}</p>
      {payload.map((entry: any) => (
        <p key={entry.dataKey} style={{ color: entry.color }}>
          {entry.name}: {entry.value.toLocaleString()}
        </p>
      ))}
    </div>
  );
}

function StatTile({ label, value, sublabel }: { label: string; value: string; sublabel: string }) {
  return (
    <GlassCard className="px-5 py-4">
      <p className="text-xs font-mono uppercase tracking-wide text-secondary">{label}</p>
      <p className="mt-1 font-display text-2xl font-semibold">{value}</p>
      <p className="mt-0.5 text-xs text-secondary">{sublabel}</p>
    </GlassCard>
  );
}

export function AnalyticsDashboard({ data }: { data: DailyMetric[] }) {
  const totalMessages = data.reduce((sum, d) => sum + d.messages, 0);
  const peakUsers = Math.max(...data.map((d) => d.activeUsers));
  const avgLatency = Math.round(data.reduce((sum, d) => sum + d.avgLatencyMs, 0) / data.length);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatTile label="Messages (7d)" value={totalMessages.toLocaleString()} sublabel="across all users" />
        <StatTile label="Peak active users" value={peakUsers.toString()} sublabel="single-day high" />
        <StatTile label="Avg. latency" value={`${avgLatency} ms`} sublabel="p50, agent response" />
      </div>

      <GlassCard className="px-5 py-5">
        <h3 className="mb-4 font-display text-sm font-semibold">Messages &amp; active users</h3>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--text-secondary)" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "var(--text-secondary)" }} axisLine={false} tickLine={false} />
            <Tooltip content={<GlassTooltip />} />
            <Line type="monotone" dataKey="messages" name="Messages" stroke="#6C5CE7" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="activeUsers" name="Active users" stroke="#22D3EE" strokeWidth={2.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </GlassCard>

      <GlassCard className="px-5 py-5">
        <h3 className="mb-4 font-display text-sm font-semibold">Average response latency</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--text-secondary)" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "var(--text-secondary)" }} axisLine={false} tickLine={false} />
            <Tooltip content={<GlassTooltip />} />
            <Bar dataKey="avgLatencyMs" name="Latency (ms)" fill="#8C7CFF" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </GlassCard>
    </div>
  );
}
