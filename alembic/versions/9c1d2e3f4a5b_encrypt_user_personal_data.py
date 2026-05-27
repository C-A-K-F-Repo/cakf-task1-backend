"""encrypt user personal data

Revision ID: 9c1d2e3f4a5b
Revises: b1e2c3d4f5a6
Create Date: 2026-05-27 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c1d2e3f4a5b"
down_revision: Union[str, Sequence[str], None] = "b1e2c3d4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_lookup", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("phone_number_lookup", sa.String(length=64), nullable=True))

    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_phone_number"), table_name="users")
    op.drop_index(op.f("ix_users_full_name"), table_name="users")

    op.alter_column("users", "email", existing_type=sa.String(length=100), type_=sa.Text(), existing_nullable=False)
    op.alter_column("users", "full_name", existing_type=sa.String(length=100), type_=sa.Text(), existing_nullable=True)
    op.alter_column("users", "phone_number", existing_type=sa.String(length=20), type_=sa.Text(), existing_nullable=True)
    op.alter_column("users", "delivery_address", existing_type=sa.String(length=255), type_=sa.Text(), existing_nullable=True)
    op.alter_column("users", "dob", existing_type=sa.Date(), type_=sa.Text(), existing_nullable=True, postgresql_using="dob::text")

    _transform_users(encrypting=True)

    op.alter_column("users", "email_lookup", existing_type=sa.String(length=64), nullable=False)
    op.create_index(op.f("ix_users_email_lookup"), "users", ["email_lookup"], unique=True)
    op.create_index(op.f("ix_users_phone_number_lookup"), "users", ["phone_number_lookup"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_phone_number_lookup"), table_name="users")
    op.drop_index(op.f("ix_users_email_lookup"), table_name="users")

    _transform_users(encrypting=False)

    op.alter_column("users", "dob", existing_type=sa.Text(), type_=sa.Date(), existing_nullable=True, postgresql_using="dob::date")
    op.alter_column("users", "delivery_address", existing_type=sa.Text(), type_=sa.String(length=255), existing_nullable=True)
    op.alter_column("users", "phone_number", existing_type=sa.Text(), type_=sa.String(length=20), existing_nullable=True)
    op.alter_column("users", "full_name", existing_type=sa.Text(), type_=sa.String(length=100), existing_nullable=True)
    op.alter_column("users", "email", existing_type=sa.Text(), type_=sa.String(length=100), existing_nullable=False)

    op.drop_column("users", "phone_number_lookup")
    op.drop_column("users", "email_lookup")

    op.create_index(op.f("ix_users_full_name"), "users", ["full_name"], unique=False)
    op.create_index(op.f("ix_users_phone_number"), "users", ["phone_number"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def _transform_users(*, encrypting: bool) -> None:
    connection = op.get_bind()
    rows = connection.execute(sa.text(
        "SELECT id, email, full_name, phone_number, dob, delivery_address FROM users"
    )).mappings().all()

    for row in rows:
        email = row["email"]
        phone = row["phone_number"]
        values = {
            "email": _encrypt(email) if encrypting else _decrypt(email),
            "full_name": _encrypt(row["full_name"]) if encrypting else _decrypt(row["full_name"]),
            "phone_number": _encrypt(phone) if encrypting else _decrypt(phone),
            "dob": _encrypt(row["dob"]) if encrypting else _decrypt(row["dob"]),
            "delivery_address": _encrypt(row["delivery_address"]) if encrypting else _decrypt(row["delivery_address"]),
            "email_lookup": _lookup_hash(_decrypt(email) if not encrypting else email),
            "phone_number_lookup": _lookup_hash(_decrypt(phone) if not encrypting else phone),
            "id": row["id"],
        }
        if not encrypting:
            values["email_lookup"] = None
            values["phone_number_lookup"] = None

        connection.execute(sa.text(
            """
            UPDATE users
            SET email = :email,
                full_name = :full_name,
                phone_number = :phone_number,
                dob = :dob,
                delivery_address = :delivery_address,
                email_lookup = :email_lookup,
                phone_number_lookup = :phone_number_lookup
            WHERE id = :id
            """
        ), values)


def _encrypt(value):
    if value is None:
        return None
    import base64
    import os

    plaintext = str(value)
    nonce = os.urandom(12)
    plaintext_bytes = plaintext.encode("utf-8")
    ciphertext = _xor_bytes(plaintext_bytes, _keystream(_key("PERSONAL_DATA_ENCRYPTION_KEY"), nonce, len(plaintext_bytes)))
    return "v1:" + base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii")


def _decrypt(value):
    if value is None:
        return None
    if not isinstance(value, str) or not value.startswith("v1:"):
        return value
    import base64

    payload = base64.urlsafe_b64decode(value[3:])
    ciphertext = payload[12:]
    plaintext = _xor_bytes(ciphertext, _keystream(_key("PERSONAL_DATA_ENCRYPTION_KEY"), payload[:12], len(ciphertext)))
    return plaintext.decode("utf-8")


def _keystream(key: bytes, nonce: bytes, size: int) -> bytes:
    import hashlib

    chunks = []
    counter = 0
    while sum(len(chunk) for chunk in chunks) < size:
        chunks.append(hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest())
        counter += 1
    return b"".join(chunks)[:size]


def _xor_bytes(left: bytes, right: bytes) -> bytes:
    return bytes(a ^ b for a, b in zip(left, right))


def _lookup_hash(value):
    if value is None:
        return None
    import hashlib
    import hmac

    normalized = str(value).strip().lower()
    if not normalized:
        return None
    return hmac.new(_key("PERSONAL_DATA_LOOKUP_KEY"), normalized.encode("utf-8"), hashlib.sha256).hexdigest()


def _key(name: str) -> bytes:
    import base64
    import os

    raw = os.environ[name].strip()
    for decoder in (base64.urlsafe_b64decode, base64.b64decode):
        try:
            key = decoder(raw + "=" * (-len(raw) % 4))
            if len(key) in {16, 24, 32}:
                return key
        except Exception:
            pass
    key = bytes.fromhex(raw)
    if len(key) not in {16, 24, 32}:
        raise ValueError(f"{name} must be a base64 or hex encoded 16/24/32 byte key")
    return key
