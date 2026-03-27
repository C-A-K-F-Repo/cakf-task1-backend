"""Account recovery endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.acc_rec import AccRecRequest, AccRecReset
from app.services.acc_rec_service import acc_rec_service

router = APIRouter()


@router.post("/request", status_code=status.HTTP_204_NO_CONTENT)
def request_recovery(payload: AccRecRequest) -> None:
    """Request account recovery token."""
    acc_rec_service.request_recovery(payload)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(payload: AccRecReset) -> None:
    """Reset password using recovery token."""
    try:
        acc_rec_service.reset_password(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
