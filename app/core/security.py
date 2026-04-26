from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

from datetime import datetime, UTC, timedelta
from typing import Literal
from app.core.config import settings

import jwt

ALGORITHM = "HS256"

TokenType = Literal["access", "refresh"]


def _create_token(data: dict, token_type: TokenType, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta

    to_encode.update({"exp": expire, "typ": token_type})

    return jwt.encode(to_encode, settings.JWT_SECRET.get_secret_value(), algorithm=ALGORITHM)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    return _create_token(
        data,
        "access",
        expires_delta or timedelta(minutes=15)
    )


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    return _create_token(
        data,
        "refresh",
        expires_delta or timedelta(days=7)
    )


def _verify_token(token: str, token_type: TokenType):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET.get_secret_value(), algorithms=[ALGORITHM])

        if payload["typ"] != token_type:
            raise ValueError("Invalid token type")

        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError(f"Invalid token")


def verify_access_token(token: str):
    return _verify_token(token, "access")


def verify_refresh_token(token: str):
    return _verify_token(token, "refresh")
