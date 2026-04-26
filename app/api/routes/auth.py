"""Authentication endpoints."""
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.db import SessionDep
from app.dependencies.user import get_current_user
from app.models import User
from app.repositories import UserRepository
from app.schemas.auth import RegisterRequest, RegisterResponse, TokenResponse
from app.schemas.user import UserOut
from app.services.auth_service import auth_service
from app.core.security import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token
)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: SessionDep) -> RegisterResponse:
    """Register a new user."""
    try:
        return await auth_service.register_user(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
async def login(payload: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep) -> TokenResponse:
    """Authenticate a user and return a bearer token."""
    try:
        return await auth_service.login_user(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/refresh")
async def refresh(refresh_token: str):
    try:
        payload = verify_refresh_token(refresh_token)

        # TODO: blacklist `refresh_token` in redis to prevent replaying

        access_token = create_access_token({"sub": payload["sub"]})
        refresh_token = create_refresh_token({"sub": payload["sub"]})

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me", response_model=UserOut)
async def get_me(db: SessionDep, current_user: str = Depends(get_current_user)):
    user = await UserRepository(db).get_by_id(current_user)
    return user
