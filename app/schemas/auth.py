"""Schemas for authentication endpoints."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserCreate, UserOut


class RegisterRequest(UserCreate):
	"""Request payload for user registration."""


class RegisterResponse(UserOut):
	"""Response model for successful registration."""


class LoginRequest(BaseModel):
	"""Request payload for login endpoint."""

	email: EmailStr
	password: str = Field(min_length=8)


class TokenResponse(BaseModel):
	"""Response payload with bearer token."""

	access_token: str
	token_type: str = "bearer"

