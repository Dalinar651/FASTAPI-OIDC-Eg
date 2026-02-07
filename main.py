from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from database import engine
from routers import tasks
from routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(tasks.task_router)
app.include_router(users.user_router)


# Optionally, add shutdown code here
@app.get("/health")
async def root():
    return {"message": "server is running"}