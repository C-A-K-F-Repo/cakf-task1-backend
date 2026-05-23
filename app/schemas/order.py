from pydantic import BaseModel, ConfigDict
import uuid
import datetime


class OrderItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    pass


class OrderIn(OrderBase):
    items: list[OrderItemBase]


class OrderOut(OrderBase):
    id: uuid.UUID
    user_id: uuid.UUID
    items: list[OrderItemBase]

    model_config = ConfigDict(from_attributes=True)
