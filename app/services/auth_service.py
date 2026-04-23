"""Authentication service with registration and login business logic."""

from datetime import datetime, timedelta, timezone
import secrets
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import password_hash
from app.repositories import UserRepository
from app.repositories.auth_repository import StoredUser, auth_repository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import Role, UserCreate, UserOut


class AuthService:
    """Service layer for auth-related use-cases."""

    async def register_user(self, db: AsyncSession, payload: UserCreate) -> UserOut:
        email_key = str(payload.email).lower()

        if await UserRepository(db).get_by_email(email_key) is not None:
            raise ValueError("User with this email already exists")

        new_user = await UserRepository(db).create(payload)

        return UserOut(
            id=new_user.id,
            full_name=new_user.full_name,
            dob=new_user.dob,
            delivery_address=new_user.delivery_address,
            phone_number=new_user.phone_number,
            email=new_user.email,
            role=new_user.role,
        )

    async def login_user(self, db: AsyncSession, payload: UserCreate) -> TokenResponse:
        email_key = str(payload.email).lower()
        stored_user = await UserRepository(db).get_by_email(email_key)

        if stored_user is None or not password_hash.verify(
                payload.password, stored_user.hashed_password
        ):
            raise ValueError("Invalid email or password")

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        auth_repository.store_token(email_key, token, expires_at)

        return TokenResponse(access_token=token)


auth_service = AuthService()
