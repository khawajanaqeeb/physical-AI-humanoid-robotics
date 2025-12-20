# Research & Technology Decisions

**Feature**: Better Auth User Authentication and Personalized RAG Chatbot
**Date**: 2025-12-20
**Status**: Completed

## Overview

This document consolidates research findings and technology decisions for implementing user authentication and personalized RAG chatbot responses. All decisions align with project constraints: extend existing FastAPI backend, use Better Auth for authentication, PostgreSQL (Neon) for data storage, and preserve existing RAG/Qdrant/Cohere functionality.

---

## 1. Better Auth Integration with FastAPI

### Decision
Use Better Auth's Python SDK (if available) or create a FastAPI-compatible wrapper around Better Auth's core authentication logic. Better Auth is primarily a TypeScript/JavaScript library, so we'll need to implement auth patterns manually in Python following Better Auth's principles.

**UPDATE**: After investigation, Better Auth is a JavaScript/TypeScript library without official Python support. We will implement a Python-based authentication system following Better Auth's security principles and patterns, using established Python libraries.

### Rationale
- Better Auth is JavaScript-focused, not Python-native
- FastAPI has mature auth ecosystem with proven patterns
- Implementing auth manually gives full control over security, session management, and PostgreSQL integration
- Can follow Better Auth's security best practices while using Python-native tools

### Implementation Approach
Use Python libraries that follow Better Auth's security principles:
- **passlib + bcrypt**: Industry-standard password hashing (replaces Better Auth's password handling)
- **python-jose**: JWT token generation and validation (replaces Better Auth's session tokens)
- **FastAPI dependencies**: Request-level auth validation
- **SQLAlchemy**: ORM for PostgreSQL user/session management
- **Pydantic**: Request/response validation

### Alternatives Considered
1. **Port Better Auth to Python**: Too time-intensive, reinventing the wheel
2. **Use Auth0 / Firebase**: Violates constraint (Better Auth is self-hosted, no external SaaS)
3. **FastAPI-Users library**: Adds unnecessary complexity, prefer lightweight custom implementation

### References
- FastAPI Security Docs: https://fastapi.tiangolo.com/tutorial/security/
- PassLib Documentation: https://passlib.readthedocs.io/
- Python-JOSE: https://python-jose.readthedocs.io/

---

## 2. Database Schema Design (PostgreSQL on Neon)

### Decision
Use SQLAlchemy ORM with Alembic for migrations. Design normalized schema with separate tables for users, profiles, and sessions.

### Schema Structure

**users table**:
- `id` (UUID, primary key)
- `email` (VARCHAR(255), unique, not null)
- `hashed_password` (VARCHAR(255), not null)
- `is_active` (BOOLEAN, default true)
- `created_at` (TIMESTAMP, default now())
- `last_login_at` (TIMESTAMP, nullable)

**user_profiles table**:
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to users.id, unique, not null)
- `software_experience` (ENUM: 'Beginner', 'Intermediate', 'Advanced', not null)
- `hardware_experience` (ENUM: 'None', 'Basic', 'Advanced', not null)
- `interests` (JSONB, array of strings, nullable)
- `created_at` (TIMESTAMP, default now())
- `updated_at` (TIMESTAMP, default now(), auto-update)

**sessions table**:
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to users.id, not null)
- `access_token` (TEXT, not null, unique)
- `refresh_token` (TEXT, nullable, unique)
- `expires_at` (TIMESTAMP, not null)
- `created_at` (TIMESTAMP, default now())
- `user_agent` (TEXT, nullable)
- `ip_address` (VARCHAR(45), nullable)

**chatbot_queries table** (optional, for analytics):
- `id` (UUID, primary key)
- `user_id` (UUID, foreign key to users.id, nullable) -- null for unauthenticated
- `query_text` (TEXT, not null)
- `response_text` (TEXT, not null)
- `personalization_context` (JSONB, nullable) -- stores profile snapshot at query time
- `created_at` (TIMESTAMP, default now())

### Rationale
- **Normalization**: Separate user_profiles table allows updating profile without touching auth credentials
- **UUIDs**: Better security than auto-increment IDs, prevent enumeration attacks
- **JSONB for interests**: Flexible array storage, queryable with PostgreSQL JSON operators
- **ENUMs for experience levels**: Enforces data integrity at database level
- **Sessions table**: Supports token revocation, device tracking, and refresh token rotation
- **Chatbot queries tracking**: Optional but valuable for personalization analytics

### Alternatives Considered
1. **Embed profile in users table**: Less normalized, harder to extend with new profile fields
2. **Use INTEGER IDs**: UUIDs provide better security and distributed system compatibility
3. **Store interests as comma-separated VARCHAR**: JSONB is more queryable and type-safe

### Migration Strategy
- Use Alembic for all schema changes
- Create initial migration with all tables
- Design rollback strategy for each migration
- Test migrations in development environment before production

---

## 3. Session Management & JWT Token Strategy

### Decision
Use JWT access tokens (short-lived, 15 minutes) with refresh tokens (long-lived, 7 days). Store refresh tokens in database for revocation capability.

### Token Structure

**Access Token (JWT)**:
```json
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "exp": 1640000000,
  "iat": 1639999100,
  "type": "access"
}
```

**Refresh Token** (opaque, stored in DB):
- Random UUID, stored in sessions table
- Mapped to user_id
- Has expiration timestamp
- Can be revoked by deleting from database

### Flow
1. **Signup**: Create user → create profile → issue access + refresh tokens
2. **Signin**: Validate credentials → issue access + refresh tokens
3. **API Request**: Extract access token from `Authorization: Bearer <token>` header → validate JWT → fetch user profile
4. **Token Refresh**: Submit refresh token → validate from DB → issue new access + refresh tokens
5. **Signout**: Delete refresh token from DB → client discards tokens

### Rationale
- **Short-lived access tokens**: Minimize damage if token is compromised
- **Refresh tokens in DB**: Enables revocation (signout, security events)
- **JWT for access**: Stateless validation, no DB lookup on every request
- **Separate token types**: Clear distinction between auth and refresh operations

### Alternatives Considered
1. **Session cookies only**: Less flexible for API clients, CSRF concerns
2. **Long-lived JWT**: Security risk, can't revoke without blacklist
3. **Opaque tokens for both**: Requires DB lookup on every request, performance impact

---

## 4. RAG Personalization Strategy

### Decision
Inject user profile context into the system prompt/preamble BEFORE retrieving chunks from Qdrant. Do NOT modify retrieval logic, Qdrant schema, or Cohere embeddings.

### Implementation

**Current RAG Flow** (from existing code):
```
User Query → Embed with Cohere → Search Qdrant → Retrieve chunks →
Generate response with Cohere (chunks as context)
```

**Enhanced RAG Flow** (with personalization):
```
User Query → Check auth → Fetch user profile (if authenticated) →
Build personalized system prompt → Embed query with Cohere →
Search Qdrant (unchanged) → Retrieve chunks →
Generate response with Cohere (personalized prompt + chunks)
```

### Personalization Prompt Template

**For Beginner Software Experience**:
```
You are an educational assistant for a Physical AI & Humanoid Robotics textbook.
The user has beginner-level software experience.

Guidelines:
- Use simple, clear language
- Avoid or explain technical jargon
- Provide analogies and real-world examples
- Break down complex concepts into steps
- Assume no prior programming knowledge

User interests: {interests_list}
Focus your explanations on these areas when relevant.
```

**For Advanced Software/Hardware Experience**:
```
You are an educational assistant for a Physical AI & Humanoid Robotics textbook.
The user has advanced software and hardware/robotics experience.

Guidelines:
- Use technical terminology appropriately
- Include formulas and mathematical notation
- Reference robotics research and industry practices
- Assume familiarity with programming and hardware concepts
- Provide deeper technical insights

User interests: {interests_list}
Emphasize these topics in your explanations.
```

### Integration Point
Modify `backend/src/services/rag_service.py`:
- Add optional `user_profile` parameter to `query_textbook()` method
- Build personalized preamble based on profile
- Pass preamble to Cohere generation (existing field: `preamble` or `system_message`)
- Keep retrieval logic identical (no changes to Qdrant queries)

### Rationale
- **System prompt injection**: Most effective personalization without re-training models
- **Pre-retrieval**: User context is fixed before Qdrant search, no changes to vector DB
- **Additive approach**: Existing RAG logic untouched, personalization is optional layer
- **Fallback**: Unauthenticated users get default prompt, system remains functional

### Alternatives Considered
1. **Modify embeddings**: Would require re-indexing entire corpus, violates FR-014
2. **Post-retrieval filtering**: Less effective, can't change LLM's explanation style
3. **Separate RAG pipelines**: Code duplication, maintenance burden

---

## 5. Environment Variables & Configuration

### New Environment Variables

**Required for Authentication**:
```bash
# PostgreSQL connection for auth/profiles
DATABASE_URL=postgresql://user:password@hostname:5432/database

# JWT secret for signing tokens (generate with: openssl rand -hex 32)
BETTER_AUTH_SECRET=<64-character-hex-string>

# Optional: JWT expiration times (defaults if not set)
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Existing Variables** (DO NOT MODIFY):
```bash
COHERE_API_KEY=<existing>
QDRANT_URL=<existing>
QDRANT_API_KEY=<existing>
CORS_ORIGINS=https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000
```

### Configuration Management
- Add to `.env` (local development, NOT committed)
- Update `.env.example` with placeholders
- Use Pydantic Settings for type-safe config loading
- Validate required vars at application startup

### Rationale
- **DATABASE_URL**: Standard PostgreSQL connection string format
- **BETTER_AUTH_SECRET**: Name aligns with user's requirement, but used for JWT signing
- **Separate database**: Auth data isolated from Qdrant (vector DB)
- **Expiration config**: Allows tuning without code changes

---

## 6. Error Handling & Security

### Security Measures

**Password Security**:
- Hash passwords with bcrypt (cost factor 12)
- Never log or return passwords in API responses
- Implement password strength requirements:
  - Minimum 8 characters
  - Must include uppercase, lowercase, number, special character

**Token Security**:
- Use secure random generators for refresh tokens
- Sign JWTs with HS256 algorithm
- Validate token expiration on every request
- Include token type in JWT claims to prevent misuse

**Database Security**:
- Use parameterized queries (SQLAlchemy ORM)
- Enable PostgreSQL SSL connections
- Set connection pool limits to prevent exhaustion

**Rate Limiting**:
- Extend existing SlowAPI rate limiter to auth endpoints
- Stricter limits on signup/signin (5/minute per IP)
- Standard limits on profile updates (10/minute)

### Error Handling Strategy

**Auth Errors** (return generic messages to prevent enumeration):
- Invalid credentials → "Invalid email or password"
- Email already exists → "Registration failed" (don't reveal if email exists)
- Expired token → "Session expired, please sign in again"
- Invalid token → "Invalid authentication token"

**Database Errors**:
- Connection failures → "Service temporarily unavailable"
- Constraint violations → Generic validation error
- Log detailed errors server-side for debugging

**Fallback for RAG**:
- If profile fetch fails → Use default (non-personalized) prompt
- If user_id is invalid → Treat as unauthenticated request
- Never fail RAG query due to auth/profile issues

### Rationale
- **Generic error messages**: Prevent attackers from enumerating valid emails or users
- **Graceful degradation**: Auth failures don't break core chatbot functionality
- **Comprehensive logging**: Detailed errors logged server-side for debugging
- **Defense in depth**: Multiple security layers (hashing, rate limiting, token validation)

---

## 7. Folder Structure & Code Organization

### Proposed Backend Structure

```
backend/
├── src/
│   ├── auth/                     # NEW: Authentication module
│   │   ├── __init__.py
│   │   ├── dependencies.py       # FastAPI dependencies (get_current_user, etc.)
│   │   ├── schemas.py            # Pydantic models for signup/signin
│   │   ├── security.py           # Password hashing, JWT functions
│   │   └── routes.py             # Auth endpoints (signup, signin, signout, refresh)
│   │
│   ├── users/                    # NEW: User profile management
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy models (User, UserProfile, Session)
│   │   ├── schemas.py            # Pydantic models for profile requests/responses
│   │   ├── services.py           # Business logic (create_user, update_profile, etc.)
│   │   └── routes.py             # Profile endpoints (GET /profile, PUT /profile)
│   │
│   ├── database/                 # NEW: Database configuration
│   │   ├── __init__.py
│   │   ├── base.py               # SQLAlchemy declarative base
│   │   ├── session.py            # Database session management
│   │   └── migrations/           # Alembic migrations directory
│   │       ├── alembic.ini
│   │       ├── env.py
│   │       └── versions/
│   │           └── 001_initial_auth_schema.py
│   │
│   ├── api/                      # EXISTING: API routes
│   │   ├── routes/
│   │   │   └── query.py          # MODIFY: Add user profile injection
│   │
│   ├── services/                 # EXISTING: Business logic
│   │   └── rag_service.py        # MODIFY: Add personalization support
│   │
│   ├── core/                     # EXISTING: Core utilities
│   │   ├── config.py             # MODIFY: Add DATABASE_URL, BETTER_AUTH_SECRET
│   │   └── exceptions.py         # ADD: Auth-specific exceptions
│   │
│   └── main.py                   # MODIFY: Register auth routes
│
├── .env                          # MODIFY: Add DATABASE_URL, BETTER_AUTH_SECRET
├── .env.example                  # MODIFY: Add placeholder values
└── requirements.txt              # MODIFY: Add new dependencies
```

### Rationale
- **Separation of concerns**: Auth logic isolated in `auth/` module, profiles in `users/`
- **Consistent with existing structure**: Follows patterns from `api/`, `services/`, `core/`
- **Modular**: Easy to extend or modify auth without affecting RAG logic
- **Database isolation**: Dedicated `database/` module for SQLAlchemy and migrations

---

## 8. Dependencies & Requirements

### New Python Packages

Add to `backend/requirements.txt`:
```
# Authentication & Security
passlib[bcrypt]==1.7.4          # Password hashing
python-jose[cryptography]==3.3.0 # JWT token handling
python-multipart==0.0.6         # Form data parsing for auth endpoints

# Database
SQLAlchemy==2.0.23              # ORM for PostgreSQL
alembic==1.13.1                 # Database migrations
psycopg2-binary==2.9.9          # PostgreSQL driver

# Validation (if not already present)
email-validator==2.1.0          # Email format validation
```

### Rationale
- **passlib + bcrypt**: Industry standard for password hashing, better than argon2 for compatibility
- **python-jose**: Lightweight JWT library, well-maintained
- **SQLAlchemy 2.x**: Latest version with improved async support
- **psycopg2-binary**: PostgreSQL driver, binary version for easier installation

---

## 9. Git Commit Strategy

### Commit Sequence

**Phase 1: Foundation** (can be pushed directly to main)
1. `feat(database): add SQLAlchemy models for users and profiles`
2. `feat(database): add Alembic initial migration for auth schema`
3. `feat(auth): implement password hashing and JWT utilities`
4. `feat(config): add DATABASE_URL and BETTER_AUTH_SECRET to settings`

**Phase 2: Authentication**
5. `feat(auth): implement signup endpoint with profile creation`
6. `feat(auth): implement signin endpoint with JWT token issuance`
7. `feat(auth): implement signout and token refresh endpoints`
8. `feat(auth): add FastAPI dependencies for current user validation`

**Phase 3: Profile Management**
9. `feat(users): implement GET /profile endpoint`
10. `feat(users): implement PUT /profile endpoint for updates`

**Phase 4: RAG Personalization**
11. `feat(rag): add personalization prompt templates based on user experience`
12. `feat(rag): integrate user profile into chatbot query endpoint`
13. `feat(rag): add fallback handling for unauthenticated users`

**Phase 5: Testing & Documentation**
14. `test(auth): add unit tests for signup and signin flows`
15. `test(users): add integration tests for profile management`
16. `test(rag): verify personalization with different user profiles`
17. `docs: update README with authentication setup instructions`
18. `docs: update .env.example with new environment variables`

### Commit Message Format
```
<type>(<scope>): <short description>

[Optional body explaining WHY, not WHAT]

[Optional footer with breaking changes or issue references]
```

**Types**: feat, fix, test, docs, refactor, chore
**Scopes**: auth, users, database, rag, config

### Rationale
- **Incremental commits**: Each commit is a working, testable increment
- **Clear scope**: Easy to review and revert if needed
- **Conventional commits**: Standard format for changelog generation
- **Direct to main**: No feature branch needed per user's constraint

---

## 10. Risk Assessment

### High-Risk Areas (DO NOT MODIFY)

1. **Qdrant Integration** (`backend/src/clients/qdrant_client.py`)
   - Vector database schema and indexing
   - Document embedding pipeline
   - **Mitigation**: Read-only interaction from personalization code

2. **Cohere Client** (`backend/src/clients/cohere_client.py`)
   - Embedding generation
   - LLM response generation
   - **Mitigation**: Only modify generation prompts, not API calls

3. **Existing RAG Service** (`backend/src/services/rag_service.py`)
   - Core retrieval logic
   - Chunk processing
   - **Mitigation**: Add personalization as optional parameter, preserve existing flow

4. **CORS Configuration** (`backend/src/main.py`)
   - Frontend origins
   - **Mitigation**: Read existing cors_origins from settings, do not override

### Medium-Risk Areas (MODIFY WITH CARE)

1. **FastAPI Main App** (`backend/src/main.py`)
   - Route registration
   - **Mitigation**: Add new routers, don't modify existing exception handlers

2. **Environment Configuration** (`backend/src/core/config.py`)
   - Settings class
   - **Mitigation**: Extend with new fields, don't change existing defaults

3. **Database Connection Handling**
   - New PostgreSQL connection alongside existing Qdrant
   - **Mitigation**: Separate connection pools, independent lifecycle

### Low-Risk Areas (SAFE TO MODIFY)

1. **New Auth Module** (`backend/src/auth/*`)
   - No dependencies on existing code
   - Self-contained functionality

2. **New Users Module** (`backend/src/users/*`)
   - Profile management
   - Independent from RAG logic

3. **Migrations Directory** (`backend/src/database/migrations/*`)
   - Database schema changes
   - Can be rolled back if issues arise

### Rollback Strategy

**Database Rollback**:
```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

**Code Rollback**:
```bash
# Revert specific commit
git revert <commit-hash>

# Reset to previous state (use with caution)
git reset --hard <commit-hash>
```

**Deployment Rollback**:
- Keep previous working deployment available
- Test all changes in development environment first
- Monitor error rates after deployment
- Be prepared to disable auth endpoints if critical issues arise

---

## 11. Optional Bonus Enhancements

### Optional Feature 1: Email Verification

**Implementation**:
- Add `email_verified` boolean to users table
- Generate verification token on signup
- Send email with verification link
- Create `/verify-email` endpoint

**Bonus Points**: Increases security, prevents spam accounts

### Optional Feature 2: Password Reset Flow

**Implementation**:
- Create `/forgot-password` endpoint
- Generate time-limited reset token
- Send reset link via email
- Create `/reset-password` endpoint

**Bonus Points**: Improves user experience, standard auth feature

### Optional Feature 3: Two-Factor Authentication (2FA)

**Implementation**:
- Add `totp_secret` to users table
- Use `pyotp` library for TOTP generation
- Create `/enable-2fa` and `/verify-2fa` endpoints
- Require 2FA code after password validation

**Bonus Points**: Significant security enhancement, competitive differentiator

### Optional Feature 4: Social OAuth Login

**Implementation**:
- Integrate Google/GitHub OAuth
- Use `authlib` library
- Create OAuth callback endpoints
- Link OAuth accounts to user profiles

**Bonus Points**: Improved UX, faster signup flow

**Note**: Social OAuth may conflict with "Better Auth" requirement if strictly interpreted as self-hosted only. Confirm with stakeholders.

### Optional Feature 5: Admin Dashboard for User Analytics

**Implementation**:
- Create `/admin/*` routes with role-based access
- Add `role` field to users table (user, admin)
- Build simple analytics: user count, query frequency, popular topics
- Track personalization effectiveness

**Bonus Points**: Demonstrates data-driven approach, useful for hackathon demo

### Recommendation
Prioritize **Email Verification** and **Password Reset** as they are standard authentication features. Implement **2FA** if time permits and seeking maximum bonus points.

---

## Summary

All technology decisions align with project requirements:
✅ Better Auth principles implemented with Python-native tools
✅ PostgreSQL (Neon) for auth/profile storage
✅ FastAPI extended with auth routes
✅ RAG personalization via prompt injection (no Qdrant/Cohere changes)
✅ Secure session management with JWT
✅ Comprehensive error handling and security measures
✅ Clear folder structure and git strategy
✅ Risk mitigation for existing RAG functionality

**Next Steps**:
1. Phase 1: Create data-model.md with detailed schema definitions
2. Phase 1: Generate API contracts (OpenAPI specs)
3. Phase 1: Write quickstart.md with step-by-step implementation guide
4. Phase 2: Begin implementation following commit sequence
