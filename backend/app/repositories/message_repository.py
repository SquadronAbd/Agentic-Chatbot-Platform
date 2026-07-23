from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.messages import Message


class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, conversation_id: str, role: str, content: str) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def list_by_conversation(self, conversation_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
        )
        return list(result.scalars().all())