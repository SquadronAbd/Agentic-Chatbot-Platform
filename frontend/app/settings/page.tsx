import { KeyRound, User } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { GlassCard } from "@/components/ui/glass-card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MOCK_USER } from "@/lib/mock-data";

export default function SettingsPage() {
  return (
    <AppShell user={MOCK_USER}>
      <Topbar title="Settings" subtitle="Profile & API keys" user={MOCK_USER} />

      <div className="space-y-6">
        <GlassCard className="px-6 py-6">
          <div className="mb-4 flex items-center gap-2">
            <User className="h-4 w-4 text-iris-dim dark:text-iris-light" />
            <h2 className="font-display text-sm font-semibold">Profile</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-mono text-secondary">Full name</label>
              <Input defaultValue={MOCK_USER.name} />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-mono text-secondary">Email</label>
              <Input defaultValue={MOCK_USER.email} type="email" />
            </div>
          </div>
          <Button className="mt-4">Save changes</Button>
        </GlassCard>

        <GlassCard className="px-6 py-6">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <KeyRound className="h-4 w-4 text-iris-dim dark:text-iris-light" />
              <h2 className="font-display text-sm font-semibold">API keys</h2>
            </div>
            <Button variant="glass">Create key</Button>
          </div>

          <div className="space-y-2">
            {[
              { label: "local-dev", used: "3 days ago" },
              { label: "ci-pipeline", used: "18 min ago" },
            ].map((key) => (
              <div key={key.label} className="flex items-center justify-between rounded-xl px-3 py-2.5 hover:bg-white/5">
                <div>
                  <p className="font-mono text-sm">{key.label}</p>
                  <p className="text-xs text-secondary">Last used {key.used}</p>
                </div>
                <Badge tone="aqua">active</Badge>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </AppShell>
  );
}
