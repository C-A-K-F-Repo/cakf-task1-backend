from typing import Annotated
from fastapi import Depends
from app.schemas.user import UserInDb


async def get_current_user():
    # TODO: get user from jwt, otherwise throw 401
    pass


async def get_admin():
    # TODO: get user from jwt, check admin role
    pass


UserDep = Annotated[UserInDb, Depends(get_current_user)]
AdminDep = Annotated[UserInDb, Depends(get_admin)]
