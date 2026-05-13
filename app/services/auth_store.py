"""Backward-compatible alias for the new auth service layer."""

from app.services.auth_service import AuthService, auth_service


class AuthStore(AuthService):
    """Compatibility class. Prefer using AuthService directly."""


auth_store = auth_service
