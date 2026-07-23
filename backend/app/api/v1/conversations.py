from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.services.conversation_service import ConversationService
from app.models.users import User
from app.schemas.conversation import ConversationCreate, ConversationOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = ConversationService(db)
    return await service.create(current_user, payload.title)


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent", "viewer")),
):
    service = ConversationService(db)
    return await service.list_for_user(current_user)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = ConversationService(db)
    await service.delete(current_user, conversation_id)
    return None