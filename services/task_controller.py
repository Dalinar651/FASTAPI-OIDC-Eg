import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from models.task_model import Task, TaskRequest


async def get_all_tasks_by_user(db: AsyncSession,user_id: uuid.UUID, offset: int = 0, limit: int = 10) -> list[Task]:
    # Implement the logic to fetch all tasks owned by the user from the database
    query = select(Task).where(Task.user_id == user_id).order_by(desc(Task.created_at)).offset(offset).limit(
        limit)
    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks


async def get_task_by_user(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Task:
    stmt = (
        select(Task)
        .where(
            Task.id == task_id &
            Task.user_id == user_id,
        )
    )

    result = await db.execute(stmt)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


async def update_task_by_user(
    db: AsyncSession,
    task_id: uuid.UUID,
    user_id: uuid.UUID,
    new_task_data: TaskRequest,
) -> Task:
    task = await get_task_by_user(db, task_id, user_id)

    task_data = new_task_data.model_dump(exclude_unset=True, exclude={'created_at', 'id', 'created_by'})
    task.sqlmodel_update(task_data)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


async def delete_task_by_user(db: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
    # Implement the logic to delete a task owned by the user from the database
    task = await get_task_by_user(db, task_id, user_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()


async def create_task_by_user(task_data: TaskRequest, db: AsyncSession, user_id: uuid.UUID) -> Task:
    new_task = Task(**task_data.model_dump(), user_id=user_id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task
