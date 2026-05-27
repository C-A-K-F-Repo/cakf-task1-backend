"""Account recovery endpoints."""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Request

from app.core.audit import audit_event, hash_identifier
from app.dependencies.db import SessionDep
from app.schemas.acc_rec import AccRecRequest, AccRecReset
from app.services.acc_rec_service import acc_rec_service

router = APIRouter()


@router.post("/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_recovery(payload: AccRecRequest, db: SessionDep, background_tasks: BackgroundTasks, request: Request) -> None:
    """Request account recovery token."""
    try:
        await acc_rec_service.request_recovery(payload, db, background_tasks)
        audit_event("account_recovery.request", "success", metadata={"email_hash": hash_identifier(payload.email)}, request=request)
    except HTTPException as exc:
        audit_event("account_recovery.request", "failure", metadata={"email_hash": hash_identifier(payload.email), "reason": exc.detail}, request=request)
        raise


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(payload: AccRecReset, db: SessionDep, request: Request) -> None:
    """Reset password using recovery token."""
    try:
        await acc_rec_service.reset_password(payload, db)
        audit_event("account_recovery.reset", "success", metadata={"email_hash": hash_identifier(payload.email)}, request=request)
    except HTTPException as exc:
        audit_event("account_recovery.reset", "failure", metadata={"email_hash": hash_identifier(payload.email), "reason": exc.detail}, request=request)
        raise
    except ValueError as exc:
        audit_event("account_recovery.reset", "failure", metadata={"email_hash": hash_identifier(payload.email), "reason": str(exc)}, request=request)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
