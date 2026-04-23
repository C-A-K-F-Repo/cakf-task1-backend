"""Business logic for account recovery flows."""

from datetime import datetime, timedelta, timezone
import secrets
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import UserRepository
from app.repositories.acc_rec_repository import acc_rec_repository
from app.schemas.acc_rec import AccRecRequest, AccRecReset


class AccountRecoveryService:
    """Service layer for account recovery use-cases."""

    async def request_recovery(self, payload: AccRecRequest, db: AsyncSession) -> None:
        email_key = str(payload.email).lower()

        existing_user = await UserRepository(db).get_by_email(email_key)

        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        token = secrets.token_urlsafe(24)
        expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
        acc_rec_repository.upsert_for_email(
            email=email_key,
            token=token,
            expires_at=expires_at,
        )

        # Placeholder for email delivery in this in-memory task implementation.

    async def reset_password(self, payload: AccRecReset, db: AsyncSession) -> None:
        token_record = acc_rec_repository.get(payload.token)
        if token_record is None:
            raise ValueError("Invalid recovery token")

        if token_record.expires_at < datetime.now(tz=timezone.utc):
            acc_rec_repository.delete(payload.token)
            raise ValueError("Recovery token expired")

        await UserRepository(db).update_password(
            email=token_record.email,
            new_password=payload.new_password
        )

        acc_rec_repository.delete(payload.token)


acc_rec_service = AccountRecoveryService()
