# Data Model
## Feature: Docusaurus Better Auth Integration with Profile Personalization

**Created**: 2025-12-21
**Status**: Existing (Backend Already Implemented)

---

## Overview

This document describes the database schema for user authentication and personalization. The schema is **already implemented** in the FastAPI backend at `backend/src/users/models.py`.

**Database**: PostgreSQL (hosted on Neon serverless)
**ORM**: SQLAlchemy 2.0
**Migrations**: Alembic

---

## Entity Relationship Diagram

```
┌─────────────────────┐
│       User          │
├─────────────────────┤
│ id (PK)             │◄─────┐
│ email               │      │
│ hashed_password     │      │
│ is_active           │      │
│ created_at          │      │
│ last_login_at       │      │
└─────────────────────┘      │
         │                   │
         │ 1:1               │
         ▼                   │
┌─────────────────────┐      │
│   UserProfile       │      │
├─────────────────────┤      │
│ id (PK)             │      │
│ user_id (FK)        │──────┘
│ software_experience │
│ hardware_experience │
│ interests (JSON)    │
│ created_at          │
│ updated_at          │
└─────────────────────┘
         ▲
         │
         │ 1:N
         │
┌─────────────────────┐
│      Session        │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │──────┐
│ refresh_token       │      │
│ expires_at          │      │
│ user_agent          │      │
│ ip_address          │      │
│ created_at          │      │
└─────────────────────┘      │
                             │
         ▲                   │
         │                   │
         │ 1:N               │
         │                   │
┌─────────────────────┐      │
│   ChatbotQuery      │      │
├─────────────────────┤      │
│ id (PK)             │      │
│ user_id (FK)        │──────┘
│ query_text          │
│ response_text       │
│ personalization_ctx │
│ created_at          │
└─────────────────────┘
```

---

## Entities

### 1. User

**Purpose**: Core authentication entity storing user credentials and account status.

**Table**: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique user identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User's email address (login identifier) |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt-hashed password (12 rounds) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT true | Account active status (for soft deletion) |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `last_login_at` | TIMESTAMP WITH TIMEZONE | NULL | Last successful login timestamp |

**Relationships**:
- **1:1 → UserProfile**: Each user has exactly one profile
- **1:N → Session**: User can have multiple active sessions (different devices)
- **1:N → ChatbotQuery**: User can have many chatbot queries

**Indexes**:
- Primary key on `id`
- Unique index on `email`

**Business Rules**:
1. Email must be unique across all users
2. Email must be validated before insertion (RFC 5322 format)
3. Password must be hashed with bcrypt before storage (never store plaintext)
4. `is_active = false` disables login without deleting data
5. `last_login_at` updated on successful signin

**SQLAlchemy Model** (`backend/src/users/models.py:44-80`):
```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
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

**Purpose**: Stores user background information for personalization of chatbot responses and book content.

**Table**: `user_profiles`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique profile identifier |
| `user_id` | UUID | FOREIGN KEY(users.id) ON DELETE CASCADE, UNIQUE, NOT NULL, INDEX | Reference to user |
| `software_experience` | ENUM | NOT NULL, DEFAULT 'BEGINNER' | Software development experience level |
| `hardware_experience` | ENUM | NOT NULL, DEFAULT 'NONE' | Hardware/robotics experience level |
| `interests` | JSONB | NOT NULL, DEFAULT '[]' | Array of interest strings |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL, DEFAULT NOW() | Profile creation timestamp |
| `updated_at` | TIMESTAMP WITH TIMEZONE | NOT NULL, DEFAULT NOW(), ON UPDATE NOW() | Profile last update timestamp |

**Enums**:

**SoftwareExperience**:
- `BEGINNER`: "I'm new to programming"
- `INTERMEDIATE`: "I have some programming experience"
- `ADVANCED`: "I'm an experienced developer"

**HardwareExperience**:
- `NONE`: "No hardware/robotics experience"
- `BASIC`: "Some electronics or maker experience"
- `ADVANCED`: "Experienced with robotics/embedded systems"

**Interests (JSON Array)**:
Examples: `["Robotics", "AI", "Machine Learning", "Computer Vision"]`

Valid values (enforced by frontend, not database):
- Robotics
- Artificial Intelligence
- Machine Learning
- Hardware Design
- Software Development
- IoT
- Computer Vision
- Natural Language Processing
- Autonomous Systems
- Embedded Systems

**Relationships**:
- **N:1 → User**: Profile belongs to exactly one user

**Indexes**:
- Primary key on `id`
- Unique index on `user_id` (enforces 1:1 relationship)

**Business Rules**:
1. Profile created atomically with User during signup
2. Cannot exist without associated User (CASCADE DELETE)
3. `interests` can be empty array `[]` (optional field)
4. `software_experience` and `hardware_experience` are required
5. `updated_at` automatically updated on any profile field change

**SQLAlchemy Model** (`backend/src/users/models.py:82-132`):
```python
class SoftwareExperience(str, enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class HardwareExperience(str, enum.Enum):
    NONE = "NONE"
    BASIC = "BASIC"
    ADVANCED = "ADVANCED"

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    software_experience = Column(Enum(SoftwareExperience, name="software_experience_enum"), nullable=False, default=SoftwareExperience.BEGINNER)
    hardware_experience = Column(Enum(HardwareExperience, name="hardware_experience_enum"), nullable=False, default=HardwareExperience.NONE)
    interests = Column(JSON, nullable=False, default=list, comment="Array of interest strings")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")
```

---

### 3. Session

**Purpose**: Manages user sessions for JWT refresh token revocation. Access tokens are stateless JWT; refresh tokens are stored for revocation capability.

**Table**: `sessions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique session identifier |
| `user_id` | UUID | FOREIGN KEY(users.id) ON DELETE CASCADE, NOT NULL, INDEX | Reference to user |
| `refresh_token` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Hashed refresh token |
| `expires_at` | TIMESTAMP WITH TIMEZONE | NOT NULL | Session expiration timestamp (7 days from creation) |
| `user_agent` | VARCHAR(500) | NULL | Browser/client user agent string (for device tracking) |
| `ip_address` | VARCHAR(45) | NULL | Client IP address (for security auditing) |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL, DEFAULT NOW() | Session creation timestamp |

**Relationships**:
- **N:1 → User**: Session belongs to exactly one user

**Indexes**:
- Primary key on `id`
- Unique index on `refresh_token` (for fast lookup during refresh)
- Index on `user_id` (for listing user's sessions)

**Business Rules**:
1. Created on successful signup/signin
2. Deleted on signout or user deletion (CASCADE DELETE)
3. Expired sessions cleaned up by background job (not implemented yet)
4. `refresh_token` is hashed before storage (same as password hashing)
5. `expires_at` set to 7 days from creation (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)
6. One user can have multiple active sessions (different devices/browsers)

**SQLAlchemy Model** (`backend/src/users/models.py:134-161`):
```python
class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")
```

---

### 4. ChatbotQuery

**Purpose**: Stores chatbot query history for analytics and A/B testing of personalization effectiveness.

**Table**: `chatbot_queries`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique query identifier |
| `user_id` | UUID | FOREIGN KEY(users.id) ON DELETE SET NULL, NULL, INDEX | Reference to user (nullable for unauthenticated queries) |
| `query_text` | TEXT | NOT NULL | User's question to chatbot |
| `response_text` | TEXT | NOT NULL | Chatbot's generated response |
| `personalization_context` | JSONB | NULL | Snapshot of user profile at query time |
| `created_at` | TIMESTAMP WITH TIMEZONE | NOT NULL, DEFAULT NOW() | Query timestamp |

**Relationships**:
- **N:1 → User**: Query belongs to zero or one user (nullable for unauthenticated users)

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for listing user's query history)
- Index on `created_at` (for time-based analytics)

**Business Rules**:
1. `user_id` can be NULL (for unauthenticated queries before auth gating)
2. `personalization_context` stores snapshot of user profile at query time:
   ```json
   {
     "software_experience": "INTERMEDIATE",
     "hardware_experience": "BASIC",
     "interests": ["Robotics", "AI"]
   }
   ```
3. Used for measuring personalization effectiveness (A/B testing)
4. ON DELETE SET NULL preserves query history even if user deleted

**SQLAlchemy Model** (`backend/src/users/models.py:163-193`):
```python
class ChatbotQuery(Base):
    __tablename__ = "chatbot_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    personalization_context = Column(JSON, nullable=True, comment="Snapshot of user profile at query time")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="chatbot_queries")
```

---

## Database Migrations

**Location**: `backend/src/database/migrations/`

**Migration Tool**: Alembic

**Existing Migration**:
- `versions/5dca6094372c_initial_schema_with_users_profiles_.py`
- Creates: `users`, `user_profiles`, `sessions`, `chatbot_queries` tables
- Creates: `software_experience_enum`, `hardware_experience_enum` types

**Apply Migrations**:
```bash
cd backend
alembic upgrade head
```

**Check Current Version**:
```bash
alembic current
```

**Generate New Migration** (if schema changes needed):
```bash
alembic revision --autogenerate -m "Description of changes"
```

---

## Data Access Patterns

### 1. User Signup (Create User + Profile Atomically)

**Service**: `backend/src/users/services.py:create_user()`

```python
def create_user(
    db: Session,
    email: str,
    password: str,
    software_experience: SoftwareExperience,
    hardware_experience: HardwareExperience,
    interests: List[str]
) -> User:
    # Transaction ensures atomicity
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.flush()  # Get user.id before creating profile

    profile = UserProfile(
        user_id=user.id,
        software_experience=software_experience,
        hardware_experience=hardware_experience,
        interests=interests
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user
```

### 2. User Signin (Authenticate + Create Session)

**Service**: `backend/src/users/services.py:authenticate_user()` + `create_user_session()`

```python
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user_session(db: Session, user_id: UUID, user_agent: str, ip_address: str) -> Tuple[str, str]:
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    session = Session(
        user_id=user_id,
        refresh_token=hash_token(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=7),
        user_agent=user_agent,
        ip_address=ip_address
    )
    db.add(session)
    db.commit()

    return access_token, refresh_token
```

### 3. Get User with Profile (For Personalization)

**Service**: `backend/src/users/services.py:get_user_with_profile()`

```python
def get_user_with_profile(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).options(
        joinedload(User.profile)
    ).filter(User.id == user_id).first()
```

### 4. Log Chatbot Query (For Analytics)

**Service**: `backend/src/users/services.py:log_chatbot_query()`

```python
def log_chatbot_query(
    db: Session,
    user_id: Optional[UUID],
    query_text: str,
    response_text: str,
    personalization_context: Optional[dict]
) -> ChatbotQuery:
    query = ChatbotQuery(
        user_id=user_id,
        query_text=query_text,
        response_text=response_text,
        personalization_context=personalization_context
    )
    db.add(query)
    db.commit()
    return query
```

---

## Validation Rules

### Email Validation
- **Format**: RFC 5322 compliant (using `email-validator` library)
- **Uniqueness**: Must be unique across all users
- **Case Sensitivity**: Stored as lowercase

### Password Validation
- **Minimum Length**: 8 characters
- **Complexity**: Must contain at least one letter and one number
- **Hashing**: Bcrypt with 12 rounds

### Profile Validation
- **software_experience**: Must be one of `BEGINNER`, `INTERMEDIATE`, `ADVANCED`
- **hardware_experience**: Must be one of `NONE`, `BASIC`, `ADVANCED`
- **interests**: Array of strings (can be empty)

---

## Performance Considerations

### Query Optimization
1. **Indexes**: All foreign keys indexed for join performance
2. **Eager Loading**: Use `joinedload` to avoid N+1 queries when fetching user + profile
3. **Connection Pooling**: SQLAlchemy connection pool (max 20 connections)

### Scalability
- **UUID Primary Keys**: Distributed ID generation (no single point of failure)
- **JSONB for Interests**: Flexible schema, indexed for fast queries
- **Session Cleanup**: Background job to delete expired sessions (prevents table bloat)

---

## Security Notes

1. **Password Hashing**: Bcrypt with 12 rounds (industry standard)
2. **Token Hashing**: Refresh tokens hashed in database (same as passwords)
3. **Cascade Deletes**: User deletion removes all related data (GDPR compliance)
4. **Soft Deletes**: `is_active` flag allows account deactivation without data loss
5. **Query Logging**: Optional query history for analytics (PII concerns - review data retention policy)

---

## Future Enhancements

1. **Email Verification**: Add `email_verified` boolean to User table
2. **Password Reset**: Add `password_reset_tokens` table
3. **OAuth Integration**: Add `oauth_accounts` table for social login
4. **User Preferences**: Extend UserProfile with `preferences` JSONB column
5. **Session Management UI**: Show active sessions to users (list devices)
6. **Query Feedback**: Add `helpful` boolean to ChatbotQuery for quality metrics

---

## Summary

**Schema Status**: ✅ Fully implemented in backend
**Migration Status**: ✅ Applied to production database
**ORM Models**: ✅ Defined in `backend/src/users/models.py`
**Services**: ✅ Implemented in `backend/src/users/services.py`

**No database changes required for this feature** - all necessary tables and columns already exist.
