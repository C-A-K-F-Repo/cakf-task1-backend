from pydantic import BaseModel, ConfigDict
import uuid


class ProductBase(BaseModel):
    name: str
    price: float
    product_type_id: uuid.UUID


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
