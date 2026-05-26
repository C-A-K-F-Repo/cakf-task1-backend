import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

from app.dependencies.db import get_db
from app.dependencies.user import allow_staff
from app.repositories.user import UserRepository
from app.services.email_notifications import email_service
from app.services.sms import SmsService
from app.schemas.notification import NotificationRequest

router = APIRouter()
logger = logging.getLogger(__name__)
sms_service = SmsService()


@router.post("/email", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(allow_staff)], summary="Send email")
async def notify_email(request: NotificationRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    notification = request.notification

    user_ids = request.user_ids

    emails = []
    if user_ids is not None:
        emails = await user_repo.get_emails_by_ids(user_ids)
    else:
        emails = await user_repo.get_all_emails()

    if not emails:
        return {"message": "No users found to notify"}

    tasks = []

    for email in emails:
        tasks.append(email_service.send_email(email, notification.subject, notification.content))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    has_errors = False

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Notification task {i} failed: {result}")
            has_errors = True

    if has_errors:
        return {"message": "Some notifications failed"}

    return {"message": f"Notifications sent to {len(emails)} users"}


@router.post("/sms", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(allow_staff)], summary="Send SMS")
async def notify_sms(request: NotificationRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    notification = request.notification
    
    user_ids = request.user_ids

    phones = []

    if user_ids is not None:
        phones = await user_repo.get_phone_numbers_by_ids(user_ids)
    else:
        phones = await user_repo.get_all_phone_numbers()

    if not phones:
        return {"message": "No users found to notify"}

    tasks = []

    for phone in phones:
        tasks.append(sms_service.send_msg(phone, request.notification.content))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    has_errors = False

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Notification task {i} failed: {result}")
            has_errors = True

    if has_errors:
        return {"message": "Some notifications failed"}

    return {"message": f"Notifications sent to {len(phones)} users"}
