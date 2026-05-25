from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy import select
import uuid

from app.dependencies.db import SessionDep
from app.dependencies.user import allow_staff
from app.models.product import Product
from app.models.product_type import ProductType
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductOut

router = APIRouter()


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_staff)])
async def create_product(product_in: ProductCreate, db: SessionDep):
    # Verify product type exists
    return await ProductRepository(db).create(product_in)


@router.get("/", response_model=list[ProductOut])
async def get_products(db: SessionDep, skip: int = 0, limit: int = 100):
    stmt = select(Product).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: uuid.UUID, db: SessionDep):
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_staff)])
async def delete_product(product_id: uuid.UUID, db: SessionDep):
    await ProductRepository(db).delete(product_id)
