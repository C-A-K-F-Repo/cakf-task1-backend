from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
import datetime
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from enum import StrEnum
from typing import Optional, Annotated
import uuid


class Role(StrEnum):
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
    password: str | None = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        has_letter = any(ch.isalpha() for ch in value)
        has_special = any(not ch.isalnum() for ch in value)
        if not has_letter or not has_special:
            raise ValueError("Password must contain at least one letter and one special character")
        return value

    role: Optional[Role] = Role.USER


class UserOut(UserBase):
    id: uuid.UUID
    role: Role

    model_config = ConfigDict(from_attributes=True)
