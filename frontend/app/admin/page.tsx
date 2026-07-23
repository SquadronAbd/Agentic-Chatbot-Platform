import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { RoleGuard } from "@/components/auth/role-guard";
import { UserTable } from "@/components/admin/user-table";
import { MOCK_USER, MOCK_USERS } from "@/lib/mock-data";

export default function AdminPage() {
  return (
    <AppShell user={MOCK_USER}>
      <Topbar title="User management" subtitle="Admin only" user={MOCK_USER} />
      <RoleGuard userRole={MOCK_USER.role} minimumRole="admin">
        <UserTable users={MOCK_USERS} />
      </RoleGuard>
    </AppShell>
  );
}
