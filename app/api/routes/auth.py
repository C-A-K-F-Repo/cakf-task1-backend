"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends

from app.core.db import SessionDep
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: SessionDep) -> RegisterResponse:
    """Register a new user."""
    try:
        return await auth_service.register_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: SessionDep) -> TokenResponse:
    """Authenticate a user and return a bearer token."""
    try:
        return await auth_service.login_user(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
