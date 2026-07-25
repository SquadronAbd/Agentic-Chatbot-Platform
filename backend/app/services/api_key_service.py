import secrets
import hashlib
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.api_key_repository import ApiKeyRepository
from app.models.users import User


class ApiKeyService:
    def __init__(self, db: AsyncSession):
        self.repo = ApiKeyRepository(db)

    def _generate_key(self) -> tuple[str, str]:
        """Generate a raw key and its SHA-256 hash. Raw key shown once only."""
        raw_key = f"sk-{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return raw_key, key_hash

    async def create(self, current_user: User, label: str | None):
        raw_key, key_hash = self._generate_key()
        api_key = await self.repo.create(str(current_user.id), key_hash, label)
        return api_key, raw_key  # raw_key returned ONCE, never stored

    async def list_for_user(self, current_user: User):
        return await self.repo.list_by_user(str(current_user.id))

    async def delete(self, current_user: User, key_id: str) -> None:
        key = await self.repo.get_by_id(key_id)
        if key is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
        if str(key.user_id) != str(current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your API key")
        await self.repo.delete(key)