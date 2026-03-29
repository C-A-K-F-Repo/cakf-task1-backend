"""Users routes."""

import datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.user import UserOut, UserUpdate, Role
from app.dependencies.user import UserDep, AdminDep

router = APIRouter()


@router.delete("/me")
async def delete_self(user: UserDep):
    return {"message": "Deleted self"}


@router.delete("/{id}")
async def delete_user(id: UUID) -> dict:
    """Delete a user by ID. Check permissions (owner or admin)."""
    # TODO: Implement - validate permissions and delete user
    return {"message": "User deleted"}


@router.put("/me")
async def update_self(user: UserDep, user_info: UserUpdate) -> UserOut:
    # TODO: get user from db, update fields, return updated user
    example_user = UserOut(
        full_name='fname',
        dob=datetime.datetime.now(),
        delivery_address="address",
        phone_number="+380963827104",
        email="me@example.com",
        id="1be872fb-e889-4d69-b5d3-3009a28c8ee5",
        role=Role.USER
    )
    return example_user


@router.put("/{id}")
async def update_user(id: UUID, user_info: UserUpdate) -> UserOut:
    """Update a user. Return updated user."""
    # TODO: Implement - validate permissions and update user
    # user = update_user_in_db(id, user_info.model_dump(exclude_unset=True))
    # return user
    example_user = UserOut(
        full_name='fname',
        dob=datetime.datetime.now(),
        delivery_address="address",
        phone_number="+380963827104",
        email="me@example.com",
        id="1be872fb-e889-4d69-b5d3-3009a28c8ee5",
        role=Role.USER
    )
    return example_user


@router.get("/me")
async def get_self(user: UserDep):
    # return user
    example_user = UserOut(
        full_name='fname',
        dob=datetime.datetime.now(),
        delivery_address="address",
        phone_number="+380963827104",
        email="me@example.com",
        id="1be872fb-e889-4d69-b5d3-3009a28c8ee5",
        role=Role.USER
    )
    return example_user


@router.get("/me/export")
async def export_user_data(user: UserDep):
    return "Your data"


@router.get("/{id}")
async def get_user(id: UUID, _: AdminDep) -> UserOut:
    """Get a user by ID."""
    # TODO: Implement - fetch user from database, admin check
    # user = get_user_from_db(id)
    # return user
    example_user = UserOut(
        full_name='fname',
        dob=datetime.datetime.now(),
        delivery_address="address",
        phone_number="+380963827104",
        email="me@example.com",
        id="1be872fb-e889-4d69-b5d3-3009a28c8ee5",
        role=Role.USER
    )
    return example_user
