import io
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db, SessionDep
from app.dependencies.user import (
    allow_staff,
    allow_admin,
    get_current_user,
    get_current_active_user,
)
from app.models.user import User
from app.repositories.order import OrderRepository
from app.repositories.user import UserRepository
from app.schemas.user import (
    UserOut,
    ProfileUpdate,
    PasswordUpdate,
    EmailUpdateRequest,
    EmailUpdateVerify,
    PhoneUpdateRequest,
    PhoneUpdateVerify,
    UserCreate,
    UserInfo,
    UserUpdate,
)
from app.core.security import password_hash
from app.core.audit import audit_event, hash_identifier, mask_phone
from app.services.user_service import UserService


router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    audit_event("user.profile.read", "success", actor_user_id=current_user.id, actor_role=current_user.role.value)
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_profile(
    payload: ProfileUpdate,
    db: SessionDep,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    user_repo = UserRepository(db)
    update_data = payload.model_dump(exclude_unset=True)
    updated_user = await user_repo.update(current_user.id, **update_data)
    audit_event(
        "user.profile.update",
        "success",
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        target_type="user",
        target_id=current_user.id,
        metadata={"fields": sorted(update_data.keys())},
        request=request,
    )
    return updated_user


@router.post("/me/password", status_code=status.HTTP_200_OK)
async def set_my_password(
    payload: PasswordUpdate,
    db: SessionDep,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    if current_user.hashed_password is not None:
        if not payload.current_password or not password_hash.verify(
            payload.current_password, current_user.hashed_password
        ):
            audit_event(
                "user.password.update",
                "failure",
                actor_user_id=current_user.id,
                actor_role=current_user.role.value,
                target_type="user",
                target_id=current_user.id,
                metadata={"reason": "incorrect_current_password"},
                request=request,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
    await UserRepository(db).update_password_by_id(current_user.id, payload.new_password)
    audit_event(
        "user.password.update",
        "success",
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        target_type="user",
        target_id=current_user.id,
        request=request,
    )
    return {"message": "Password updated successfully"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    db: SessionDep,
    current_user: User = Depends(get_current_active_user)
):
    await UserRepository(db).delete(current_user.id)
    return None



@router.post("/me/email/request", status_code=status.HTTP_202_ACCEPTED)
async def request_email_update(
    payload: EmailUpdateRequest,
    db: SessionDep,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    user_service = UserService(db)
    await user_service.request_email_update(current_user, payload.new_email)
    audit_event(
        "user.email_update.request",
        "success",
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        target_type="user",
        target_id=current_user.id,
        metadata={"new_email_hash": hash_identifier(payload.new_email)},
        request=request,
    )
    return {"message": "Verification code sent to your new email"}


@router.post("/me/email/verify", status_code=status.HTTP_200_OK)
async def verify_email_update(
    payload: EmailUpdateVerify,
    db: SessionDep,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    user_service = UserService(db)
    await user_service.verify_email_update(current_user, payload.code)
    audit_event(
        "user.email_update.verify",
        "success",
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        target_type="user",
        target_id=current_user.id,
        request=request,
    )
    return {"message": "Email updated successfully"}


@router.post("/me/phone/request", status_code=status.HTTP_202_ACCEPTED)
async def request_phone_update(
    payload: PhoneUpdateRequest,
    db: SessionDep,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    user_service = UserService(db)
    await user_service.request_phone_update(current_user, payload.new_phone)
    audit_event(
        "user.phone_update.request",
        "success",
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        target_type="user",
        target_id=current_user.id,
        metadata={"new_phone": mask_phone(str(payload.new_phone))},
        request=request,
    )
    return {"message": "OTP sent to your new phone number"}


@router.post("/me/phone/verify", status_code=status.HTTP_200_OK)
async def verify_phone_update(
    payload: PhoneUpdateVerify,
    db: SessionDep,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    user_service = UserService(db)
    await user_service.verify_phone_update(current_user, payload.code)
    audit_event(
        "user.phone_update.verify",
        "success",
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        target_type="user",
        target_id=current_user.id,
        request=request,
    )
    return {"message": "Phone number updated successfully"}


@router.post("/create_user", status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_admin)])
async def create_user(user_data: UserCreate, request: Request, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user_repo = UserRepository(db)

    created_user = await user_repo.create(user_data)
    audit_event(
        "admin.user.create",
        "success",
        actor_user_id=current_user.get("sub"),
        actor_role=current_user.get("role"),
        target_type="user",
        target_id=created_user.id,
        metadata={"email_hash": hash_identifier(user_data.email), "role": created_user.role.value},
        request=request,
    )

    return {"message": f"User created sucesfully, user_id: {created_user.id}"}


@router.delete("/delete_user", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_admin)])
async def delete_user(user_id: UUID, request: Request, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user_repo = UserRepository(db)
    await user_repo.delete(user_id)
    audit_event(
        "admin.user.delete",
        "success",
        actor_user_id=current_user.get("sub"),
        actor_role=current_user.get("role"),
        target_type="user",
        target_id=user_id,
        request=request,
    )
    return None


@router.get("/get_user_info", response_model=UserInfo, dependencies=[Depends(allow_staff)])
async def get_user_info(user_id: UUID, request: Request, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        audit_event("staff.user.read", "failure", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="user", target_id=user_id, request=request)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")
    audit_event("staff.user.read", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="user", target_id=user_id, request=request)
    return user


@router.get("/get_all_users_info", response_model=List[UserInfo], dependencies=[Depends(allow_staff)])
async def get_all_users_info(request: Request, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user_repo = UserRepository(db)
    users = await user_repo.get_all(limit=limit, offset=offset)

    if not users:
        audit_event("staff.user.list", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"limit": limit, "offset": offset, "result_count": 0}, request=request)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not Found")
    audit_event("staff.user.list", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"limit": limit, "offset": offset, "result_count": len(users)}, request=request)
    return users


@router.patch("/update", response_model=UserInfo, dependencies=[Depends(allow_admin)])
async def update_user(user_id: UUID, user_data: UserUpdate, request: Request, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user_repo = UserRepository(db)
    updated_user = await user_repo.update(user_id, **user_data.model_dump(exclude_unset=True))

    if not updated_user:
        audit_event("admin.user.update", "failure", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="user", target_id=user_id, request=request)
        raise HTTPException(status_code=404, detail="User not found")

    audit_event(
        "admin.user.update",
        "success",
        actor_user_id=current_user.get("sub"),
        actor_role=current_user.get("role"),
        target_type="user",
        target_id=user_id,
        metadata={"fields": sorted(user_data.model_dump(exclude_unset=True).keys())},
        request=request,
    )

    return updated_user


@router.delete("/")
async def delete_self(password: str, db: SessionDep, request: Request, current_user=Depends(get_current_user)):
    user = await UserRepository(db).get_by_id(current_user["sub"])
    if not user:
        audit_event("user.self_delete", "failure", actor_user_id=current_user.get("sub"), metadata={"reason": "user_not_found"}, request=request)
        raise HTTPException(status_code=404, detail="User not found")
    if not user.hashed_password:
        audit_event("user.self_delete", "failure", actor_user_id=user.id, actor_role=user.role.value, metadata={"reason": "missing_password"}, request=request)
        raise HTTPException(status_code=400, detail="Set a password before deleting your account")
    if not password_hash.verify(password, user.hashed_password):
        audit_event("user.self_delete", "failure", actor_user_id=user.id, actor_role=user.role.value, metadata={"reason": "incorrect_password"}, request=request)
        raise HTTPException(status_code=400, detail="Incorrect password")

    await OrderRepository(db).delete_by_user(user.id)

    await UserRepository(db).delete(user.id)
    audit_event("user.self_delete", "success", actor_user_id=user.id, actor_role=user.role.value, target_type="user", target_id=user.id, request=request)


@router.get("/info")
async def get_info(db: SessionDep, request: Request, current_user=Depends(get_current_user)):
    user = await UserRepository(db).get_by_id_with_orders(current_user["sub"])
    if not user:
        audit_event("user.export", "failure", actor_user_id=current_user.get("sub"), metadata={"reason": "user_not_found"}, request=request)
        raise HTTPException(status_code=404, detail="User not found")

    audit_event("user.export", "success", actor_user_id=user.id, actor_role=user.role.value, target_type="user", target_id=user.id, metadata={"order_count": len(user.orders)}, request=request)

    content = f"User: {user.email}\n"
    content += f"Full name: {user.full_name}\n"
    content += f"Date of birth: {user.dob}\n"
    content += f"Role: {user.role.value}\n"
    content += f"Phone: {user.phone_number}\n"
    content += f"delivery_address: {user.delivery_address}\n"
    for order in user.orders:
        content += f"  Order: {order.id.hex}\n"
        for item in order.items:
            content += f"    Item: {item.product.name}\n"
            content += f"    Quantity: {item.quantity}\n"
            content += f"    Price: {item.product.price}\n"

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=user_info.txt"}
    )
