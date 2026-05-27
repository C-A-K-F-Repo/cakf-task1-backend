import uuid

from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import logging

from app.dependencies.db import get_db
from app.dependencies.user import allow_staff, get_current_user
from app.core.audit import audit_event
from app.repositories.user import UserRepository
from app.services.email_notifications import email_service
from app.services.sms import SmsService
from app.schemas.notification import NotificationRequest

router = APIRouter()
logger = logging.getLogger(__name__)
sms_service = SmsService()


@router.post("/email", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(allow_staff)], summary="Send email")
async def notify_email(request: NotificationRequest, http_request: Request, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    user_repo = UserRepository(db)
    notification = request.notification

    user_ids = request.user_ids

    emails = []
    if user_ids is not None:
        emails = await user_repo.get_emails_by_ids(user_ids)
    else:
        emails = await user_repo.get_all_emails()

    if not emails:
        audit_event("notification.email.send", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"targeting": "selected" if user_ids is not None else "all", "requested_count": len(user_ids or []), "resolved_count": 0}, request=http_request)
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
        audit_event("notification.email.send", "partial_failure", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"targeting": "selected" if user_ids is not None else "all", "requested_count": len(user_ids or []), "resolved_count": len(emails), "failure_count": sum(1 for result in results if isinstance(result, Exception))}, request=http_request)
        return {"message": "Some notifications failed"}

    audit_event("notification.email.send", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"targeting": "selected" if user_ids is not None else "all", "requested_count": len(user_ids or []), "resolved_count": len(emails)}, request=http_request)
    return {"message": f"Notifications sent to {len(emails)} users"}


@router.post("/sms", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(allow_staff)], summary="Send SMS")
async def notify_sms(request: NotificationRequest, http_request: Request, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    user_repo = UserRepository(db)
    notification = request.notification
    
    user_ids = request.user_ids

    phones = []

    if user_ids is not None:
        phones = await user_repo.get_phone_numbers_by_ids(user_ids)
    else:
        phones = await user_repo.get_all_phone_numbers()

    if not phones:
        audit_event("notification.sms.send", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"targeting": "selected" if user_ids is not None else "all", "requested_count": len(user_ids or []), "resolved_count": 0}, request=http_request)
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
        audit_event("notification.sms.send", "partial_failure", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"targeting": "selected" if user_ids is not None else "all", "requested_count": len(user_ids or []), "resolved_count": len(phones), "failure_count": sum(1 for result in results if isinstance(result, Exception))}, request=http_request)
        return {"message": "Some notifications failed"}

    audit_event("notification.sms.send", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"targeting": "selected" if user_ids is not None else "all", "requested_count": len(user_ids or []), "resolved_count": len(phones)}, request=http_request)
    return {"message": f"Notifications sent to {len(phones)} users"}
