"""Authentication service with registration and login business logic."""

from datetime import datetime, timedelta, timezone
import secrets
import uuid

from app.core.security import hash_password, verify_password
from app.repositories.auth_repository import StoredUser, auth_repository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import Role, UserCreate, UserOut


class AuthService:
    """Service layer for auth-related use-cases."""

    def register_user(self, payload: UserCreate) -> UserOut:
        email_key = str(payload.email).lower()

        if auth_repository.get_by_email(email_key) is not None:
            raise ValueError("User with this email already exists")

        salt_hex, password_hash_hex = hash_password(payload.password)
        stored = StoredUser(
            id=uuid.uuid4(),
            full_name=payload.full_name,
            dob=payload.dob,
            delivery_address=payload.delivery_address,
            phone_number=str(payload.phone_number),
            email=email_key,
            role=payload.role or Role.USER,
            salt_hex=salt_hex,
            password_hash_hex=password_hash_hex,
        )

        auth_repository.add_user(stored)

        return UserOut(
            id=stored.id,
            full_name=stored.full_name,
            dob=stored.dob,
            delivery_address=stored.delivery_address,
            phone_number=stored.phone_number,
            email=stored.email,
            role=stored.role,
        )

    def login_user(self, payload: LoginRequest) -> TokenResponse:
        email_key = str(payload.email).lower()
        stored_user = auth_repository.get_by_email(email_key)

        if stored_user is None or not verify_password(
            payload.password,
            stored_user.salt_hex,
            stored_user.password_hash_hex,
        ):
            raise ValueError("Invalid email or password")

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=1)
        auth_repository.store_token(email_key, token, expires_at)

        return TokenResponse(access_token=token)


auth_service = AuthService()
