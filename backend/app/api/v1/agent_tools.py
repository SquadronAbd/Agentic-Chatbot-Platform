from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import require_role
from app.services.agent_tool_service import AgentToolService
from app.models.users import User
from app.schemas.agent_tool import AgentToolCreate, AgentToolUpdate, AgentToolOut

router = APIRouter(prefix="/agent-tools", tags=["agent-tools"])


@router.post("", response_model=AgentToolOut, status_code=status.HTTP_201_CREATED)
async def create_tool(
    payload: AgentToolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    service = AgentToolService(db)
    return await service.create(payload.name, payload.description, payload.enabled, payload.config)


@router.get("", response_model=list[AgentToolOut])
async def list_tools(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "agent")),
):
    service = AgentToolService(db)
    return await service.list_all()


@router.put("/{tool_id}", response_model=AgentToolOut)
async def update_tool(
    tool_id: str,
    payload: AgentToolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    service = AgentToolService(db)
    return await service.update(tool_id, payload.description, payload.enabled, payload.config)


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    service = AgentToolService(db)
    await service.delete(tool_id)
    return None