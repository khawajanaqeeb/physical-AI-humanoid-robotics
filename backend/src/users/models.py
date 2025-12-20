"""
SQLAlchemy models for users, profiles, sessions, and chatbot queries.
"""
import uuid
import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.base import Base


# Enums for experience levels
class SoftwareExperience(str, enum.Enum):
    """Software development experience levels."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class HardwareExperience(str, enum.Enum):
    """Hardware/robotics experience levels."""

    NONE = "NONE"
    BASIC = "BASIC"
    ADVANCED = "ADVANCED"


# Models
class User(Base):
    """
    User authentication model.

    Stores core authentication credentials and account status.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    chatbot_queries = relationship(
        "ChatbotQuery",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"


class UserProfile(Base):
    """
    User profile model for personalization.

    Stores user background information used for tailoring chatbot responses.
    """

    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    software_experience = Column(
        Enum(SoftwareExperience, name="software_experience_enum"),
        nullable=False,
        default=SoftwareExperience.BEGINNER,
    )
    hardware_experience = Column(
        Enum(HardwareExperience, name="hardware_experience_enum"),
        nullable=False,
        default=HardwareExperience.NONE,
    )
    interests = Column(
        JSON,
        nullable=False,
        default=list,
        comment="Array of interest strings (e.g., ['robotics', 'AI', 'computer vision'])",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return (
            f"<UserProfile(user_id={self.user_id}, "
            f"software={self.software_experience.value}, "
            f"hardware={self.hardware_experience.value})>"
        )


class Session(Base):
    """
    User session model for JWT token management.

    Stores refresh tokens for revocation capability while access tokens remain stateless.
    """

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session(user_id={self.user_id}, expires_at={self.expires_at})>"


class ChatbotQuery(Base):
    """
    Chatbot query history model (optional for analytics).

    Stores user queries, responses, and personalization context for tracking effectiveness.
    """

    __tablename__ = "chatbot_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # Allow unauthenticated queries
        index=True,
    )
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    personalization_context = Column(
        JSON,
        nullable=True,
        comment="Snapshot of user profile at query time for A/B testing",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="chatbot_queries")

    def __repr__(self):
        return f"<ChatbotQuery(user_id={self.user_id}, created_at={self.created_at})>"
