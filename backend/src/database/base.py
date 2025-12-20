"""
SQLAlchemy declarative base for database models.
"""
from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base class
# All SQLAlchemy models will inherit from this Base
Base = declarative_base()

# Metadata is accessible via Base.metadata
# This is used by Alembic for migrations
