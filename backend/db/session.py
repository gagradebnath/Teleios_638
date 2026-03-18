"""
Database session — SQLite via aiosqlite + SQLAlchemy async.
"""
from __future__ import annotations
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

_engine = None
_session_factory = None


class Base(DeclarativeBase):
    pass


async def init_db(db_url: str) -> None:
    global _engine, _session_factory
    # Ensure correct driver prefix
    if db_url.startswith("sqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    _engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Auto-create all tables on first run
    from db.models import Base as ModelBase
    async with _engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)


@asynccontextmanager
async def get_async_session():
    if _session_factory is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")
    async with _session_factory() as session:
        yield session