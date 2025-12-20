"""
Database session management and connection pooling.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from typing import Generator

from src.core.config import get_settings

# Get database settings
settings = get_settings()

# Create engine with connection pooling
# For Neon serverless PostgreSQL, use NullPool to avoid connection issues
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,  # Neon handles connection pooling on their side
    echo=False,  # Set to True for SQL query logging during development
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator:
    """
    Dependency function for FastAPI endpoints.

    Yields:
        Database session

    Usage:
        @router.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
