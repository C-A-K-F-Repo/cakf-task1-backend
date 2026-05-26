from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from uuid import UUID

from starlette import status

from app.models.product_type import ProductType
from app.schemas.product_type import ProductTypeCreate


class ProductTypeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_type_id: UUID | str) -> ProductType | None:
        """Get product_type by ID."""
        stmt = select(ProductType).where(ProductType.id == product_type_id)
        result = await self.db.execute(stmt)
        product_type = result.scalar_one_or_none()
        if not product_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product type not found")
        return product_type


    async def get(self, skip: int = 0, limit: int = 100):
        limit = min(limit, 100)
        stmt = select(ProductType).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def create(self, product_type: ProductTypeCreate):
        try:
            new_product_type = ProductType(**product_type.model_dump())
            self.db.add(new_product_type)
            await self.db.commit()
            await self.db.refresh(new_product_type)
            return new_product_type
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product type already exists")

    async def delete(self, product_type_id: UUID | str) -> None:
        await self.db.execute(delete(ProductType).where(ProductType.id == product_type_id))
        await self.db.commit()
