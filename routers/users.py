import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, col

from auth import verify_token
from database import  AsyncSessionDep
from dependencies.user_dp import get_or_create_user, get_current_user
from models.task_model import Task, TaskRequest
from models.user_model import UserInDB, TokenModel

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@user_router.get("/me", response_model=UserInDB)
async def me(
        db: AsyncSessionDep,
        token_model: TokenModel = Depends(get_current_user),
):
    user = await get_or_create_user(token_model, db)
    return user


