"""Business logic for account recovery flows."""

from datetime import datetime, timedelta, timezone
import secrets

from app.core.security import hash_password
from app.repositories.acc_rec_repository import acc_rec_repository
from app.repositories.auth_repository import auth_repository
from app.schemas.acc_rec import AccRecRequest, AccRecReset


class AccountRecoveryService:
    """Service layer for account recovery use-cases."""

    def request_recovery(self, payload: AccRecRequest) -> None:
        email_key = str(payload.email).lower()

        # Do not disclose whether user exists.
        if auth_repository.get_by_email(email_key) is None:
            return

        token = secrets.token_urlsafe(24)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        acc_rec_repository.upsert_for_email(
            email=email_key,
            token=token,
            expires_at=expires_at,
        )

        # Placeholder for email delivery in this in-memory task implementation.

    def reset_password(self, payload: AccRecReset) -> None:
        token_record = acc_rec_repository.get(payload.token)
        if token_record is None:
            raise ValueError("Invalid recovery token")

        if token_record.expires_at < datetime.now(tz=timezone.utc):
            acc_rec_repository.delete(payload.token)
            raise ValueError("Recovery token expired")

        salt_hex, password_hash_hex = hash_password(payload.new_password)
        is_updated = auth_repository.update_password(
            email=token_record.email,
            salt_hex=salt_hex,
            password_hash_hex=password_hash_hex,
        )
        if not is_updated:
            acc_rec_repository.delete(payload.token)
            raise ValueError("User not found")

        acc_rec_repository.delete(payload.token)


acc_rec_service = AccountRecoveryService()
