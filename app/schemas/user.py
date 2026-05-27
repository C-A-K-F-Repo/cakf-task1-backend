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


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    dob: Optional[datetime.date] = None
    delivery_address: Optional[str] = None
    phone_number: Optional[str] = None
    role: Role
    has_password: bool = False

    model_config = ConfigDict(from_attributes=True)


class PasswordUpdate(BaseModel):
    current_password: Optional[str] = None
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_complexity(cls, value: str) -> str:
        has_letter = any(ch.isalpha() for ch in value)
        has_special = any(not ch.isalnum() for ch in value)
        if not has_letter or not has_special:
            raise ValueError("Password must contain at least one letter and one special character")
        return value


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[datetime.date] = None
    delivery_address: Optional[str] = None


class EmailUpdateRequest(BaseModel):
    new_email: EmailStr


class EmailUpdateVerify(BaseModel):
    code: str


class PhoneUpdateRequest(BaseModel):
    new_phone: Annotated[PhoneNumber, PhoneNumberValidator(number_format="E164")]


class PhoneUpdateVerify(BaseModel):
    code: str


class UserInfo(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    role: Role
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    role: Role | None = None
