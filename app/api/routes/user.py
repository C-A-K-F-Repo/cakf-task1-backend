from fastapi import APIRouter, Depends, status
from app.dependencies.db import SessionDep
from app.dependencies.user import get_current_active_user
from app.models.user import User
from app.schemas.user import (
    UserOut, 
    ProfileUpdate, 
    EmailUpdateRequest, 
    EmailUpdateVerify,
    PhoneUpdateRequest,
    PhoneUpdateVerify
)
from app.services.user_service import UserService
from app.repositories.user import UserRepository

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_profile(
    payload: ProfileUpdate,
    db: SessionDep,
    current_user: User = Depends(get_current_active_user)
):
    user_repo = UserRepository(db)
    update_data = payload.model_dump(exclude_unset=True)
    updated_user = await user_repo.update(current_user.id, **update_data)
    return updated_user


@router.post("/me/email/request", status_code=status.HTTP_202_ACCEPTED)
async def request_email_update(
    payload: EmailUpdateRequest,
    db: SessionDep,
    current_user: User = Depends(get_current_active_user)
):
    user_service = UserService(db)
    await user_service.request_email_update(current_user, payload.new_email)
    return {"message": "Verification code sent to your new email"}


@router.post("/me/email/verify", status_code=status.HTTP_200_OK)
async def verify_email_update(
    payload: EmailUpdateVerify,
    db: SessionDep,
    current_user: User = Depends(get_current_active_user)
):
    user_service = UserService(db)
    await user_service.verify_email_update(current_user, payload.code)
    return {"message": "Email updated successfully"}


@router.post("/me/phone/request", status_code=status.HTTP_202_ACCEPTED)
async def request_phone_update(
    payload: PhoneUpdateRequest,
    db: SessionDep,
    current_user: User = Depends(get_current_active_user)
):
    user_service = UserService(db)
    await user_service.request_phone_update(current_user, payload.new_phone)
    return {"message": "OTP sent to your new phone number"}


@router.post("/me/phone/verify", status_code=status.HTTP_200_OK)
async def verify_phone_update(
    payload: PhoneUpdateVerify,
    db: SessionDep,
    current_user: User = Depends(get_current_active_user)
):
    user_service = UserService(db)
    await user_service.verify_phone_update(current_user, payload.code)
    return {"message": "Phone number updated successfully"}
