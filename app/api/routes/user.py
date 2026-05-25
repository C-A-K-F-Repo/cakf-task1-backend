from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.dependencies.db import get_db, SessionDep
from app.dependencies.user import allow_staff, allow_admin, get_current_user
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserInfo, UserUpdate
from uuid import UUID
from app.core.security import password_hash

router = APIRouter()


@router.post("/create_user", status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_admin)])
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)

    created_user = await user_repo.create(user_data)

    return {"message": f"User created sucesfully, user_id: {created_user.id}"}


@router.delete("/delete_user", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_admin)])
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    await user_repo.delete(user_id)
    return None


@router.get("/get_user_info", response_model=UserInfo, dependencies=[Depends(allow_staff)])
async def get_user_info(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")
    return user


@router.get("/get_all_users_info", response_model=List[UserInfo], dependencies=[Depends(allow_staff)])
async def get_all_users_info(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    users = await user_repo.get_all(limit=limit, offset=offset)

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not Found")
    return users


@router.patch("/update", response_model=UserInfo, dependencies=[Depends(allow_admin)])
async def update_user(user_id: UUID, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    updated_user = await user_repo.update(user_id, user_data.model_dump(exclude_unset=True))

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user


@router.delete("/")
async def delete_self(password: str, db: SessionDep, current_user=Depends(get_current_user)):
    user = await UserRepository(db).get_by_id(current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not password_hash.verify(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    await UserRepository(db).delete(user.id)
