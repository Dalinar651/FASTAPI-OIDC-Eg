import datetime
import uuid

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from models.task_model import _now_utc


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    keycloak_user_id: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User, SQLModel, table=True):
    __tablename__ = "user_model"
    created_at: datetime.datetime = Field(default_factory=_now_utc)
    class Config:
        from_attributes = True

