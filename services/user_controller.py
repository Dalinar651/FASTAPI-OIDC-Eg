from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models.user_model import UserInDB


async def get_or_create_user(payload, db: AsyncSession):
    result = await db.execute(
        select(UserInDB).where(
            UserInDB.keycloak_user_id == payload["sub"]
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        user = UserInDB(
            keycloak_user_id=payload["sub"],
            username=payload["preferred_username"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user