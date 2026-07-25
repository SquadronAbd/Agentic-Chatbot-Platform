from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import require_role
from app.models.users import User
from app.models.audit_logs import AuditLog
import uuid
from datetime import datetime
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    resource: str | None
    ip_address: str | None
    created_at: datetime

    class Config:
        from_attributes = True


router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=list[AuditLogOut])
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(500))
    return list(result.scalars().all())