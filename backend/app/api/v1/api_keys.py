from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.api_key_service import ApiKeyService
from app.models.users import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyOut, ApiKeyCreatedResponse

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ApiKeyService(db)
    api_key, raw_key = await service.create(current_user, payload.label)
    return ApiKeyCreatedResponse(
        id=api_key.id,
        key=raw_key,
        label=api_key.label,
        created_at=api_key.created_at,
    )


@router.get("", response_model=list[ApiKeyOut])
async def list_api_keys(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ApiKeyService(db)
    return await service.list_for_user(current_user)


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ApiKeyService(db)
    await service.delete(current_user, key_id)
    return None