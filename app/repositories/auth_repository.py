"""In-memory repository for authentication users."""

from dataclasses import dataclass
from datetime import datetime
from threading import Lock
import uuid

from app.schemas.user import Role


@dataclass
class StoredUser:
    id: uuid.UUID
    full_name: str
    dob: datetime
    delivery_address: str
    phone_number: str
    email: str
    role: Role
    salt_hex: str
    password_hash_hex: str


class InMemoryAuthRepository:
    """Thread-safe in-memory repository for users."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._users_by_email: dict[str, StoredUser] = {}

    def add_user(self, user: StoredUser) -> None:
        """Persist user, raising if email already exists."""
        with self._lock:
            if user.email in self._users_by_email:
                raise ValueError("User with this email already exists")
            self._users_by_email[user.email] = user

    def get_by_email(self, email: str) -> StoredUser | None:
        """Return stored user by email or None."""
        with self._lock:
            return self._users_by_email.get(email.lower())

    def update_password(self, email: str, salt_hex: str, password_hash_hex: str) -> bool:
        """Update password hash for user by email. Returns False if user does not exist."""
        email_key = email.lower()
        with self._lock:
            stored_user = self._users_by_email.get(email_key)
            if stored_user is None:
                return False
            stored_user.salt_hex = salt_hex
            stored_user.password_hash_hex = password_hash_hex
            return True


auth_repository = InMemoryAuthRepository()
