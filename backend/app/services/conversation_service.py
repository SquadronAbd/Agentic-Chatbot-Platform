from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.conversation_repository import ConversationRepository
from app.models.users import User
from app.models.conversations import Conversation
from app.core.deps import is_privileged


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.repo = ConversationRepository(db)

    async def create(self, current_user: User, title: str | None) -> Conversation:
        return await self.repo.create(str(current_user.id), title)

    async def list_for_user(self, current_user: User) -> list[Conversation]:
        if is_privileged(current_user):
            return await self.repo.list_all()
        # Agents see only their own; Viewers currently see none until sharing exists
        if current_user.role == "agent":
            return await self.repo.list_by_user(str(current_user.id))
        return []

    async def get_owned_or_403(self, current_user: User, conversation_id: str) -> Conversation:
        conv = await self.repo.get_by_id(conversation_id)
        if conv is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        if not is_privileged(current_user) and str(conv.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your conversation")
        return conv

    async def delete(self, current_user: User, conversation_id: str) -> None:
        conv = await self.get_owned_or_403(current_user, conversation_id)
        await self.repo.delete(conv)