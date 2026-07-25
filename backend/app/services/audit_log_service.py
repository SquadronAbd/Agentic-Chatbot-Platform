from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_logs import AuditLog


class AuditLogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, action: str, user_id: str | None = None, resource: str | None = None, ip_address: str | None = None) -> None:
        """Write an audit log entry. Call this from any route that needs tracking."""
        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
        )
        self.db.add(entry)
        await self.db.commit()