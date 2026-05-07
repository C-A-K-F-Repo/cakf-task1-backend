"""Account recovery endpoints."""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks

from app.dependencies.db import SessionDep
from app.schemas.acc_rec import AccRecRequest, AccRecReset
from app.services.acc_rec_service import acc_rec_service

router = APIRouter()


@router.post("/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_recovery(payload: AccRecRequest, db: SessionDep, background_tasks: BackgroundTasks) -> None:
    """Request account recovery token."""
    await acc_rec_service.request_recovery(payload, db, background_tasks)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(payload: AccRecReset, db: SessionDep) -> None:
    """Reset password using recovery token."""
    try:
        await acc_rec_service.reset_password(payload, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
