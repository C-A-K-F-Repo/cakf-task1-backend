from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional


class Role(Enum):
    USER = "User"
    ADVANCED_USER = "Advanced_User"
    ADMINISTRATOR = "Administrator"


class UserBase(BaseModel):
    full_name: str
    dob: datetime
    delivery_address: str
    phone_number: PhoneNumber
    email: EmailStr


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[datetime] = None
    delivery_address: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str

    role: Role = Role.USER


class UserOut(UserBase):
    id: UUID
    role: Role


class UserInDb(UserOut):
    pass
