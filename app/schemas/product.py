from pydantic import BaseModel, ConfigDict
import uuid


class ProductBase(BaseModel):
    name: str
    price: float
    product_type_id: uuid.UUID
    description: str | None = None


class ProductCreate(BaseModel):
    name: str
    price: float
    product_type_id: uuid.UUID
    description: str | None = None

class ProductOut(ProductBase):
    id: uuid.UUID
    image_url: str | None = None
    
    model_config = ConfigDict(from_attributes=True)
