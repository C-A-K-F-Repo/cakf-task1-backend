"""Authentication service with registration and login business logic."""
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import password_hash
from app.repositories import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import Role, UserCreate, UserOut
from app.core.security import create_access_token, create_refresh_token


class AuthService:
    """Service layer for auth-related use-cases."""

    @staticmethod
    async def register_user(db: AsyncSession, payload: UserCreate) -> UserOut:
        if await UserRepository(db).get_by_email(payload.email) is not None:
            raise ValueError("User with this email already exists")

        new_user = await UserRepository(db).create(payload)

        return UserOut.model_validate(new_user)

    @staticmethod
    async def login_user(db: AsyncSession, payload: OAuth2PasswordRequestForm) -> TokenResponse:
        stored_user = await UserRepository(db).get_by_email(payload.username)

        if stored_user is None or not password_hash.verify(
                payload.password, stored_user.hashed_password
        ):
            raise ValueError("Invalid email or password")

        access_token = create_access_token({"sub": str(stored_user.id), "role": stored_user.role.value})
        refresh_token = create_refresh_token({"sub": str(stored_user.id)})

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


auth_service = AuthService()
