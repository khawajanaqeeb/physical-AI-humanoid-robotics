# Quickstart: Implementation Guide

**Feature**: Better Auth User Authentication and Personalized RAG Chatbot
**For**: Developers implementing this feature
**Time to Complete**: ~11 hours (core features)

This quickstart provides a condensed implementation checklist. For detailed explanations, see `plan.md`.

---

## Prerequisites Checklist

- [ ] PostgreSQL database created on Neon (https://neon.tech)
- [ ] DATABASE_URL copied from Neon dashboard
- [ ] BETTER_AUTH_SECRET generated (`openssl rand -hex 32`)
- [ ] `.env` file updated with new environment variables
- [ ] `.env.example` updated with placeholders
- [ ] Python dependencies installed (`pip install -r backend/requirements.txt`)

---

## Phase 0: Setup (1 hour)

### 0.1 Environment Variables

Add to `backend/.env`:
```bash
DATABASE_URL=postgresql://user:password@hostname:5432/database
BETTER_AUTH_SECRET=<64-character-hex-string>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 0.2 Install Dependencies

Add to `backend/requirements.txt`:
```
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
SQLAlchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
email-validator==2.1.0
```

Run: `pip install -r requirements.txt`

**Commit**: `chore(config): add environment variables and dependencies for authentication`

---

## Phase 1: Database (2 hours)

### 1.1 Create Database Module

```bash
mkdir -p backend/src/database/migrations/versions
```

Create:
- `backend/src/database/base.py` → SQLAlchemy declarative base
- `backend/src/database/session.py` → Database session factory
- `backend/src/database/__init__.py` → Module exports

Update `backend/src/core/config.py`:
```python
database_url: str = Field(..., env="DATABASE_URL")
better_auth_secret: str = Field(..., env="BETTER_AUTH_SECRET")
access_token_expire_minutes: int = 15
refresh_token_expire_days: int = 7
```

**Commit**: `feat(database): add SQLAlchemy base and session management`

### 1.2 Create Models

Create `backend/src/users/models.py` with:
- `User` model (id, email, hashed_password, is_active, timestamps)
- `UserProfile` model (user_id FK, software_experience, hardware_experience, interests)
- `Session` model (user_id FK, access_token, refresh_token, expires_at)
- `ChatbotQuery` model (optional, for analytics)

See `data-model.md` for full SQLAlchemy code.

**Commit**: `feat(database): add User, UserProfile, Session models`

### 1.3 Create Migration

```bash
cd backend
alembic init src/database/migrations
alembic revision --autogenerate -m "Initial auth schema"
alembic upgrade head
```

Verify tables created: `users`, `user_profiles`, `sessions`, `chatbot_queries`

**Commit**: `feat(database): add Alembic initial migration for auth schema`

---

## Phase 2: Authentication (3 hours)

### 2.1 Security Utilities

Create `backend/src/auth/security.py` with:
- `hash_password(password: str) -> str` → bcrypt hashing
- `verify_password(plain: str, hashed: str) -> bool` → password verification
- `create_access_token(data: dict) -> str` → JWT generation
- `create_refresh_token() -> str` → UUID generation
- `verify_access_token(token: str) -> dict` → JWT validation

**Commit**: `feat(auth): implement password hashing and JWT utilities`

### 2.2 Pydantic Schemas

Create:
- `backend/src/auth/schemas.py` → SignupRequest, SigninRequest, AuthResponse
- `backend/src/users/schemas.py` → ProfileDetails, UserProfileResponse, UpdateProfileRequest

Include password strength validation in SignupRequest.

**Commit**: `feat(auth): add Pydantic schemas for auth and profile`

### 2.3 User Services

Create `backend/src/users/services.py` with:
- `create_user(db, signup_data) -> User` → Create user + profile
- `authenticate_user(db, email, password) -> User` → Validate credentials
- `create_user_session(db, user, user_agent, ip) -> Session` → Issue tokens
- `get_user_by_token(db, token) -> User` → Fetch user from JWT
- `refresh_user_session(db, refresh_token) -> Session` → Rotate tokens
- `delete_user_session(db, user_id, token)` → Signout
- `update_user_profile(db, user_id, update_data) -> UserProfile` → Update profile

**Commit**: `feat(users): implement user and session management services`

### 2.4 Auth Endpoints

Create `backend/src/auth/routes.py` with:
- `POST /auth/signup` → Call create_user, create_user_session, return tokens
- `POST /auth/signin` → Call authenticate_user, create_user_session, return tokens
- `POST /auth/signout` → Require auth, delete session
- `POST /auth/refresh` → Validate refresh token, issue new tokens

Register in `backend/src/main.py`:
```python
from src.auth import routes as auth_routes
app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Authentication"])
```

**Commit**: `feat(auth): add signup, signin, signout, refresh endpoints`

### 2.5 Auth Dependencies

Create `backend/src/auth/dependencies.py` with:
- `get_current_user(token, db) -> User` → Extract and validate JWT, fetch user
- `get_current_user_optional(token, db) -> Optional[User]` → Optional auth for query endpoint

**Commit**: `feat(auth): add FastAPI dependencies for current user validation`

---

## Phase 3: Profile Management (1 hour)

### 3.1 Profile Endpoints

Create `backend/src/users/routes.py` with:
- `GET /profile` → Require auth, return UserProfileResponse
- `PUT /profile` → Require auth, update profile, return UserProfileResponse

Register in `backend/src/main.py`:
```python
from src.users import routes as user_routes
app.include_router(user_routes.router, prefix="/api/v1", tags=["Profile"])
```

**Commit**: `feat(users): add GET and PUT /profile endpoints`

---

## Phase 4: RAG Personalization (1.5 hours)

### 4.1 Personalization Prompts

Create `backend/src/services/personalization.py` with:
- `build_personalized_prompt(profile: UserProfile) -> str`
- Define templates for Beginner, Intermediate, Advanced experience levels
- Inject interests into prompts

**Commit**: `feat(rag): add personalization prompt templates`

### 4.2 Integrate into Query Endpoint

Modify `backend/src/api/routes/query.py`:
1. Add `get_current_user_optional` dependency
2. If user authenticated, fetch profile and build personalized prompt
3. Pass `personalized_prompt` to rag_service.query_textbook()
4. Add `personalization_applied` boolean to response

Modify `backend/src/services/rag_service.py`:
1. Add `system_prompt: Optional[str]` parameter to `query_textbook()`
2. Pass `system_prompt` (or `preamble`) to Cohere generation
3. DO NOT modify retrieval logic (Qdrant queries unchanged)

**Commit**: `feat(rag): integrate user profile personalization into chatbot query`

### 4.3 Fallback Handling

Wrap personalization logic in try-except:
```python
try:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile:
        personalized_prompt = build_personalized_prompt(profile)
except Exception as e:
    logger.warning(f"Profile fetch failed: {e}")
    # Continue with standard prompt (graceful degradation)
```

**Commit**: `feat(rag): add fallback handling for personalization failures`

---

## Phase 5: Testing (1.5 hours)

### 5.1 Manual API Tests

Test with curl or Postman:

1. Signup:
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!", "software_experience": "Beginner", "hardware_experience": "None", "interests": ["AI"]}'
```

2. Signin:
```bash
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!"}'
```

3. Get Profile:
```bash
curl -X GET http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer <access_token>"
```

4. Update Profile:
```bash
curl -X PUT http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"software_experience": "Advanced"}'
```

5. Personalized Query:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are servo motors?"}'
```

6. Unauthenticated Query:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are servo motors?"}'
```

**Commit**: `test: verify all auth and personalization endpoints`

### 5.2 Edge Case Tests

- Signup with existing email → 400
- Signin with wrong password → 401
- Protected endpoint without token → 401
- Update profile with invalid enum → 400
- Query with profile fetch failure → Falls back to standard response

**Commit**: `test: verify error handling and edge cases`

---

## Phase 6: Documentation (1 hour)

### 6.1 Update README

Update `backend/README.md` with:
- Authentication setup instructions
- New environment variables
- API endpoint examples
- Database migration commands

**Commit**: `docs: update README with authentication setup`

### 6.2 Final Integration Test

End-to-end test:
1. Signup as beginner user
2. Ask question → Verify simplified response
3. Update to advanced profile
4. Ask same question → Verify technical response
5. Signout and query → Verify standard response

**Commit**: `test: end-to-end integration test`

---

## Quick Reference

### Environment Variables
```bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=<64-char-hex>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Database Commands
```bash
alembic upgrade head       # Apply migrations
alembic downgrade -1       # Rollback last migration
alembic history            # View migration history
```

### Testing Shortcuts
```bash
# Start server
cd backend
uvicorn src.main:app --reload

# Test signup
curl -X POST localhost:8000/api/v1/auth/signup -H "Content-Type: application/json" -d @test_signup.json

# Test signin
curl -X POST localhost:8000/api/v1/auth/signin -H "Content-Type: application/json" -d @test_signin.json
```

### File Structure Summary
```
backend/
├── src/
│   ├── auth/
│   │   ├── security.py       # Password hashing, JWT
│   │   ├── schemas.py        # Signup/Signin models
│   │   ├── routes.py         # Auth endpoints
│   │   └── dependencies.py   # get_current_user
│   ├── users/
│   │   ├── models.py         # User, UserProfile, Session
│   │   ├── schemas.py        # Profile models
│   │   ├── services.py       # Business logic
│   │   └── routes.py         # Profile endpoints
│   ├── database/
│   │   ├── base.py           # SQLAlchemy base
│   │   ├── session.py        # DB session
│   │   └── migrations/       # Alembic migrations
│   ├── services/
│   │   ├── personalization.py # Prompt templates
│   │   └── rag_service.py    # MODIFIED: Add system_prompt param
│   └── api/routes/
│       └── query.py          # MODIFIED: Add personalization
```

---

## Troubleshooting

**"alembic: command not found"**
```bash
pip install alembic==1.13.1
```

**"could not connect to server"**
- Verify DATABASE_URL is correct
- Check Neon database is running
- Test connection: `psql $DATABASE_URL`

**"JWT decode error"**
- Verify BETTER_AUTH_SECRET matches between token creation and validation
- Check token hasn't expired (15 min default)

**"Profile fetch failed but query works"**
- This is expected! Fallback handling ensures RAG continues without personalization

**"Personalization not applied"**
- Verify user is authenticated (Authorization header present)
- Check profile exists for user in database
- Review server logs for personalization errors

---

## Success Checklist

- [ ] All dependencies installed
- [ ] Database created and migrated
- [ ] Environment variables configured
- [ ] Signup endpoint working (creates user + profile)
- [ ] Signin endpoint working (returns tokens)
- [ ] Profile endpoints working (GET/PUT)
- [ ] Personalized query working (different responses for beginner vs advanced)
- [ ] Unauthenticated query working (existing RAG preserved)
- [ ] All error cases handled gracefully
- [ ] Documentation updated
- [ ] Zero secrets committed to git

---

**Implementation Time**: ~11 hours for core features
**Optional Bonus**: +2-3 hours for email verification, password reset
**Status**: READY TO START

For detailed explanations, architecture decisions, and risk mitigation, see `plan.md`.
