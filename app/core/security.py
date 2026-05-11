"""Security helpers for password hashing and JWT tokens."""

from datetime import UTC, datetime, timedelta
from typing import Literal
import hashlib
import hmac
import secrets
import uuid

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITHM = "HS256"
TokenType = Literal["access", "refresh"]

password_hash = PasswordHash.recommended()


def _create_token(data: dict, token_type: TokenType, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta

    to_encode.update({"exp": expire, "typ": token_type, "jti": str(uuid.uuid4())})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET.get_secret_value(),
        algorithm=ALGORITHM,
    )


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    return _create_token(data, "access", expires_delta or timedelta(minutes=15))


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    return _create_token(data, "refresh", expires_delta or timedelta(days=7))


def _verify_token(token: str, token_type: TokenType):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET.get_secret_value(),
            algorithms=[ALGORITHM],
        )

        if payload["typ"] != token_type:
            raise ValueError("Invalid token type")

        return payload
    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc


def verify_access_token(token: str):
    return _verify_token(token, "access")


def verify_refresh_token(token: str):
    return _verify_token(token, "refresh")


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """Return (salt_hex, hash_hex) for a plaintext password."""
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return salt.hex(), digest.hex()


def verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    """Verify password against stored PBKDF2 hash."""
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return hmac.compare_digest(digest.hex(), expected_hash_hex)


def revoke_token(jti: str):
    return None
