from datetime import datetime, UTC
import logging

from app.core.db import SessionLocal
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

from app.services.email_notifications import email_service

logger = logging.getLogger(__name__)


async def notify_birthday():
    today = datetime.now(UTC).date()

    query = (
        select(User.email)
        .where(
            User.dob.isnot(None),
            extract("month", User.dob) == today.month,
            extract("day", User.dob) == today.day,
            User.is_active.is_(True),
        )
    )

    async with SessionLocal() as db:
        result = await db.execute(query)
    emails = result.scalars().all()

    logger.info(f"Today {len(emails)} users have birthday")

    for email in emails:
        await email_service.send_email(email, "Happy birthday", "Special offer for you")
