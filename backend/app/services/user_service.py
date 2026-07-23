from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.models.users import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user(self, email: str, password: str, full_name: str | None, role: str) -> User:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists",
            )
        return await self.repo.create(email, hash_password(password), full_name, role)

    async def list_users(self) -> list[User]:
        return await self.repo.list_all()

    async def delete_user(self, user_id: str, current_user: User) -> None:
        if str(user_id) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account",
            )
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self.repo.delete(user)