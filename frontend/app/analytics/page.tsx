import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { RoleGuard } from "@/components/auth/role-guard";
import { AnalyticsDashboard } from "@/components/analytics/analytics-dashboard";
import { MOCK_DAILY_METRICS, MOCK_USER } from "@/lib/mock-data";

export default function AnalyticsPage() {
  return (
    <AppShell user={MOCK_USER}>
      <Topbar title="Analytics" subtitle="Manager role or higher · last 7 days" user={MOCK_USER} />
      <RoleGuard userRole={MOCK_USER.role} minimumRole="manager">
        <AnalyticsDashboard data={MOCK_DAILY_METRICS} />
      </RoleGuard>
    </AppShell>
  );
}
