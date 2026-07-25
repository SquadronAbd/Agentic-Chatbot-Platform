from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.api_keys import ApiKey


class ApiKeyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: str, key_hash: str, label: str | None) -> ApiKey:
        api_key = ApiKey(user_id=user_id, key_hash=key_hash, label=label)
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    async def list_by_user(self, user_id: str) -> list[ApiKey]:
        result = await self.db.execute(select(ApiKey).where(ApiKey.user_id == user_id))
        return list(result.scalars().all())

    async def get_by_id(self, key_id: str) -> ApiKey | None:
        result = await self.db.execute(select(ApiKey).where(ApiKey.id == key_id))
        return result.scalar_one_or_none()

    async def delete(self, api_key: ApiKey) -> None:
        await self.db.delete(api_key)
        await self.db.commit()