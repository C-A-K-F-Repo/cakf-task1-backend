from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.db import SessionDep
from app.dependencies.user import get_current_user, allow_staff
from app.repositories import UserRepository
from app.schemas.auth import RegisterRequest, RegisterResponse, TokenResponse
from app.schemas.user import UserOut, UserCreate
from app.services.auth_service import auth_service
from app.core.security import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token
)

from app.schemas.google_oauth import CallbackPayload, UserInfoResponse
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from app.core.config import settings
from app.dependencies.user import allow_admin
from app.services.email_notifications import email_service

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: SessionDep, background_tasks: BackgroundTasks) -> RegisterResponse:
    """Register a new user."""
    try:
        background_tasks.add_task(email_service.send_verification_email, payload.email)
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
async def refresh(db: SessionDep, refresh_token: str):
    try:
        payload = verify_refresh_token(refresh_token)

        # TODO: blacklist `refresh_token` in redis to prevent replaying

        user = await UserRepository(db).get_by_id(payload["sub"])
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        access_token = create_access_token({"sub": payload["sub"], "role": user.role.value})
        refresh_token = create_refresh_token({"sub": payload["sub"]})

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me", response_model=UserOut)
async def get_me(db: SessionDep, current_user = Depends(get_current_user)):
    user = await UserRepository(db).get_by_id(current_user["sub"])
    return user


@router.get("/staff-only", dependencies=[Depends(allow_staff)])
async def staff_only():
    return {"message": "Accessed as admin"}

@router.post("/email/verify")
async def verify_email(token: str, db: SessionDep):
    result = await email_service.verify_token(db, token)
    if not result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="failed to verify email")
    return {"message": "Email verified"}


@router.get("/email/request")
async def get_verify_email(db: SessionDep, background_tasks: BackgroundTasks,
                           current_user = Depends(get_current_user)):
    background_tasks.add_task(email_service.send_verification_email, current_user["email"])
    return {"message": "Email verification sent"}


@router.post("/google/callback")
async def google_callback(db: SessionDep, payload: CallbackPayload):
    try:
        id_info = id_token.verify_oauth2_token(
            payload.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        validated_info = UserInfoResponse.model_validate(id_info)

        print(validated_info)

        if not validated_info.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified"
            )

        existing_user = await UserRepository(db).get_by_email(validated_info.email)

        if existing_user is None:
            user = await UserRepository(db).create_from_oauth(validated_info.email)
        else:
            user = existing_user

        access_token = create_access_token({"sub": str(user.id), "email": validated_info.email, "role": user.role.value})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except GoogleAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
