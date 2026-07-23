from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.auth_service import AuthService
from app.models.users import User
from app.schemas.user import (
    UserCreate,
    RegisterResponse,
    UserOut,
    Token,
    TokenRefreshRequest,
    AccessTokenResponse,
    LogoutRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, access_token = await service.register(user_in.email, user_in.password, user_in.full_name)
    return RegisterResponse(user=user, access_token=access_token)


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    access_token, refresh_token = await service.login(form_data.username, form_data.password)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(payload: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    new_access_token = await service.refresh(payload.refresh_token)
    return AccessTokenResponse(access_token=new_access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(payload.refresh_token)
    return None


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user