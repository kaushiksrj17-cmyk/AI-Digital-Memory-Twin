"""Database schema initialization.

Creates tables for SQLite and PostgreSQL environments.
"""

import asyncio
from sqlalchemy import create_engine
from database.base import Base
from database.session import engine, has_aiosqlite
import database.models  # Register all models on Base.metadata


async def init_db_async():
    """Asynchronously create all tables."""
    if hasattr(engine, "begin"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    elif hasattr(engine, "raw_engine"):
        Base.metadata.create_all(bind=engine.raw_engine)


def init_db_sync():
    """Synchronously create all tables."""
    sync_engine = create_engine(
        "sqlite:///D:/ECHO/storage/local/echo_dev.db",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=sync_engine)
    sync_engine.dispose()


if __name__ == "__main__":
    init_db_sync()
    print("Database tables initialized successfully.")
