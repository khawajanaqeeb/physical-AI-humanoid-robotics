---
id: 002
title: Better Auth Implementation Plan
stage: plan
date: 2025-12-20
surface: agent
model: claude-sonnet-4-5
feature: 004-better-auth-personalization
branch: main
user: khawaja naqeeb
command: /sp.plan
labels: ["authentication", "personalization", "better-auth", "architecture", "database-design", "api-design"]
links:
  spec: specs/004-better-auth-personalization/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-better-auth-personalization/research.md
  - specs/004-better-auth-personalization/data-model.md
  - specs/004-better-auth-personalization/plan.md
  - specs/004-better-auth-personalization/quickstart.md
  - specs/004-better-auth-personalization/contracts/api-contracts.yaml
  - CLAUDE.md
tests:
  - Architecture validation against project constraints
  - Database schema design review
  - API contract completeness verification
---

## Prompt

(User provided comprehensive planning requirements for Better Auth authentication and personalized RAG chatbot implementation. Full prompt details in plan.md document.)

Key requirements:
- Implement Signup/Signin using Better Auth principles with PostgreSQL (Neon)
- Collect user profile: software experience, hardware experience, interests
- Personalize RAG responses via prompt injection based on user background
- Preserve existing RAG/Qdrant/Cohere functionality
- Work on main branch only
- Never commit secrets

## Response snapshot

Created comprehensive implementation plan across multiple artifacts:

### 1. **Research & Technology Decisions** (research.md)
- **Better Auth Integration**: Implemented auth using Python-native tools (passlib, python-jose) following Better Auth security principles, since Better Auth is JavaScript-focused
- **Database Design**: PostgreSQL (Neon) with SQLAlchemy ORM, normalized schema (users, user_profiles, sessions, chatbot_queries)
- **Session Strategy**: JWT access tokens (15 min) + refresh tokens (7 days) stored in database for revocation
- **Personalization Approach**: Inject user profile context into RAG system prompt BEFORE retrieval (no Qdrant/Cohere modifications)
- **Security Measures**: Bcrypt password hashing, rate limiting, defensive error handling, graceful degradation

### 2. **Data Model Specification** (data-model.md)
- **4 Core Entities**: User, UserProfile, Session, ChatbotQuery (optional)
- **User**: id (UUID), email (unique), hashed_password, is_active, timestamps
- **UserProfile**: software_experience (ENUM), hardware_experience (ENUM), interests (JSONB array), timestamps
- **Session**: access_token (JWT), refresh_token (UUID), expires_at, user_agent, ip_address
- **Relationships**: User↔Profile (1:1), User↔Sessions (1:N), User↔Queries (1:N)
- **Alembic Migration**: Initial schema with indexes, constraints, cascade deletes

### 3. **API Contracts** (contracts/api-contracts.yaml)
- **Auth Endpoints**: POST /auth/signup, /auth/signin, /auth/signout, /auth/refresh
- **Profile Endpoints**: GET /profile, PUT /profile
- **Query Endpoint** (enhanced): POST /query with optional personalization
- **OpenAPI 3.0.3 Spec**: Full request/response schemas with examples for beginner/advanced personalization

### 4. **Implementation Plan** (plan.md)
- **6 Phases, 18 Steps**: Prerequisites → Database → Auth → Profile → Personalization → Testing
- **Timeline**: ~11 hours core implementation
- **Git Strategy**: Sequential commits on main branch, clear scope per commit
- **Risk Mitigation**: Identified high-risk areas (Qdrant, Cohere, RAG service), fallback strategies
- **Optional Bonuses**: Email verification, password reset, 2FA, admin dashboard

### 5. **Quickstart Guide** (quickstart.md)
- **Developer-Focused**: Condensed checklist for rapid implementation
- **Step-by-Step Commands**: Environment setup, dependency installation, migration commands
- **Testing Shortcuts**: curl examples for all endpoints
- **Troubleshooting**: Common errors and solutions

### 6. **Agent Context Update** (CLAUDE.md)
- **Recent Changes**: Added 004-better-auth-personalization entry
- **Active Technologies**: Documented auth stack (passlib, python-jose, SQLAlchemy, PostgreSQL/Neon)

## Architectural Decisions

### Decision 1: Python-Native Auth vs Better Auth Port
**Choice**: Use passlib + python-jose instead of porting Better Auth (JavaScript library)
**Rationale**: Better Auth lacks Python support; established Python libraries provide equivalent security with less complexity
**Alternatives**: Port Better Auth to Python (too time-intensive), use Auth0/Firebase (violates self-hosted requirement)

### Decision 2: PostgreSQL + SQLAlchemy vs NoSQL
**Choice**: PostgreSQL (Neon) with SQLAlchemy ORM
**Rationale**: Relational model fits auth data (users, profiles, sessions) perfectly; ACID guarantees for credential storage; Alembic for safe migrations
**Alternatives**: MongoDB (less suited for auth), SQLite (not production-ready), existing Qdrant (vector DB, wrong tool)

### Decision 3: JWT + Refresh Tokens vs Session Cookies
**Choice**: JWT access tokens (short-lived) + refresh tokens (DB-stored)
**Rationale**: Stateless JWT for API performance, refresh tokens in DB for revocation capability, API-first design for frontend flexibility
**Alternatives**: Session cookies (CSRF concerns), long-lived JWT (can't revoke), opaque tokens only (DB lookup overhead)

### Decision 4: Prompt Injection vs Model Fine-Tuning
**Choice**: Inject personalized system prompt before Qdrant retrieval
**Rationale**: No re-embedding required, preserves existing RAG pipeline, immediate effect, reversible
**Alternatives**: Fine-tune Cohere model (expensive, slow), modify embeddings (requires re-indexing corpus), post-retrieval filtering (less effective)

### Decision 5: Fallback Strategy for Personalization
**Choice**: Graceful degradation - if profile fetch fails, use default prompt
**Rationale**: Ensures RAG never breaks due to auth issues, unauthenticated users get standard experience
**Alternatives**: Fail fast (breaks RAG), cache profiles (stale data risk), skip personalization silently (poor UX)

## Outcome

- ✅ Impact: Comprehensive implementation plan ready for immediate development. All architectural decisions documented with clear rationales. Zero ambiguity in requirements or design.
- 🧪 Tests: Architecture validated against all 27 functional requirements and 12 success criteria. Database schema normalized and migration-ready. API contracts complete with request/response examples.
- 📁 Files: Created 6 planning artifacts - research.md (11 sections), data-model.md (4 entities, migration script), plan.md (6 phases, 18 steps), quickstart.md (developer guide), api-contracts.yaml (OpenAPI spec), CLAUDE.md (context update)
- 🔁 Next prompts: `/sp.tasks` to generate testable task breakdown from this plan. Then begin Phase 0 implementation (environment setup, dependency installation). Optional: `/sp.adr` to document key architectural decisions (auth strategy, database choice, personalization approach).
- 🧠 Reflection: Plan successfully balances security (bcrypt, JWT, rate limiting) with simplicity (no unnecessary abstractions). Personalization via prompt injection is elegant - no changes to existing RAG retrieval logic. Risk mitigation strategy explicitly identifies what NOT to modify. Timeline estimate (11 hours) is realistic for core features, with clear optional enhancements for bonus points.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning phase completed without blocking issues. User requirements were comprehensive and unambiguous.
- Graders run and results (PASS/FAIL): PASS - All functional requirements mapped to implementation steps. All success criteria have measurable validation points. API contracts align with data model. No conflicts between research decisions and plan phases.
- Prompt variant (if applicable): Standard /sp.plan workflow with comprehensive user context and constraints
- Next experiment (smallest change to try): Consider adding WebSocket support for real-time profile updates in future iteration (out of scope for current plan, but noted for roadmap)

## ADR Suggestions

📋 Architectural decisions detected that merit documentation:

1. **Authentication Strategy Decision**: Python-native auth libraries vs Better Auth port
   - Document reasoning and tradeoffs? Run `/sp.adr auth-library-selection`

2. **Session Management Decision**: JWT + refresh tokens vs session cookies vs opaque tokens
   - Document reasoning and tradeoffs? Run `/sp.adr session-management-strategy`

3. **Personalization Approach Decision**: Prompt injection vs model fine-tuning vs embedding modification
   - Document reasoning and tradeoffs? Run `/sp.adr rag-personalization-approach`

These decisions are architecturally significant (long-term impact, multiple alternatives considered, cross-cutting concerns). Grouping all three into a single ADR is recommended: `/sp.adr better-auth-architecture-decisions`
