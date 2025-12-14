"""
Database connection manager with async SQLAlchemy.

This module provides database connection pooling and session management
for async PostgreSQL operations using Neon.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.config.settings import get_settings

# Create declarative base for ORM models
Base = declarative_base()

# Global engine and session factory
_engine = None
_async_session_factory = None


def get_engine():
    """
    Get or create the async database engine.

    Returns:
        AsyncEngine instance with connection pooling

    Example:
        >>> engine = get_engine()
        >>> async with engine.begin() as conn:
        ...     await conn.execute(text("SELECT 1"))
    """
    global _engine

    if _engine is None:
        settings = get_settings()

        _engine = create_async_engine(
            settings.database_url,
            echo=settings.log_level == "DEBUG",  # Log SQL in debug mode
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the async session factory.

    Returns:
        AsyncSession factory for creating database sessions

    Example:
        >>> session_factory = get_session_factory()
        >>> async with session_factory() as session:
        ...     result = await session.execute(select(User))
    """
    global _async_session_factory

    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autoflush=False,  # Manual flushing for better control
        )

    return _async_session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session with automatic cleanup.

    Yields:
        AsyncSession for database operations

    Example:
        >>> async with get_db_session() as session:
        ...     query = await session.execute(select(User))
        ...     users = query.scalars().all()
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """
    Initialize database schema (create all tables).

    Note: In production, use Alembic migrations instead.

    Example:
        >>> await init_database()
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    """
    Close database connections and dispose of the engine.

    Call this on application shutdown.

    Example:
        >>> await close_database()
    """
    global _engine, _async_session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None


async def check_database_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        True if connection is healthy, False otherwise

    Example:
        >>> is_healthy = await check_database_connection()
        >>> print(f"Database: {'ok' if is_healthy else 'error'}")
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


# Import text for raw SQL queries
from sqlalchemy import text  # noqa: E402

__all__ = [
    "Base",
    "get_engine",
    "get_session_factory",
    "get_db_session",
    "init_database",
    "close_database",
    "check_database_connection",
]
