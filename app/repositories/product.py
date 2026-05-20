from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from starlette import status

from app.models import ProductType, Product
from app.schemas.product import ProductCreate


class ProductRepository:
    def __init__(self, db):
        self.db = db

    async def create(self, product_in: ProductCreate):
        try:
            stmt = select(ProductType).where(ProductType.id == product_in.product_type_id)
            result = await self.db.execute(stmt)
            product_type = result.scalar_one_or_none()
            if not product_type:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product_type_id")

            new_product = Product(
                name=product_in.name,
                price=product_in.price,
                product_type_id=product_in.product_type_id
            )
            self.db.add(new_product)
            await self.db.commit()
            await self.db.refresh(new_product)
            return new_product
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product with that name and type id already exists")
