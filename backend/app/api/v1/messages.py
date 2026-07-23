from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.services.message_service import MessageService
from app.models.users import User
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/conversations/{conversation_id}/messages", tags=["messages"])


@router.post("", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: str,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = MessageService(db)
    return await service.create(current_user, conversation_id, payload.role, payload.content)


@router.get("", response_model=list[MessageOut])
async def list_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent", "viewer")),
):
    service = MessageService(db)
    return await service.list_for_conversation(current_user, conversation_id)