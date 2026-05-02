"""Business logic for account recovery flows."""

from datetime import datetime, timedelta, timezone
import secrets
from fastapi import HTTPException, BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import UserRepository
from app.repositories.acc_rec_repository import acc_rec_repository
from app.schemas.acc_rec import AccRecRequest, AccRecReset
from app.services.email_notifications import email_service


class AccountRecoveryService:
    """Service layer for account recovery use-cases."""

    @staticmethod
    async def request_recovery(payload: AccRecRequest, db: AsyncSession, background_tasks: BackgroundTasks) -> None:
        existing_user = await UserRepository(db).get_by_email(payload.email)

        if existing_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        background_tasks.add_task(email_service.send_recovery_email, payload.email)

    @staticmethod
    async def reset_password(payload: AccRecReset, db: AsyncSession) -> None:
        await email_service.verify(payload.email, payload.code)

        await UserRepository(db).update_password(
            email=payload.email,
            new_password=payload.new_password
        )


acc_rec_service = AccountRecoveryService()
