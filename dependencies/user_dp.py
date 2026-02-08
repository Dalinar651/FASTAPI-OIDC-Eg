import logging
from uuid import uuid4

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.annotation import Annotated
from sqlmodel import col, select

from auth import verify_token
from database import AsyncSessionDep
from models.user_model import User, UserInDB
from services.user_controller import get_or_create_user

security = HTTPBearer()


def get_current_user(creds=Depends(security)) -> dict:
    try:
        payload = verify_token(creds.credentials)
        return payload
    except Exception as error:
        logging.exception(error)
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user_db(
    db: AsyncSessionDep,
    payload: dict = Depends(get_current_user),
) -> UserInDB:

    return await get_or_create_user(db=db, payload=payload)

async def get_current_active_user(
        current_user: UserInDB = Depends(get_current_user_db)):

    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


CurrentActiveUserDp = Annotated[UserInDB,Depends(get_current_active_user)]
