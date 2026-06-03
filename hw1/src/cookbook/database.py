import os
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool


DEFAULT_DATABASE_URL = os.getenv(
    "RECIPES_DATABASE_URL",
    "sqlite+aiosqlite:///./recipes.db",
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


def create_engine(database_url: str = DEFAULT_DATABASE_URL) -> AsyncEngine:
    if database_url == "sqlite+aiosqlite:///:memory:":
        return create_async_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    return create_async_engine(database_url, echo=False)


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
