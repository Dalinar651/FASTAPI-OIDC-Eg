# python
import datetime
import uuid

from pydantic import BaseModel
from sqlalchemy import event
from sqlmodel import SQLModel, Field


def _now_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

class TaskRequest(SQLModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., max_length=4000)
    completed: bool = Field(default=False)

    class Config:
        str_strip_whitespace = True

class Task(TaskRequest, SQLModel, table=True):
    __tablename__ = "task_table"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    created_at: datetime.datetime = Field(default_factory=_now_utc)
    updated_at: datetime.datetime = Field(default_factory=_now_utc)
    user_id: uuid.UUID = Field(foreign_key="user_model.id")

    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    user_id: uuid.UUID
    completed: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


@event.listens_for(Task, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    target.updated_at = _now_utc()
