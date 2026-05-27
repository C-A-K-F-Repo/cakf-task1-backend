import datetime
import uuid
from pydantic import BaseModel, ConfigDict
from app.schemas.product import ProductOut


class OrderItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderItemOut(OrderItemBase):
    product: ProductOut


class OrderBase(BaseModel):
    pass


class OrderIn(OrderBase):
    items: list[OrderItemBase]


class OrderOut(OrderBase):
    id: uuid.UUID
    user_id: uuid.UUID
    items: list[OrderItemOut]
    date: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class OrderAdminOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_email: str | None = None
    user_full_name: str | None = None
    items: list[OrderItemOut]
    date: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
