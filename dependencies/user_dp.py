import logging
from uuid import uuid4

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from auth import verify_token
from database import AsyncSessionDep
from models.user_model import User, UserInDB

security = HTTPBearer()

def get_current_user(creds=Depends(security)):
    try:
        payload = verify_token(creds.credentials)
        return payload
    except Exception as error:
        logging.exception(error)
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_or_create_user(payload, db: AsyncSession):
    result = await db.execute(
        select(UserInDB).where(
            col(UserInDB.keycloak_user_id)== payload["sub"]
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        user = UserInDB(
            id=uuid4(),
            keycloak_user_id=payload["sub"],
            username=payload["preferred_username"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


