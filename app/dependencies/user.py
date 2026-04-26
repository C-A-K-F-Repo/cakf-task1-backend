from fastapi import status, Depends, HTTPException

from .db import SessionDep
from .oauth2 import oauth2_scheme

from app.core.security import verify_access_token


async def get_current_user(db: SessionDep, token: str = Depends(oauth2_scheme)):
    try:
        access_token = verify_access_token(token)
        return access_token["sub"]
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
