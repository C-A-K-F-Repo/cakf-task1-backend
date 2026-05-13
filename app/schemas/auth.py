"""Schemas for authentication endpoints."""

from pydantic import BaseModel, EmailStr

from app.schemas.user import UserCreate, UserOut


class RegisterRequest(UserCreate):
	"""Request payload for user registration."""


class RegisterResponse(UserOut):
	"""Response model for successful registration."""


class TokenResponse(BaseModel):
	"""Response payload with bearer token."""

	access_token: str
	refresh_token: str
	token_type: str = "bearer"

