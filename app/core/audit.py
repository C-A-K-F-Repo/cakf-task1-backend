import logging
from typing import Any

from fastapi import Request


audit_logger = logging.getLogger("audit")


def hash_identifier(value: str | None) -> str | None:
    if not value:
        return None
    from app.core.personal_data_crypto import lookup_hash

    return lookup_hash(value)


def mask_phone(value: str | None) -> str | None:
    if not value:
        return None
    return f"***{value[-4:]}" if len(value) > 4 else "***"


def audit_event(
    event: str,
    outcome: str,
    *,
    actor_user_id: Any = None,
    actor_role: str | None = None,
    target_type: str | None = None,
    target_id: Any = None,
    metadata: dict[str, Any] | None = None,
    request: Request | None = None,
) -> None:
    safe_metadata = metadata or {}
    extra = {
        "audit_event": event,
        "audit_outcome": outcome,
        "actor_user_id": hash_identifier(str(actor_user_id)) if actor_user_id is not None else None,
        "actor_role": actor_role,
        "target_type": target_type,
        "target_id": hash_identifier(str(target_id)) if target_id is not None else None,
        "metadata": safe_metadata,
    }
    if request is not None:
        extra["client_ip"] = request.client.host if request.client else None
        extra["user_agent"] = request.headers.get("user-agent")

    audit_logger.info("audit_event", extra=extra)
