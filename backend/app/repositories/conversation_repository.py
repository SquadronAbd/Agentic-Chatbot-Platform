from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversations import Conversation


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: str, title: str | None) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Conversation]:
        result = await self.db.execute(select(Conversation))
        return list(result.scalars().all())

    async def list_by_user(self, user_id: str) -> list[Conversation]:
        result = await self.db.execute(select(Conversation).where(Conversation.user_id == user_id))
        return list(result.scalars().all())

    async def delete(self, conversation: Conversation) -> None:
        await self.db.delete(conversation)
        await self.db.commit()