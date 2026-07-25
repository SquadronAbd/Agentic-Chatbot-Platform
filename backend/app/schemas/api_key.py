import uuid
from datetime import datetime
from pydantic import BaseModel


class ApiKeyCreate(BaseModel):
    label: str | None = None


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    label: str | None
    created_at: datetime
    last_used: datetime | None
    # key_hash is deliberately excluded — never expose the hash over the API

    class Config:
        from_attributes = True


class ApiKeyCreatedResponse(BaseModel):
    """Only returned once at creation time — the raw key is never stored."""
    id: uuid.UUID
    key: str
    label: str | None
    created_at: datetime