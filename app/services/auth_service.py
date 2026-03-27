"""Authentication service with registration business logic."""

import uuid

from app.core.security import hash_password
from app.repositories.auth_repository import StoredUser, auth_repository
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


auth_service = AuthService()
