from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.message_repository import MessageRepository
from app.services.conversation_service import ConversationService
from app.models.users import User
from app.models.messages import Message


class MessageService:
    def __init__(self, db: AsyncSession):
        self.repo = MessageRepository(db)
        self.conversation_service = ConversationService(db)

    async def create(self, current_user: User, conversation_id: str, role: str, content: str) -> Message:
        # Ensures the user actually owns (or is privileged over) this conversation first
        await self.conversation_service.get_owned_or_403(current_user, conversation_id)
        return await self.repo.create(conversation_id, role, content)

    async def list_for_conversation(self, current_user: User, conversation_id: str) -> list[Message]:
        await self.conversation_service.get_owned_or_403(current_user, conversation_id)
        return await self.repo.list_by_conversation(conversation_id)