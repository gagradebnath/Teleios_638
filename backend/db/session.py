"""
db/session.py — SQLite async engine and session factory.
Uses SQLAlchemy 2.x + aiosqlite driver.

Usage:
    from db.session import init_db, get_async_session

    await init_db("sqlite+aiosqlite:///./data/teleios.db")

    async with get_async_session() as session:
        result = await session.execute(text("SELECT 1"))
"""
from __future__ import annotations
import os
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase

import structlog

logger = structlog.get_logger()

# Module-level singletons — set once by init_db()
_engine:          AsyncEngine | None               = None
_session_factory: async_sessionmaker | None        = None


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


async def init_db(db_url: str) -> None:
    """
    Initialise the async engine and create all tables.
    Must be called once during application startup (lifespan).

    Automatically:
      - normalises sqlite:// → sqlite+aiosqlite://
      - creates the directory for the .db file if it doesn't exist
      - runs CREATE TABLE IF NOT EXISTS for all mapped models
    """
    global _engine, _session_factory

    # Normalise driver prefix
    if db_url.startswith("sqlite://") and not db_url.startswith("sqlite+aiosqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    # Ensure the data directory exists (e.g. ./data/)
    if "///" in db_url:
        db_path = db_url.split("///", 1)[1]
        db_dir  = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    _engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    # Import models here to ensure they are registered with Base.metadata
    from db import models as _models  # noqa: F401

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("db.ready", url=db_url)


@asynccontextmanager
async def get_async_session():
    """
    Async context manager that yields a SQLAlchemy AsyncSession.

    Usage:
        async with get_async_session() as session:
            await session.execute(...)
            await session.commit()
    """
    if _session_factory is None:
        raise RuntimeError(
            "Database not initialised. Call await init_db(url) before using sessions."
        )
    async with _session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def close_db() -> None:
    """Dispose the engine — call during application shutdown."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        logger.info("db.closed")