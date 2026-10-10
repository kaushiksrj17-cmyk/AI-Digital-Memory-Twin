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

DATABASE_URL = os.getenv("DATABASE_URL", "")

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
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///D:/ECHO/storage/local/echo_dev.db"
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
    SYNC_DATABASE_URL = "sqlite:///D:/ECHO/storage/local/echo_dev.db"
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
