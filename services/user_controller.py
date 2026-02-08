from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models.user_model import UserInDB, TokenModel


async def get_or_create_user(token_model: TokenModel, db: AsyncSession):
    result = await db.execute(
        select(UserInDB).where(
            UserInDB.keycloak_user_id == token_model.sub
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        user = UserInDB(
            keycloak_user_id=token_model.sub,
            username=token_model.preferred_username,
            **token_model.model_dump()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user