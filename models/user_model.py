import datetime
import uuid
from typing import List

from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from pydantic import Field as PydanticField

from models.task_model import _now_utc



class RealmAccess(BaseModel):
    roles: List[str]


class Account(BaseModel):
    roles: List[str]


class ResourceAccess(BaseModel):
    account: Account


class TokenModel(BaseModel):
    exp: int
    iat: int
    auth_time: int
    jti: str
    iss: str
    aud: str
    sub: str
    typ: str
    azp: str
    nonce: str
    session_state: str
    acr: str
    allowed_origins: list[str] = PydanticField(..., alias='allowed-origins')
    realm_access: RealmAccess
    resource_access: ResourceAccess
    scope: str
    sid: str
    email_verified: bool
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True



class User(BaseModel):
    username: str
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    keycloak_user_id: str
    email: str | None = None
    family_name: str | None = None
    given_name: str | None = None
    disabled: bool = False


class UserInDB(User, SQLModel, table=True):
    __tablename__ = "user_model"
    created_at: datetime.datetime = Field(default_factory=_now_utc)
    class Config:
        from_attributes = True

