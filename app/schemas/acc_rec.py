"""Schemas for account recovery endpoints."""

from pydantic import BaseModel, EmailStr, Field


class AccRecRequest(BaseModel):
    email: EmailStr


class AccRecReset(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(min_length=8)
