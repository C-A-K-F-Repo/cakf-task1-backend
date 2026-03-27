"""In-memory repository for password recovery tokens."""

from dataclasses import dataclass
from datetime import datetime
from threading import Lock


@dataclass
class RecoveryTokenRecord:
    token: str
    email: str
    expires_at: datetime


class InMemoryAccountRecoveryRepository:
    """Thread-safe storage for account recovery tokens."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._tokens: dict[str, RecoveryTokenRecord] = {}

    def upsert_for_email(self, email: str, token: str, expires_at: datetime) -> None:
        """Store one active token per email and remove previous token records."""
        email_key = email.lower()
        with self._lock:
            old_token = None
            for key, record in self._tokens.items():
                if record.email == email_key:
                    old_token = key
                    break
            if old_token is not None:
                del self._tokens[old_token]
            self._tokens[token] = RecoveryTokenRecord(
                token=token,
                email=email_key,
                expires_at=expires_at,
            )

    def get(self, token: str) -> RecoveryTokenRecord | None:
        with self._lock:
            return self._tokens.get(token)

    def delete(self, token: str) -> None:
        with self._lock:
            self._tokens.pop(token, None)


acc_rec_repository = InMemoryAccountRecoveryRepository()
