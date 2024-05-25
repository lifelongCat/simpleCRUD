from contextlib import asynccontextmanager

from asyncpg import create_pool
from fastapi import FastAPI

from app.config import settings


@asynccontextmanager
async def init_db(app: FastAPI) -> None:
    settings.POSTGRES_POOL = await create_pool(settings.POSTGRES_URL)
    yield
    settings.POSTGRES_POOL.close()
