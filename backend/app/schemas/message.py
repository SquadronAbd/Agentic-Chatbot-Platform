import uuid
from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class MessageOut(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True