from typing import Any

from fastapi import status, Depends, HTTPException

from .db import SessionDep
from .oauth2 import oauth2_scheme

from app.core.security import verify_access_token
from app.schemas.user import Role
from ..models import User
from ..repositories import UserRepository


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    try:
        access_token = verify_access_token(token)
        return access_token
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


async def get_current_active_user(
    db: SessionDep,
    current_user_token: dict[str, Any] = Depends(get_current_user),
) -> User:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user_token["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = [role.value for role in allowed_roles]

    def __call__(self, current_user = Depends(get_current_user)):
        print(current_user["role"], self.allowed_roles)
        if current_user["role"] in self.allowed_roles:
            return True
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


allow_admin = RoleChecker([Role.ADMINISTRATOR])
allow_staff = RoleChecker([Role.ADMINISTRATOR, Role.ADVANCED_USER])
