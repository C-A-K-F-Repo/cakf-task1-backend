"""Schemas for account recovery endpoints."""

from pydantic import BaseModel, EmailStr, Field


class AccRecRequest(BaseModel):
    email: EmailStr


class AccRecReset(BaseModel):
    token: str = Field(min_length=16)
    new_password: str = Field(min_length=8)
