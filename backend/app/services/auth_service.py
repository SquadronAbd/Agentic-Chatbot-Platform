from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_remaining_seconds,
)
from app.core.redis_client import blocklist_token, is_token_blocklisted
from app.repositories.user_repository import UserRepository
from app.models.users import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, email: str, password: str, full_name: str | None) -> tuple[User, str]:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists",
            )

        user = await self.repo.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role="agent",  # public registration can never grant admin/manager
        )
        access_token = create_access_token({"sub": str(user.id), "role": user.role})
        return user, access_token

    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self.repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated",
            )

        token_data = {"sub": str(user.id), "role": user.role}
        return create_access_token(token_data), create_refresh_token(token_data)

    async def refresh(self, refresh_token: str) -> str:
        decoded = decode_token(refresh_token)
        if decoded is None or decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        jti = decoded.get("jti")
        if jti and await is_token_blocklisted(jti):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This token has been revoked")

        user = await self.repo.get_by_id(decoded.get("sub"))
        if user is None or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer valid")

        return create_access_token({"sub": str(user.id), "role": user.role})

    async def logout(self, refresh_token: str) -> None:
        decoded = decode_token(refresh_token)
        if decoded is None or decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        jti = decoded.get("jti")
        if jti:
            await blocklist_token(jti, get_token_remaining_seconds(decoded))