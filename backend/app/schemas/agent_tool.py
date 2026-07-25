import uuid
from pydantic import BaseModel
from typing import Any


class AgentToolCreate(BaseModel):
    name: str
    description: str | None = None
    enabled: bool = True
    config: dict[str, Any] | None = None


class AgentToolUpdate(BaseModel):
    description: str | None = None
    enabled: bool | None = None
    config: dict[str, Any] | None = None


class AgentToolOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    enabled: bool
    config: dict[str, Any] | None

    class Config:
        from_attributes = True