from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
import uuid

from app.dependencies.db import SessionDep
from app.dependencies.user import allow_staff
from app.models.product_type import ProductType
from app.repositories.product_type import ProductTypeRepository
from app.schemas.product_type import ProductTypeCreate, ProductTypeOut

router = APIRouter()


@router.post("/", response_model=ProductTypeOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_staff)])
async def create_product_type(product_type_in: ProductTypeCreate, db: SessionDep):
    return await ProductTypeRepository(db).create(product_type_in)


@router.get("/", response_model=list[ProductTypeOut])
async def get_product_types(db: SessionDep, skip: int = 0, limit: int = 100):
    return await ProductTypeRepository(db).get(skip, limit)


@router.get("/{product_type_id}", response_model=ProductTypeOut)
async def get_product_type(product_type_id: uuid.UUID, db: SessionDep):
    return await ProductTypeRepository(db).get_by_id(product_type_id)


@router.delete("/{product_type_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_staff)])
async def delete_product_type(product_type_id: uuid.UUID, db: SessionDep):
    await ProductTypeRepository(db).delete(product_type_id)
