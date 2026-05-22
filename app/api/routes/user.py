from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.dependencies.user import allow_staff,allow_admin
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate,UserBase
from uuid import  UUID

router = APIRouter()

@router.post("/create_user",status_code=status.HTTP_201_CREATED,dependencies=[Depends(allow_admin)])
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)

    created_user = await user_repo.create(user_data)

    return {"message": f"User created sucesfully, user_id: {created_user.id}"}


@router.delete("/delete_user", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_admin)])
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    deleted = await user_repo.delete(user_id)
    
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")
    return None

@router.get("/get_user_info",response_model= UserBase,dependencies=[Depends(allow_staff)])
async def get_info(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not Found")
    return user