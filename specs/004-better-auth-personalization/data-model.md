# Data Model Specification

**Feature**: Better Auth User Authentication and Personalized RAG Chatbot
**Date**: 2025-12-20
**Database**: PostgreSQL (Neon)

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the authentication and user profile system. All entities are implemented using SQLAlchemy ORM with PostgreSQL-specific features (ENUMs, JSONB, UUIDs).

---

## Entity Relationship Diagram (Text Format)

```
┌─────────────────┐
│     User        │
│─────────────────│
│ id (PK)         │◄──────┐
│ email (UQ)      │       │
│ hashed_password │       │
│ is_active       │       │
│ created_at      │       │
│ last_login_at   │       │
└─────────────────┘       │
         │                │
         │ 1:1            │ 1:N
         ▼                │
┌─────────────────┐       │
│  UserProfile    │       │
│─────────────────│       │
│ id (PK)         │       │
│ user_id (FK,UQ) │───────┘
│ software_exp    │
│ hardware_exp    │
│ interests       │
│ created_at      │
│ updated_at      │
└─────────────────┘

         │
         │ 1:N
         ▼
┌─────────────────┐
│    Session      │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │───────┐
│ access_token    │       │
│ refresh_token   │       │
│ expires_at      │       │
│ created_at      │       │
│ user_agent      │       │
│ ip_address      │       │
└─────────────────┘       │
                          │
                          │ 1:N
                          ▼
                    ┌─────────────────┐
                    │ ChatbotQuery    │
                    │─────────────────│
                    │ id (PK)         │
                    │ user_id (FK,NULL)│
                    │ query_text      │
                    │ response_text   │
                    │ personalization_│
                    │   context       │
                    │ created_at      │
                    └─────────────────┘
```

**Legend**:
- PK: Primary Key
- FK: Foreign Key
- UQ: Unique Constraint
- 1:1: One-to-One Relationship
- 1:N: One-to-Many Relationship

---

## Entity Definitions

### 1. User

**Purpose**: Represents an authenticated user account with credentials and basic account info.

**Fields**:

| Field            | Type         | Constraints                  | Description                                    |
|------------------|--------------|------------------------------|------------------------------------------------|
| id               | UUID         | PRIMARY KEY                  | Unique identifier for user                     |
| email            | VARCHAR(255) | UNIQUE, NOT NULL             | User's email address (login identifier)        |
| hashed_password  | VARCHAR(255) | NOT NULL                     | Bcrypt-hashed password (never store plaintext) |
| is_active        | BOOLEAN      | NOT NULL, DEFAULT TRUE       | Account status (false = disabled)              |
| created_at       | TIMESTAMP    | NOT NULL, DEFAULT NOW()      | Account creation timestamp                     |
| last_login_at    | TIMESTAMP    | NULLABLE                     | Last successful login timestamp                |

**Indexes**:
- `idx_user_email`: Index on `email` for fast lookup during signin
- `idx_user_created_at`: Index on `created_at` for analytics queries

**Validation Rules**:
- `email`: Must match regex `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- `hashed_password`: Must be bcrypt hash (starts with `$2b$`)
- `is_active`: Can only be set by admin or system (not user-modifiable)

**Business Rules**:
- Email must be unique across all users
- Password must meet strength requirements before hashing:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character (@$!%*?&)
- Default `is_active` to TRUE on creation
- Update `last_login_at` on every successful signin

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    chatbot_queries = relationship("ChatbotQuery", back_populates="user", cascade="all, delete-orphan")
```

---

### 2. UserProfile

**Purpose**: Stores user background information for personalizing RAG chatbot responses.

**Fields**:

| Field              | Type         | Constraints                     | Description                                      |
|--------------------|--------------|---------------------------------|--------------------------------------------------|
| id                 | UUID         | PRIMARY KEY                     | Unique identifier for profile                    |
| user_id            | UUID         | FOREIGN KEY (users.id), UNIQUE  | Reference to user (1:1 relationship)             |
| software_experience| ENUM         | NOT NULL                        | Software skill level                             |
| hardware_experience| ENUM         | NOT NULL                        | Hardware/robotics skill level                    |
| interests          | JSONB        | NULLABLE                        | Array of interest categories                     |
| created_at         | TIMESTAMP    | NOT NULL, DEFAULT NOW()         | Profile creation timestamp                       |
| updated_at         | TIMESTAMP    | NOT NULL, DEFAULT NOW()         | Last profile update timestamp (auto-updated)     |

**ENUMs**:

**SoftwareExperienceEnum**:
- `Beginner`: Minimal or no programming experience
- `Intermediate`: Some programming knowledge, can write basic scripts
- `Advanced`: Proficient in multiple languages, understands algorithms

**HardwareExperienceEnum**:
- `None`: No hardware or robotics experience
- `Basic`: Understands basic electronics, has used dev boards (Arduino, Raspberry Pi)
- `Advanced`: Experience with sensors, actuators, embedded systems

**Interests** (JSONB array, predefined categories):
- `["AI", "Robotics", "APIs", "ML", "Computer Vision", "Sensors", "Actuators", "Control Systems"]`
- Can be empty array if user skips optional interests during signup

**Indexes**:
- `idx_profile_user_id`: Index on `user_id` (automatically created by FK)
- `idx_profile_updated_at`: Index on `updated_at` for analytics

**Validation Rules**:
- `software_experience`: Must be one of enum values
- `hardware_experience`: Must be one of enum values
- `interests`: If not null, must be array of strings, max 10 interests
- `interests`: Each interest string must be max 50 characters

**Business Rules**:
- Profile must be created atomically with user during signup
- If user is deleted, profile is also deleted (cascade)
- `updated_at` automatically updates on any field modification
- Empty interests array is valid (user skipped optional field)

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

class SoftwareExperience(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class HardwareExperience(str, enum.Enum):
    NONE = "None"
    BASIC = "Basic"
    ADVANCED = "Advanced"

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    software_experience = Column(SQLEnum(SoftwareExperience), nullable=False)
    hardware_experience = Column(SQLEnum(HardwareExperience), nullable=False)
    interests = Column(JSONB, nullable=True)  # Array of strings
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")
```

---

### 3. Session

**Purpose**: Manages user authentication sessions with JWT access tokens and refresh tokens.

**Fields**:

| Field          | Type         | Constraints                  | Description                                        |
|----------------|--------------|------------------------------|----------------------------------------------------|
| id             | UUID         | PRIMARY KEY                  | Unique identifier for session                      |
| user_id        | UUID         | FOREIGN KEY (users.id)       | Reference to user                                  |
| access_token   | TEXT         | UNIQUE, NOT NULL             | JWT access token (short-lived, 15 min)             |
| refresh_token  | TEXT         | UNIQUE, NULLABLE             | Opaque refresh token (long-lived, 7 days)          |
| expires_at     | TIMESTAMP    | NOT NULL                     | Token expiration timestamp                         |
| created_at     | TIMESTAMP    | NOT NULL, DEFAULT NOW()      | Session creation timestamp                         |
| user_agent     | TEXT         | NULLABLE                     | Browser/client user agent string                   |
| ip_address     | VARCHAR(45)  | NULLABLE                     | Client IP address (supports IPv4 and IPv6)         |

**Indexes**:
- `idx_session_user_id`: Index on `user_id` for fast user session lookup
- `idx_session_access_token`: Index on `access_token` for token validation
- `idx_session_refresh_token`: Index on `refresh_token` for refresh operations
- `idx_session_expires_at`: Index on `expires_at` for cleanup queries

**Validation Rules**:
- `access_token`: Must be valid JWT format
- `refresh_token`: Must be UUID format if present
- `expires_at`: Must be future timestamp at creation
- `ip_address`: Must be valid IPv4 or IPv6 address if present

**Business Rules**:
- Multiple active sessions allowed per user (different devices)
- Signout deletes session from database
- Expired sessions should be periodically cleaned up (cron job)
- Access token stored for reference/revocation, but validation happens via JWT signature
- If user is deleted, all sessions are also deleted (cascade)

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    access_token = Column(Text, unique=True, nullable=False, index=True)
    refresh_token = Column(Text, unique=True, nullable=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
```

---

### 4. ChatbotQuery (Optional)

**Purpose**: Logs chatbot queries for analytics and personalization effectiveness tracking.

**Fields**:

| Field                   | Type         | Constraints                  | Description                                     |
|-------------------------|--------------|------------------------------|-------------------------------------------------|
| id                      | UUID         | PRIMARY KEY                  | Unique identifier for query                     |
| user_id                 | UUID         | FOREIGN KEY (users.id), NULL | Reference to user (NULL if unauthenticated)     |
| query_text              | TEXT         | NOT NULL                     | User's original question                        |
| response_text           | TEXT         | NOT NULL                     | Chatbot's generated response                    |
| personalization_context | JSONB        | NULLABLE                     | Snapshot of user profile at query time          |
| created_at              | TIMESTAMP    | NOT NULL, DEFAULT NOW()      | Query timestamp                                 |

**personalization_context structure** (JSON):
```json
{
  "software_experience": "Beginner",
  "hardware_experience": "None",
  "interests": ["AI", "ML"],
  "is_authenticated": true
}
```

**Indexes**:
- `idx_chatbot_query_user_id`: Index on `user_id` for user query history
- `idx_chatbot_query_created_at`: Index on `created_at` for time-based queries

**Validation Rules**:
- `query_text`: Max length 5000 characters
- `response_text`: Max length 10000 characters
- `personalization_context`: Must be valid JSON object if present

**Business Rules**:
- `user_id` is NULL for unauthenticated users
- If user is deleted, queries are retained but user_id set to NULL (no cascade delete)
- Store personalization snapshot (not just reference) to track changes over time
- Optional table - can be disabled if storage is a concern

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

class ChatbotQuery(Base):
    __tablename__ = "chatbot_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    personalization_context = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="chatbot_queries")
```

---

## State Transitions

### User Account Lifecycle

```
[New User] --signup--> [Active User] --signin--> [Authenticated User]
                            │                          │
                            │                          └--signout--> [Active User]
                            │
                            └--admin disable--> [Inactive User]
                                                      │
                                                      └--admin enable--> [Active User]
```

**States**:
- **New User**: Before account creation
- **Active User**: Account created, `is_active = TRUE`, not signed in
- **Authenticated User**: Valid session exists
- **Inactive User**: `is_active = FALSE`, cannot sign in

**Transitions**:
- **signup**: Create user + profile → Active User
- **signin**: Validate credentials → Create session → Authenticated User
- **signout**: Delete session → Active User
- **admin disable**: Set `is_active = FALSE` → Inactive User
- **admin enable**: Set `is_active = TRUE` → Active User

### Session Lifecycle

```
[No Session] --signin--> [Active Session] --access chatbot--> [Session in Use]
                              │                                      │
                              └--signout--> [Deleted Session]        │
                              │                                      │
                              └--token expires--> [Expired Session]  │
                                                      │              │
                                                      └--cleanup------┘
```

**States**:
- **No Session**: User not authenticated
- **Active Session**: Valid tokens, not expired
- **Session in Use**: Access token being used for API requests
- **Expired Session**: Past `expires_at` timestamp
- **Deleted Session**: Removed from database (signout or cleanup)

**Transitions**:
- **signin**: Create session record → Active Session
- **access chatbot**: Validate token → Session in Use (temporary state)
- **signout**: Delete session from DB → Deleted Session
- **token expires**: Time passes `expires_at` → Expired Session
- **cleanup**: Cron job removes expired sessions → Deleted Session

### Profile Update Lifecycle

```
[Profile Created] --user updates--> [Profile Modified] --auto save--> [Profile Saved]
                                           │
                                           └--validation fails--> [Profile Created] (no change)
```

**Transitions**:
- **user updates**: PUT /api/v1/profile request
- **validation fails**: Invalid enum value or interests format → Return error, no DB change
- **auto save**: Validation passes → Update `updated_at` → Profile Saved

---

## Data Integrity Constraints

### Foreign Key Constraints

1. **user_profiles.user_id → users.id**
   - ON DELETE CASCADE: Delete profile when user is deleted
   - ON UPDATE CASCADE: Update profile if user ID changes (unlikely with UUIDs)

2. **sessions.user_id → users.id**
   - ON DELETE CASCADE: Delete all sessions when user is deleted
   - ON UPDATE CASCADE: Update sessions if user ID changes

3. **chatbot_queries.user_id → users.id**
   - ON DELETE SET NULL: Preserve queries but anonymize when user is deleted
   - ON UPDATE CASCADE: Update queries if user ID changes

### Unique Constraints

1. **users.email**: Prevents duplicate accounts with same email
2. **user_profiles.user_id**: Enforces 1:1 relationship (one profile per user)
3. **sessions.access_token**: Prevents token reuse
4. **sessions.refresh_token**: Prevents token reuse

### Check Constraints

1. **users.email**: Length > 0 AND matches email regex
2. **users.hashed_password**: Length = 60 (bcrypt hash length)
3. **user_profiles.interests**: Array length ≤ 10 if not null
4. **sessions.expires_at**: expires_at > created_at

---

## Migration Scripts (Alembic)

### Initial Migration: 001_initial_auth_schema.py

```python
"""Initial auth schema with users, profiles, sessions

Revision ID: 001
Create Date: 2025-12-20
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# Revision identifiers
revision = '001_initial_auth_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create ENUMs
    software_exp_enum = postgresql.ENUM('Beginner', 'Intermediate', 'Advanced', name='software_experience')
    hardware_exp_enum = postgresql.ENUM('None', 'Basic', 'Advanced', name='hardware_experience')
    software_exp_enum.create(op.get_bind())
    hardware_exp_enum.create(op.get_bind())

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_created_at', 'users', ['created_at'])

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('software_experience', software_exp_enum, nullable=False),
        sa.Column('hardware_experience', hardware_exp_enum, nullable=False),
        sa.Column('interests', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index('idx_profile_updated_at', 'user_profiles', ['updated_at'])

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False, unique=True),
        sa.Column('refresh_token', sa.Text(), nullable=True, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
    )
    op.create_index('idx_session_user_id', 'sessions', ['user_id'])
    op.create_index('idx_session_access_token', 'sessions', ['access_token'])
    op.create_index('idx_session_refresh_token', 'sessions', ['refresh_token'])
    op.create_index('idx_session_expires_at', 'sessions', ['expires_at'])

    # Create chatbot_queries table (optional)
    op.create_table(
        'chatbot_queries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('personalization_context', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('idx_chatbot_query_user_id', 'chatbot_queries', ['user_id'])
    op.create_index('idx_chatbot_query_created_at', 'chatbot_queries', ['created_at'])

def downgrade():
    # Drop tables in reverse order
    op.drop_table('chatbot_queries')
    op.drop_table('sessions')
    op.drop_table('user_profiles')
    op.drop_table('users')

    # Drop ENUMs
    op.execute('DROP TYPE software_experience')
    op.execute('DROP TYPE hardware_experience')
```

---

## Summary

**Total Entities**: 4 (User, UserProfile, Session, ChatbotQuery)
**Total Relationships**: 3 (User↔Profile 1:1, User↔Session 1:N, User↔Query 1:N)
**Database Features Used**: UUIDs, ENUMs, JSONB, Foreign Keys, Cascade Deletes, Auto-timestamps

**Next Steps**:
1. Generate API contracts (OpenAPI specs) based on these entities
2. Define request/response schemas (Pydantic models)
3. Create implementation guide (quickstart.md)
