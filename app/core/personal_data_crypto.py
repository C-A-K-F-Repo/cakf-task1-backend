import base64
import hashlib
import hmac
import os
from datetime import date, datetime
from typing import Any

from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

PREFIX = "v1:"
NONCE_SIZE = 12


def _decode_key(value: str, setting_name: str) -> bytes:
    raw = value.strip()
    for decoder in (base64.urlsafe_b64decode, base64.b64decode):
        try:
            key = decoder(raw + "=" * (-len(raw) % 4))
            if len(key) in {16, 24, 32}:
                return key
        except Exception:
            pass
    try:
        key = bytes.fromhex(raw)
        if len(key) in {16, 24, 32}:
            return key
    except ValueError:
        pass
    raise ValueError(f"{setting_name} must be a base64 or hex encoded 16/24/32 byte key")


def _encryption_key() -> bytes:
    from app.core.config import settings

    return _decode_key(
        settings.PERSONAL_DATA_ENCRYPTION_KEY.get_secret_value(),
        "PERSONAL_DATA_ENCRYPTION_KEY",
    )


def _lookup_key() -> bytes:
    from app.core.config import settings

    return _decode_key(
        settings.PERSONAL_DATA_LOOKUP_KEY.get_secret_value(),
        "PERSONAL_DATA_LOOKUP_KEY",
    )


def encrypt(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        plaintext = value.isoformat()
    else:
        plaintext = str(value)
    if plaintext.startswith(PREFIX):
        return plaintext

    nonce = os.urandom(NONCE_SIZE)
    plaintext_bytes = plaintext.encode("utf-8")
    ciphertext = _xor_bytes(plaintext_bytes, _keystream(_encryption_key(), nonce, len(plaintext_bytes)))
    return PREFIX + base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")


def decrypt(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.startswith(PREFIX):
        return value
    payload = base64.urlsafe_b64decode(value[len(PREFIX):])
    nonce = payload[:NONCE_SIZE]
    ciphertext = payload[NONCE_SIZE:]
    plaintext = _xor_bytes(ciphertext, _keystream(_encryption_key(), nonce, len(ciphertext)))
    return plaintext.decode("utf-8")


def _keystream(key: bytes, nonce: bytes, size: int) -> bytes:
    chunks = []
    counter = 0
    while sum(len(chunk) for chunk in chunks) < size:
        chunks.append(hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest())
        counter += 1
    return b"".join(chunks)[:size]


def _xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def normalize_email(value: str) -> str:
    return value.strip().lower()


def normalize_lookup(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    return normalized or None


def lookup_hash(value: str | None) -> str | None:
    normalized = normalize_lookup(value)
    if normalized is None:
        return None
    return hmac.new(_lookup_key(), normalized.encode("utf-8"), hashlib.sha256).hexdigest()


class EncryptedString(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> str | None:
        return encrypt(value)

    def process_result_value(self, value: str | None, dialect) -> str | None:
        return decrypt(value)


class EncryptedDate(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect) -> str | None:
        return encrypt(value)

    def process_result_value(self, value: str | None, dialect) -> date | None:
        decrypted = decrypt(value)
        if decrypted is None or isinstance(decrypted, date):
            return decrypted
        return date.fromisoformat(decrypted[:10])
