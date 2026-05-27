from pydantic import BaseModel, ConfigDict
import uuid


class ProductTypeBase(BaseModel):
    name: str


class ProductTypeCreate(ProductTypeBase):
    pass


class ProductTypeOut(ProductTypeBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)
