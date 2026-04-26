from pydantic import BaseModel, EmailStr
import datetime
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from enum import Enum
from typing import Optional, Annotated
import uuid


class Role(Enum):
    USER = "User"
    ADVANCED_USER = "Advanced_User"
    ADMINISTRATOR = "Administrator"


class UserBase(BaseModel):
    full_name: str
    dob: datetime.datetime
    delivery_address: str
    phone_number: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]
    email: EmailStr


class UserCreate(UserBase):
    password: str

    role: Optional[Role] = Role.USER


class UserOut(UserBase):
    id: uuid.UUID
    role: Role
