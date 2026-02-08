# python
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlmodel import select, col, desc

from database import  AsyncSessionDep
from dependencies.user_dp import get_current_active_user, CurrentActiveUserDp
from models.task_model import Task, TaskRequest
from models.user_model import UserInDB
from services.task_controller import get_all_tasks_by_user, get_task_by_user, update_task_by_user, delete_task_by_user

task_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@task_router.get("/", response_model=list[Task])
async def get_tasks(db: AsyncSessionDep,
                    current_user: CurrentActiveUserDp,
                    offset: Annotated[int, Query(ge=0)] = 0,
                    limit: Annotated[int, Query(ge=1,le=100)] = 10):

    return await get_all_tasks_by_user(current_user.id, db, offset, limit)


@task_router.get("/{task_id}", response_model=Task)
async def get_task_by_id(task_id: uuid.UUID, db:AsyncSessionDep,
                         current_user: CurrentActiveUserDp,
                         ):

    return await get_task_by_user(db, task_id, current_user.id)

#
@task_router.put("/{task_id}", response_model=Task)



async def update_task(task_id: uuid.UUID, new_task: TaskRequest,
                      db:AsyncSessionDep,
                      current_user: CurrentActiveUserDp,
                      ):

    return await update_task_by_user(db, task_id, current_user.id, new_task)
#
@task_router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: uuid.UUID, db:AsyncSessionDep,
                      current_user: CurrentActiveUserDp,
                      ):

    return await delete_task_by_user(db, task_id, current_user.id)
#
#
@task_router.post("/", response_model=Task, status_code=201)
async def create_task(task: TaskRequest, db:AsyncSessionDep,
                      current_user: CurrentActiveUserDp,
                      ):

    return await create_task_by_user(task, db, current_user)
