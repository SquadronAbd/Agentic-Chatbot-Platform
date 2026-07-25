import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.agent_tool_repository import AgentToolRepository
from app.models.agent_tools import AgentTool


class AgentToolService:
    def __init__(self, db: AsyncSession):
        self.repo = AgentToolRepository(db)

    async def create(self, name: str, description: str | None, enabled: bool, config: dict | None) -> AgentTool:
        return await self.repo.create(name, description, enabled, config)

    async def list_all(self) -> list[AgentTool]:
        return await self.repo.list_all()

    async def update(self, tool_id: str, description: str | None, enabled: bool | None, config: dict | None) -> AgentTool:
        tool = await self.repo.get_by_id(tool_id)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
        return await self.repo.update(tool, description, enabled, config)

    async def delete(self, tool_id: str) -> None:
        tool = await self.repo.get_by_id(tool_id)
        if tool is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
        await self.repo.delete(tool)