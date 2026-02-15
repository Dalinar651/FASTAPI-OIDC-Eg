import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from database import engine
from error_handlers import register_exception_handlers
from routers import tasks
from routers import users


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
register_exception_handlers(app)

app.include_router(tasks.task_router)
app.include_router(users.user_router)


@app.get("/health")
async def root():
    return {"message": "server is running"}
