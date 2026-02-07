# python
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select, col

from database import  AsyncSessionDep
from models.task_model import Task, TaskRequest


task_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@task_router.get("/", response_model=list[Task])
async def get_tasks(db: AsyncSessionDep, offset: Annotated[int, Query(ge=0)] = 0,limit: Annotated[int, Query(ge=1,le=100)] = 10):
    query = select(Task).order_by(col(Task.created_at).desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@task_router.get("/{task_id}", response_model=Task)
async def get_task_by_id(task_id: uuid.UUID, db:AsyncSessionDep):
    result = await db.get(Task, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return result

#
@task_router.put("/{task_id}", response_model=Task)
async def update_task(task_id: uuid.UUID, new_task: TaskRequest, db:AsyncSessionDep):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = new_task.model_dump(exclude_unset=True,exclude={'created_at','id', 'created_by'})
    task.sqlmodel_update(task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
#
@task_router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: uuid.UUID, db:AsyncSessionDep):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return
#
#
@task_router.post("/", response_model=Task, status_code=201)
async def create_task(task: TaskRequest, db:AsyncSessionDep):
    # rely on Task defaults for id/created_at/updated_at
    new_task = Task(**task.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task
