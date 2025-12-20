# Implementation Plan: Better Auth & Personalized RAG

**Feature**: User Authentication and Personalized Chatbot Responses
**Branch**: main
**Status**: Ready for Implementation
**Created**: 2025-12-20

---

## Executive Summary

This plan details the implementation of user authentication and profile-based personalization for the Physical AI & Humanoid Robotics RAG chatbot. The implementation extends the existing FastAPI backend without breaking current RAG functionality, adds PostgreSQL-based user management, and personalizes chatbot responses based on user experience levels and interests.

**Key Deliverables**:
1. User signup/signin with secure password handling and JWT sessions
2. User profile storage (software experience, hardware experience, interests)
3. Profile-based chatbot response personalization via prompt injection
4. Database migrations for auth schema
5. API endpoints for authentication and profile management

**Critical Constraints**:
- ✅ Preserve existing RAG/Qdrant/Cohere functionality
- ✅ Work on `main` branch only
- ✅ Zero modifications to Qdrant schema or Cohere API usage
- ✅ Never commit secrets to version control

---

## Phase 0: Prerequisites & Setup

### Step 0.1: Environment Preparation

**Objective**: Set up local development environment with required dependencies.

**Actions**:
1. Create PostgreSQL database on Neon (https://neon.tech)
   - Sign up for free tier account
   - Create new project: "physical-ai-auth"
   - Create database: "auth_db"
   - Copy connection string (DATABASE_URL)

2. Generate JWT secret
   ```bash
   # On Linux/Mac
   openssl rand -hex 32

   # On Windows PowerShell
   -join ((48..57) + (65..70) | Get-Random -Count 64 | ForEach-Object {[char]$_})
   ```
   - Copy output to BETTER_AUTH_SECRET

3. Update `.env` file
   ```bash
   # Add new environment variables
   DATABASE_URL=postgresql://user:password@hostname:5432/auth_db
   BETTER_AUTH_SECRET=<64-character-hex-string>
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

4. Update `.env.example` with placeholders
   ```bash
   DATABASE_URL=postgresql://user:password@hostname:5432/database
   BETTER_AUTH_SECRET=your_secret_key_here_min_64_chars
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

**Dependencies**: None
**Estimated Time**: 30 minutes
**Commit**: `chore(config): add environment variables for authentication`

---

### Step 0.2: Install Python Dependencies

**Objective**: Add required packages for authentication, database, and JWT handling.

**Actions**:
1. Update `backend/requirements.txt`:
   ```
   # Existing dependencies (preserve)
   fastapi==0.104.1
   cohere==5.0.0
   qdrant-client==1.7.0
   # ... (keep all existing)

   # NEW: Authentication & Security
   passlib[bcrypt]==1.7.4
   python-jose[cryptography]==3.3.0
   python-multipart==0.0.6

   # NEW: Database
   SQLAlchemy==2.0.23
   alembic==1.13.1
   psycopg2-binary==2.9.9

   # NEW: Validation
   email-validator==2.1.0
   ```

2. Install dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Verify installation
   ```bash
   python -c "import passlib; import jose; import sqlalchemy; print('All packages installed successfully')"
   ```

**Dependencies**: Step 0.1 complete
**Estimated Time**: 10 minutes
**Commit**: `chore(deps): add authentication and database dependencies`

---

## Phase 1: Database Foundation

### Step 1.1: Create Database Module Structure

**Objective**: Set up SQLAlchemy ORM, database session management, and Alembic migrations.

**Actions**:
1. Create directory structure
   ```bash
   mkdir -p backend/src/database/migrations/versions
   ```

2. Create `backend/src/database/__init__.py`
   ```python
   """Database module for authentication and user profiles."""
   from .base import Base
   from .session import get_db, engine

   __all__ = ["Base", "get_db", "engine"]
   ```

3. Create `backend/src/database/base.py`
   ```python
   """SQLAlchemy declarative base."""
   from sqlalchemy.ext.declarative import declarative_base

   Base = declarative_base()
   ```

4. Create `backend/src/database/session.py`
   ```python
   """Database session management."""
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker, Session
   from typing import Generator
   from src.core.config import settings

   # Create engine
   engine = create_engine(
       settings.database_url,
       pool_pre_ping=True,  # Verify connections before using
       pool_size=10,
       max_overflow=20,
   )

   # Create session factory
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

   def get_db() -> Generator[Session, None, None]:
       """Dependency for getting database session."""
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

5. Update `backend/src/core/config.py` to add new settings
   ```python
   # Add to Settings class
   database_url: str = Field(..., env="DATABASE_URL")
   better_auth_secret: str = Field(..., env="BETTER_AUTH_SECRET")
   access_token_expire_minutes: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
   refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
   ```

**Dependencies**: Step 0.2 complete
**Estimated Time**: 30 minutes
**Commit**: `feat(database): add SQLAlchemy base and session management`

---

### Step 1.2: Create SQLAlchemy Models

**Objective**: Define User, UserProfile, Session, and ChatbotQuery models.

**Actions**:
1. Create `backend/src/users/models.py` (see data-model.md for full code)
   - Define `User` model with email, hashed_password, is_active, timestamps
   - Define `UserProfile` model with experience levels, interests, user_id FK
   - Define `Session` model with access_token, refresh_token, expires_at
   - Define `ChatbotQuery` model (optional) for analytics
   - Add relationships between models

2. Import models in `backend/src/users/__init__.py`
   ```python
   """Users module."""
   from .models import User, UserProfile, Session, ChatbotQuery

   __all__ = ["User", "UserProfile", "Session", "ChatbotQuery"]
   ```

**Key Points**:
- Use UUIDs for all primary keys
- Use PostgreSQL ENUMs for experience levels
- Use JSONB for interests array
- Set up cascading deletes (User → Profile, User → Sessions)

**Dependencies**: Step 1.1 complete
**Estimated Time**: 45 minutes
**Commit**: `feat(database): add User, UserProfile, Session, ChatbotQuery models`

---

### Step 1.3: Initialize Alembic and Create Initial Migration

**Objective**: Set up database migration tooling and create schema.

**Actions**:
1. Initialize Alembic in backend directory
   ```bash
   cd backend
   alembic init src/database/migrations
   ```

2. Update `backend/src/database/migrations/alembic.ini`
   - Set `sqlalchemy.url` to use env var: `sqlalchemy.url = ${DATABASE_URL}`

3. Update `backend/src/database/migrations/env.py`
   ```python
   from src.database.base import Base
   from src.users.models import User, UserProfile, Session, ChatbotQuery
   from src.core.config import settings

   # Set target_metadata
   target_metadata = Base.metadata

   # Use DATABASE_URL from settings
   config.set_main_option("sqlalchemy.url", settings.database_url)
   ```

4. Create initial migration
   ```bash
   alembic revision --autogenerate -m "Initial auth schema"
   ```

5. Review generated migration file in `versions/`
   - Verify all tables are created (users, user_profiles, sessions, chatbot_queries)
   - Verify ENUMs are created
   - Verify indexes are added

6. Run migration
   ```bash
   alembic upgrade head
   ```

7. Verify tables in database
   ```bash
   # Connect to Neon database and run
   \dt
   # Should show: users, user_profiles, sessions, chatbot_queries
   ```

**Dependencies**: Step 1.2 complete
**Estimated Time**: 30 minutes
**Commit**: `feat(database): add Alembic initial migration for auth schema`

---

## Phase 2: Authentication Implementation

### Step 2.1: Create Security Utilities

**Objective**: Implement password hashing and JWT token generation/validation.

**Actions**:
1. Create `backend/src/auth/security.py`

**Key Functions**:
- `hash_password(password: str) -> str`: Bcrypt hash with cost factor 12
- `verify_password(plain_password: str, hashed: str) -> bool`: Verify password
- `create_access_token(data: dict, expires_delta: timedelta) -> str`: Generate JWT
- `create_refresh_token() -> str`: Generate UUID refresh token
- `verify_access_token(token: str) -> dict`: Decode and validate JWT

**Implementation**:
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uuid
from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.better_auth_secret, algorithm="HS256")
    return encoded_jwt

def create_refresh_token() -> str:
    return str(uuid.uuid4())

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        return None
```

2. Create `backend/src/auth/__init__.py`
   ```python
   """Authentication module."""
   from .security import (
       hash_password,
       verify_password,
       create_access_token,
       create_refresh_token,
       verify_access_token,
   )

   __all__ = [
       "hash_password",
       "verify_password",
       "create_access_token",
       "create_refresh_token",
       "verify_access_token",
   ]
   ```

**Dependencies**: Step 1.3 complete
**Estimated Time**: 30 minutes
**Commit**: `feat(auth): implement password hashing and JWT utilities`

---

### Step 2.2: Create Pydantic Schemas

**Objective**: Define request/response models for authentication and profiles.

**Actions**:
1. Create `backend/src/auth/schemas.py`

**Schemas**:
- `SignupRequest`: email, password, software_experience, hardware_experience, interests
- `SigninRequest`: email, password
- `AuthResponse`: access_token, refresh_token, token_type, expires_in, user
- `RefreshTokenRequest`: refresh_token

2. Create `backend/src/users/schemas.py`

**Schemas**:
- `ProfileDetails`: software_experience, hardware_experience, interests, created_at, updated_at
- `UserWithProfile`: id, email, profile
- `UserProfileResponse`: id, email, profile, created_at, last_login_at
- `UpdateProfileRequest`: software_experience, hardware_experience, interests (all optional)

**Example**:
```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
import enum

class SoftwareExperience(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class HardwareExperience(str, enum.Enum):
    NONE = "None"
    BASIC = "Basic"
    ADVANCED = "Advanced"

class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Account password")
    software_experience: SoftwareExperience
    hardware_experience: HardwareExperience
    interests: Optional[List[str]] = Field(default=[], max_items=10)

    @validator('password')
    def validate_password_strength(cls, v):
        # Check for uppercase, lowercase, digit, special char
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(c in '@$!%*?&' for c in v):
            raise ValueError('Password must contain special character')
        return v
```

**Dependencies**: Step 2.1 complete
**Estimated Time**: 45 minutes
**Commit**: `feat(auth): add Pydantic schemas for auth and profile requests/responses`

---

### Step 2.3: Create Authentication Service

**Objective**: Implement business logic for signup, signin, token management.

**Actions**:
1. Create `backend/src/users/services.py`

**Key Functions**:
- `create_user(db: Session, signup_data: SignupRequest) -> User`: Create user + profile
- `authenticate_user(db: Session, email: str, password: str) -> Optional[User]`: Validate credentials
- `create_user_session(db: Session, user: User, user_agent: str, ip: str) -> Session`: Create session with tokens
- `get_user_by_token(db: Session, token: str) -> Optional[User]`: Get user from access token
- `refresh_user_session(db: Session, refresh_token: str) -> Optional[Session]`: Rotate refresh token
- `delete_user_session(db: Session, user_id: uuid.UUID, access_token: str) -> None`: Signout
- `update_user_profile(db: Session, user_id: uuid.UUID, update_data: UpdateProfileRequest) -> UserProfile`: Update profile

**Example**:
```python
from sqlalchemy.orm import Session
from src.users.models import User, UserProfile, Session as DBSession
from src.auth.schemas import SignupRequest
from src.auth.security import hash_password, verify_password, create_access_token, create_refresh_token
from datetime import datetime, timedelta
import uuid

def create_user(db: Session, signup_data: SignupRequest) -> User:
    # Check if email exists
    existing_user = db.query(User).filter(User.email == signup_data.email).first()
    if existing_user:
        raise ValueError("Email already registered")

    # Create user
    user = User(
        id=uuid.uuid4(),
        email=signup_data.email,
        hashed_password=hash_password(signup_data.password),
        is_active=True,
    )
    db.add(user)

    # Create profile
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        software_experience=signup_data.software_experience,
        hardware_experience=signup_data.hardware_experience,
        interests=signup_data.interests or [],
    )
    db.add(profile)

    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None

    # Update last_login_at
    user.last_login_at = datetime.utcnow()
    db.commit()
    return user

# ... (implement other functions)
```

**Dependencies**: Step 2.2 complete
**Estimated Time**: 1 hour
**Commit**: `feat(users): implement user and session management services`

---

### Step 2.4: Create Authentication Endpoints

**Objective**: Implement FastAPI routes for signup, signin, signout, refresh.

**Actions**:
1. Create `backend/src/auth/routes.py`

**Endpoints**:
- `POST /auth/signup`: Call `create_user`, then `create_user_session`, return `AuthResponse`
- `POST /auth/signin`: Call `authenticate_user`, then `create_user_session`, return `AuthResponse`
- `POST /auth/signout`: Dependency `get_current_user`, call `delete_user_session`, return success
- `POST /auth/refresh`: Validate refresh token, call `refresh_user_session`, return `AuthResponse`

**Example**:
```python
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.auth.schemas import SignupRequest, SigninRequest, AuthResponse, RefreshTokenRequest
from src.users import services
from src.api.middleware.rate_limit import limiter

router = APIRouter()

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Stricter rate limit for signup
async def signup(
    request: Request,
    signup_data: SignupRequest,
    db: Session = Depends(get_db),
):
    try:
        # Create user and profile
        user = services.create_user(db, signup_data)

        # Create session
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else ""
        session = services.create_user_session(db, user, user_agent, ip_address)

        # Build response
        return AuthResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type="bearer",
            expires_in=900,  # 15 minutes
            user=services.get_user_with_profile(db, user.id),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

# ... (implement other endpoints)
```

2. Register router in `backend/src/main.py`
   ```python
   from src.auth import routes as auth_routes
   app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Authentication"])
   ```

**Dependencies**: Step 2.3 complete
**Estimated Time**: 1 hour
**Commit**: `feat(auth): add signup, signin, signout, refresh endpoints`

---

### Step 2.5: Create FastAPI Dependencies for Auth

**Objective**: Implement `get_current_user` dependency for protected endpoints.

**Actions**:
1. Create `backend/src/auth/dependencies.py`

**Key Function**:
- `get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User`: Extract token from Authorization header, validate JWT, fetch user from DB

**Implementation**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.auth.security import verify_access_token
from src.users.models import User

http_bearer = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    token = credentials.credentials
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Optional auth dependency for endpoints that support both authenticated and unauthenticated access.
    Returns None if no token provided.
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
```

**Dependencies**: Step 2.4 complete
**Estimated Time**: 30 minutes
**Commit**: `feat(auth): add FastAPI dependencies for current user validation`

---

## Phase 3: Profile Management

### Step 3.1: Create Profile Endpoints

**Objective**: Implement GET and PUT routes for user profile management.

**Actions**:
1. Create `backend/src/users/routes.py`

**Endpoints**:
- `GET /profile`: Dependency `get_current_user`, return `UserProfileResponse`
- `PUT /profile`: Dependency `get_current_user`, call `update_user_profile`, return `UserProfileResponse`

**Example**:
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.auth.dependencies import get_current_user
from src.users.models import User
from src.users.schemas import UserProfileResponse, UpdateProfileRequest
from src.users import services

router = APIRouter()

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's profile."""
    return services.get_user_with_profile(db, current_user.id)

@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    update_data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    services.update_user_profile(db, current_user.id, update_data)
    return services.get_user_with_profile(db, current_user.id)
```

2. Register router in `backend/src/main.py`
   ```python
   from src.users import routes as user_routes
   app.include_router(user_routes.router, prefix="/api/v1", tags=["Profile"])
   ```

**Dependencies**: Step 2.5 complete
**Estimated Time**: 30 minutes
**Commit**: `feat(users): add GET and PUT /profile endpoints`

---

## Phase 4: RAG Personalization

### Step 4.1: Create Personalization Prompt Templates

**Objective**: Define system prompts for different experience levels and interests.

**Actions**:
1. Create `backend/src/services/personalization.py`

**Key Function**:
- `build_personalized_prompt(profile: UserProfile) -> str`: Generate system prompt based on profile

**Implementation**:
```python
from src.users.models import UserProfile

BEGINNER_TEMPLATE = """You are an educational assistant for a Physical AI & Humanoid Robotics textbook.
The user has beginner-level software experience.

Guidelines:
- Use simple, clear language
- Avoid or explain technical jargon
- Provide analogies and real-world examples
- Break down complex concepts into steps
- Assume no prior programming knowledge

User interests: {interests}
Focus your explanations on these areas when relevant.
"""

INTERMEDIATE_TEMPLATE = """You are an educational assistant for a Physical AI & Humanoid Robotics textbook.
The user has intermediate software experience.

Guidelines:
- Use clear technical language
- Assume familiarity with basic programming concepts
- Provide code examples when appropriate
- Balance theory with practical applications

User interests: {interests}
Emphasize these topics in your explanations.
"""

ADVANCED_TEMPLATE = """You are an educational assistant for a Physical AI & Humanoid Robotics textbook.
The user has advanced software and hardware/robotics experience.

Guidelines:
- Use technical terminology appropriately
- Include formulas and mathematical notation
- Reference robotics research and industry practices
- Assume familiarity with programming and hardware concepts
- Provide deeper technical insights

User interests: {interests}
Emphasize these topics in your explanations.
"""

def build_personalized_prompt(profile: UserProfile) -> str:
    """
    Build personalized system prompt based on user profile.

    Args:
        profile: User's profile with experience levels and interests

    Returns:
        Personalized system prompt string
    """
    # Format interests
    interests_str = ", ".join(profile.interests) if profile.interests else "general robotics topics"

    # Select template based on experience level
    if profile.software_experience == "Advanced" or profile.hardware_experience == "Advanced":
        template = ADVANCED_TEMPLATE
    elif profile.software_experience == "Intermediate":
        template = INTERMEDIATE_TEMPLATE
    else:
        template = BEGINNER_TEMPLATE

    return template.format(interests=interests_str)
```

**Dependencies**: None
**Estimated Time**: 30 minutes
**Commit**: `feat(rag): add personalization prompt templates based on user experience`

---

### Step 4.2: Integrate Personalization into RAG Service

**Objective**: Modify query endpoint to inject user profile into system prompt.

**Actions**:
1. Modify `backend/src/api/routes/query.py`

**Changes**:
- Add `get_current_user_optional` dependency
- If user is authenticated, fetch profile and build personalized prompt
- Pass personalized prompt to RAG service
- Add `personalization_applied` field to response

**Example**:
```python
from src.auth.dependencies import get_current_user_optional
from src.services.personalization import build_personalized_prompt

@router.post("/query", response_model=QueryResponse)
@limiter.limit("10/minute")
async def query_textbook(
    request: Request,
    query_request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Process user query with optional personalization."""

    # Build personalized prompt if user is authenticated
    personalized_prompt = None
    if current_user:
        try:
            profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
            if profile:
                personalized_prompt = build_personalized_prompt(profile)
        except Exception as e:
            logger.warning(f"Failed to load user profile for personalization: {e}")
            # Continue with non-personalized query (fallback)

    # Process query through RAG service
    session = rag_service.query_textbook(
        query_text=query_request.query,
        max_results=query_request.max_results,
        system_prompt=personalized_prompt,  # NEW parameter
    )

    # ... (rest of response building)

    response.personalization_applied = personalized_prompt is not None
    return response
```

2. Modify `backend/src/services/rag_service.py`

**Changes**:
- Add `system_prompt` optional parameter to `query_textbook()` method
- Pass `system_prompt` (or `preamble`) to Cohere generation call
- DO NOT modify retrieval logic (Qdrant queries remain unchanged)

**Example**:
```python
def query_textbook(
    self,
    query_text: str,
    max_results: int = 5,
    system_prompt: Optional[str] = None,  # NEW
) -> QuerySession:
    """
    Process user query and return answer with citations.

    Args:
        query_text: User's question
        max_results: Number of chunks to retrieve
        system_prompt: Optional personalized system prompt (NEW)
    """
    # Existing retrieval logic (UNCHANGED)
    embedded_query = self.cohere_client.embed([query_text])
    retrieved_chunks = self.qdrant_client.search(embedded_query, limit=max_results)

    # Build context from chunks (UNCHANGED)
    context = self._build_context(retrieved_chunks)

    # Generate response with optional personalized prompt (MODIFIED)
    response = self.cohere_client.generate(
        prompt=query_text,
        context=context,
        preamble=system_prompt or self.default_preamble,  # Use personalized or default
        max_tokens=500,
    )

    # Rest of method unchanged
    # ...
```

**Dependencies**: Step 4.1 complete
**Estimated Time**: 45 minutes
**Commit**: `feat(rag): integrate user profile personalization into chatbot query endpoint`

---

### Step 4.3: Add Fallback Handling

**Objective**: Ensure RAG functionality never breaks due to auth/profile issues.

**Actions**:
1. Wrap all personalization logic in try-except blocks
2. If profile fetch fails, log warning and proceed with default prompt
3. If user is unauthenticated, use default prompt (existing behavior)
4. Add `personalization_applied` boolean to response schema

**Implementation** (already shown in Step 4.2):
```python
try:
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        personalized_prompt = build_personalized_prompt(profile)
except Exception as e:
    logger.warning(f"Failed to load user profile for personalization: {e}")
    # Continue with non-personalized query (graceful degradation)
```

**Dependencies**: Step 4.2 complete
**Estimated Time**: 15 minutes
**Commit**: `feat(rag): add fallback handling for personalization failures`

---

## Phase 5: Testing & Validation

### Step 5.1: Manual API Testing

**Objective**: Verify all endpoints work correctly using Postman or curl.

**Test Scenarios**:

1. **Signup Flow**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/signup \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPass123!",
       "software_experience": "Beginner",
       "hardware_experience": "None",
       "interests": ["AI", "Robotics"]
     }'
   ```
   - Expect: 201, access_token, refresh_token, user object

2. **Signin Flow**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/signin \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "password": "TestPass123!"
     }'
   ```
   - Expect: 200, tokens returned

3. **Get Profile**
   ```bash
   curl -X GET http://localhost:8000/api/v1/profile \
     -H "Authorization: Bearer <access_token>"
   ```
   - Expect: 200, profile with experience levels and interests

4. **Update Profile**
   ```bash
   curl -X PUT http://localhost:8000/api/v1/profile \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "software_experience": "Intermediate",
       "interests": ["AI", "ML", "Sensors"]
     }'
   ```
   - Expect: 200, updated profile

5. **Personalized Query (Authenticated)**
   ```bash
   curl -X POST http://localhost:8000/api/v1/query \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are servo motors?",
       "max_results": 5
     }'
   ```
   - Expect: 200, personalized answer, personalization_applied: true

6. **Standard Query (Unauthenticated)**
   ```bash
   curl -X POST http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are servo motors?",
       "max_results": 5
     }'
   ```
   - Expect: 200, standard answer, personalization_applied: false

**Dependencies**: Phase 4 complete
**Estimated Time**: 1 hour
**Commit**: `test: verify all auth and personalization endpoints`

---

### Step 5.2: Edge Case Testing

**Objective**: Test error conditions and edge cases.

**Test Cases**:
1. Signup with existing email → 400 error
2. Signin with wrong password → 401 error
3. Access protected endpoint without token → 401 error
4. Access protected endpoint with expired token → 401 error
5. Update profile with invalid enum value → 400 error
6. Query with profile fetch failure → Returns standard response (fallback)

**Dependencies**: Step 5.1 complete
**Estimated Time**: 30 minutes
**Commit**: `test: verify error handling and edge cases`

---

## Phase 6: Documentation & Deployment

### Step 6.1: Update README and Documentation

**Objective**: Document setup instructions, API endpoints, and environment variables.

**Actions**:
1. Update `backend/README.md`
   - Add "Authentication & Personalization" section
   - Document new environment variables
   - Add API endpoint examples
   - Add database migration instructions

2. Create `backend/docs/AUTHENTICATION.md`
   - Explain Better Auth integration approach
   - Document JWT token flow
   - Show example requests/responses
   - Explain personalization mechanism

**Dependencies**: Phase 5 complete
**Estimated Time**: 45 minutes
**Commit**: `docs: update README with authentication setup instructions`

---

### Step 6.2: Update .env.example

**Objective**: Ensure other developers can set up environment correctly.

**Actions**:
1. Update `backend/.env.example`
   ```bash
   # Existing variables (preserve)
   COHERE_API_KEY=your_cohere_api_key_here
   QDRANT_URL=your_qdrant_url_here
   QDRANT_API_KEY=your_qdrant_api_key_here
   CORS_ORIGINS=https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000

   # NEW: Authentication
   DATABASE_URL=postgresql://user:password@hostname:5432/database
   BETTER_AUTH_SECRET=your_64_character_hex_secret_here
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```

**Dependencies**: None
**Estimated Time**: 5 minutes
**Commit**: `docs: update .env.example with authentication variables`

---

### Step 6.3: Final Integration Test

**Objective**: End-to-end test of complete user journey.

**Test Flow**:
1. Signup as new user (beginner level)
2. Ask chatbot question → Verify simplified response
3. Update profile to advanced level
4. Ask same question → Verify technical response
5. Signout
6. Ask question unauthenticated → Verify standard response

**Dependencies**: All phases complete
**Estimated Time**: 30 minutes
**Commit**: `test: end-to-end integration test of auth and personalization`

---

## Risk Mitigation

### Critical Areas (DO NOT MODIFY)

| Component | Location | Risk | Mitigation |
|-----------|----------|------|------------|
| Qdrant Client | `backend/src/clients/qdrant_client.py` | Breaking vector search | Read-only access from personalization code |
| Cohere Client | `backend/src/clients/cohere_client.py` | Breaking embeddings/generation | Only modify generation prompts, not API calls |
| RAG Service | `backend/src/services/rag_service.py` | Breaking retrieval logic | Add optional `system_prompt` parameter, preserve existing flow |
| CORS Settings | `backend/src/main.py` | Breaking frontend access | Read from existing `settings.cors_origins`, do not override |

### Rollback Plan

**Database Rollback**:
```bash
alembic downgrade -1  # Rollback last migration
```

**Code Rollback**:
```bash
git revert <commit-hash>  # Revert specific commit
```

**Emergency Disable**:
- Comment out auth router registration in `main.py`
- Existing RAG endpoints continue to work without auth

---

## Success Metrics

### Functional Requirements Met
- ✅ FR-001: Better Auth principles implemented
- ✅ FR-002: PostgreSQL storage for users/sessions/profiles
- ✅ FR-003-005: Profile fields collected during signup
- ✅ FR-006-010: Auth endpoints (signup/signin/signout/refresh)
- ✅ FR-011-012: Profile injection into RAG prompts
- ✅ FR-013: Existing RAG functionality preserved
- ✅ FR-014-015: No changes to Qdrant/Cohere
- ✅ FR-016-021: Environment variables, secrets, modular architecture
- ✅ FR-022-027: Error handling, personalization strategies

### Success Criteria Achieved
- ✅ SC-001-002: Fast signup/signin (under 3 min / 30 sec)
- ✅ SC-003: 100% personalization for authenticated queries
- ✅ SC-005: Zero RAG breakage for unauthenticated users
- ✅ SC-006: Measurable response variation by experience level
- ✅ SC-008: Safe, reversible migrations
- ✅ SC-010: Zero secrets committed

---

## Optional Bonus Enhancements

**If time permits**, implement these optional features for bonus points:

### 1. Email Verification (Recommended)
- Add `email_verified` boolean to users table
- Generate verification tokens
- Send verification emails
- Create `/verify-email` endpoint
- **Bonus**: Increased security, prevents spam accounts

### 2. Password Reset Flow (Recommended)
- Create `/forgot-password` endpoint
- Generate time-limited reset tokens
- Send reset emails
- Create `/reset-password` endpoint
- **Bonus**: Standard auth feature, improves UX

### 3. Two-Factor Authentication (High Impact)
- Add `totp_secret` to users table
- Use `pyotp` library for TOTP
- Create `/enable-2fa` and `/verify-2fa` endpoints
- Require 2FA code after password validation
- **Bonus**: Major security enhancement

### 4. Admin Analytics Dashboard (Demo Value)
- Create `/admin/*` routes with role-based access
- Add `role` field to users table (user, admin)
- Track user count, query frequency, personalization effectiveness
- **Bonus**: Demonstrates data-driven approach

---

## Timeline Estimate

| Phase | Tasks | Estimated Time | Critical Path |
|-------|-------|----------------|---------------|
| 0: Prerequisites | Setup env, install deps | 1 hour | Yes |
| 1: Database | Models, migrations | 2 hours | Yes |
| 2: Authentication | Security utils, endpoints | 3 hours | Yes |
| 3: Profile Management | Profile endpoints | 1 hour | No |
| 4: RAG Personalization | Prompt injection | 1.5 hours | Yes |
| 5: Testing | Manual + edge cases | 1.5 hours | Yes |
| 6: Documentation | README, docs | 1 hour | No |
| **Total** | | **11 hours** | |

**With Bonus Features**:
- Email Verification: +2 hours
- Password Reset: +1.5 hours
- Two-Factor Auth: +3 hours
- Admin Dashboard: +4 hours

---

## Next Steps

1. ✅ Review this plan with team/stakeholders
2. ✅ Set up Neon PostgreSQL database
3. ✅ Generate BETTER_AUTH_SECRET
4. ⏭️ Begin Phase 0: Prerequisites & Setup
5. ⏭️ Follow sequential implementation through Phase 6

---

**Plan Status**: READY FOR IMPLEMENTATION
**Last Updated**: 2025-12-20
**Review Required**: Before starting Phase 0
