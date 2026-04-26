from pydantic import BaseModel


class UserInfoResponse(BaseModel):
    email: str
    email_verified: bool


class CallbackPayload(BaseModel):
    id_token: str
