from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.agent_tools import AgentTool


class AgentToolRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, description: str | None, enabled: bool, config: dict | None) -> AgentTool:
        tool = AgentTool(name=name, description=description, enabled=enabled, config=config)
        self.db.add(tool)
        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    async def get_by_id(self, tool_id: str) -> AgentTool | None:
        result = await self.db.execute(select(AgentTool).where(AgentTool.id == tool_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[AgentTool]:
        result = await self.db.execute(select(AgentTool))
        return list(result.scalars().all())

    async def update(self, tool: AgentTool, description: str | None, enabled: bool | None, config: dict | None) -> AgentTool:
        if description is not None:
            tool.description = description
        if enabled is not None:
            tool.enabled = enabled
        if config is not None:
            tool.config = config
        await self.db.commit()
        await self.db.refresh(tool)
        return tool

    async def delete(self, tool: AgentTool) -> None:
        await self.db.delete(tool)
        await self.db.commit()