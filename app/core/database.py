from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    create_async_engine,
)

from app.core.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
    )


async def get_db_connection() -> AsyncIterator[AsyncConnection]:
    async with get_engine().connect() as connection:
        yield connection


async def dispose_engine() -> None:
    await get_engine().dispose()
