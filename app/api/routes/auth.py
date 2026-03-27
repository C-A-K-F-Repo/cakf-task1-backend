"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserCreate, UserOut
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate) -> UserOut:
    """Register a new user."""
    try:
        return auth_service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
