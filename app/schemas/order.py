from pydantic import BaseModel
import uuid
import datetime


class OrderBase(BaseModel):
    user_id: uuid.UUID
    date: datetime.datetime
    product_type: str
    quantity: int


class OrderIn(OrderBase):
    pass


class OrderOut(OrderBase):
    id: uuid.UUID
