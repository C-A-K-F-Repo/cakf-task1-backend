"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.google_oauth import CallbackPayload, UserInfoResponse
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth.exceptions import GoogleAuthError
from app.core.config import settings

router = APIRouter()


@router.post("/google/callback")
async def google_callback(payload: CallbackPayload):
    try:
        id_info = id_token.verify_oauth2_token(
            payload.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        validated_info = UserInfoResponse.model_validate(id_info)

        if not validated_info.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified"
            )

        # TODO: return jwt tokens

        return validated_info
    except GoogleAuthError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
