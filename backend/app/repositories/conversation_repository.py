from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversations import Conversation
from app.models.messages import Message


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _with_message_count(self):
        """Base query that adds message_count as a column via subquery."""
        count_sub = (
            select(func.count(Message.id))
            .where(Message.conversation_id == Conversation.id)
            .correlate(Conversation)
            .scalar_subquery()
        )
        return select(Conversation, count_sub.label("message_count"))

    async def _hydrate(self, rows) -> list[Conversation]:
        """Attach message_count onto each Conversation ORM object."""
        result = []
        for conv, count in rows:
            conv.message_count = count
            result.append(conv)
        return result

    async def create(self, user_id: str, title: str | None) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        conv.message_count = 0
        return conv

    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Conversation]:
        result = await self.db.execute(self._with_message_count())
        return await self._hydrate(result.all())

    async def list_by_user(self, user_id: str) -> list[Conversation]:
        result = await self.db.execute(
            self._with_message_count().where(Conversation.user_id == user_id)
        )
        return await self._hydrate(result.all())

    async def delete(self, conversation: Conversation) -> None:
        await self.db.delete(conversation)
        await self.db.commit()
