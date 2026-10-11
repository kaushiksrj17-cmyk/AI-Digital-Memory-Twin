"""Database session management (PostgreSQL-ready with local fallback).

Dynamically detects available database drivers (PostgreSQL asyncpg, SQLite aiosqlite,
or standard synchronous SQLite with thread offloading) to ensure immediate offline
executability with zero external setup friction.
"""

from typing import AsyncGenerator, Optional, Any
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
import asyncio
from pathlib import Path
from backend.app.core.config import settings

DATABASE_URL = os.getenv("DATABASE_URL") or settings.DATABASE_URL

has_aiosqlite = False
try:
    import aiosqlite
    has_aiosqlite = True
except ImportError:
    has_aiosqlite = False

# Resolve engine
if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgresql+asyncpg://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=os.getenv("DATABASE_ECHO", "False").lower() == "true",
        future=True
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
elif has_aiosqlite:
    if "sqlite" in DATABASE_URL and "+aiosqlite" not in DATABASE_URL:
        ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    else:
        ASYNC_DATABASE_URL = DATABASE_URL

    # Ensure parent directory of local SQLite database file exists safely
    if "sqlite" in ASYNC_DATABASE_URL:
        db_path = ASYNC_DATABASE_URL.split(":///")[-1]
        if db_path:
            try:
                Path(db_path).resolve().parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=os.getenv("DATABASE_ECHO", "False").lower() == "true",
        future=True
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
else:
    # Fallback to standard built-in SQLite engine
    SYNC_DATABASE_URL = DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
    if "sqlite" in SYNC_DATABASE_URL:
        db_path = SYNC_DATABASE_URL.split(":///")[-1]
        if db_path:
            try:
                Path(db_path).resolve().parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        connect_args={"check_same_thread": False},
        future=True
    )
    SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

    # Provide an engine adapter that responds gracefully to dispose()
    class SyncEngineAdapter:
        def __init__(self, raw_engine):
            self.raw_engine = raw_engine

        async def dispose(self):
            self.raw_engine.dispose()

    engine = SyncEngineAdapter(sync_engine)
    AsyncSessionLocal = SyncSessionLocal


async def get_db_session():
    """Dependency that yields an active database session."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        if hasattr(session, "close"):
            if asyncio.iscoroutinefunction(session.close):
                await session.close()
            else:
                session.close()
