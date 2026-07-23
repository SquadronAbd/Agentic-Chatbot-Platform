import { AppShell } from "@/components/layout/app-shell";
import { Topbar } from "@/components/layout/topbar";
import { RoleGuard } from "@/components/auth/role-guard";
import { DocumentUploader } from "@/components/documents/document-uploader";
import { DocumentList } from "@/components/documents/document-list";
import { MOCK_DOCUMENTS, MOCK_USER } from "@/lib/mock-data";

export default function DocumentsPage() {
  return (
    <AppShell user={MOCK_USER}>
      <Topbar title="Knowledge base" subtitle="Agent role or higher" user={MOCK_USER} />
      <RoleGuard userRole={MOCK_USER.role} minimumRole="agent">
        <div className="space-y-6">
          <DocumentUploader />
          <DocumentList documents={MOCK_DOCUMENTS} />
        </div>
      </RoleGuard>
    </AppShell>
  );
}
