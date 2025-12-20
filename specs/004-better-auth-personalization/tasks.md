# Tasks: Better Auth User Authentication and Personalized RAG Chatbot

**Input**: Design documents from `/specs/004-better-auth-personalization/`
**Prerequisites**: plan.md (implementation guide), spec.md (user stories), data-model.md (entities), contracts/api-contracts.yaml (endpoints), research.md (technology decisions)

**Tests**: Tests are NOT explicitly requested in the specification. Tasks focus on implementation with manual validation per plan.md Phase 5.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web app with backend focus:
- **Backend**: `backend/src/`, `backend/tests/`
- **Database**: `backend/src/database/migrations/`
- **Config**: `backend/.env`, `backend/requirements.txt`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment setup

- [ ] T001 Create PostgreSQL database on Neon (https://neon.tech) and copy DATABASE_URL
- [ ] T002 Generate BETTER_AUTH_SECRET using `openssl rand -hex 32` and store securely
- [ ] T003 Add new environment variables to `backend/.env`: DATABASE_URL, BETTER_AUTH_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES=15, REFRESH_TOKEN_EXPIRE_DAYS=7
- [ ] T004 Update `backend/.env.example` with placeholder values for new environment variables
- [ ] T005 [P] Add authentication dependencies to `backend/requirements.txt`: passlib[bcrypt]==1.7.4, python-jose[cryptography]==3.3.0, python-multipart==0.0.6
- [ ] T006 [P] Add database dependencies to `backend/requirements.txt`: SQLAlchemy==2.0.23, alembic==1.13.1, psycopg2-binary==2.9.9, email-validator==2.1.0
- [ ] T007 Install all dependencies with `pip install -r backend/requirements.txt`
- [ ] T008 [P] Create directory structure: `backend/src/auth/`, `backend/src/users/`, `backend/src/database/`, `backend/src/database/migrations/`

**Checkpoint**: Environment ready - database created, dependencies installed, directory structure in place

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database and authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Foundation

- [ ] T009 Create `backend/src/database/base.py` with SQLAlchemy declarative base
- [ ] T010 [P] Create `backend/src/database/session.py` with database session factory using settings.database_url
- [ ] T011 [P] Create `backend/src/database/__init__.py` exporting Base, get_db, engine
- [ ] T012 Update `backend/src/core/config.py` Settings class to add database_url, better_auth_secret, access_token_expire_minutes, refresh_token_expire_days fields

### SQLAlchemy Models (Data Layer)

- [ ] T013 [P] Create `backend/src/users/models.py` with User model (id, email, hashed_password, is_active, created_at, last_login_at)
- [ ] T014 [P] Add UserProfile model to `backend/src/users/models.py` (software_experience ENUM, hardware_experience ENUM, interests JSONB, timestamps)
- [ ] T015 [P] Add Session model to `backend/src/users/models.py` (access_token, refresh_token, expires_at, user_agent, ip_address)
- [ ] T016 [P] Add ChatbotQuery model to `backend/src/users/models.py` (user_id nullable FK, query_text, response_text, personalization_context JSONB, created_at)
- [ ] T017 Create `backend/src/users/__init__.py` exporting User, UserProfile, Session, ChatbotQuery models

### Database Migrations

- [ ] T018 Initialize Alembic in backend directory: `alembic init src/database/migrations`
- [ ] T019 Update `backend/src/database/migrations/alembic.ini` to use environment variable for sqlalchemy.url
- [ ] T020 Update `backend/src/database/migrations/env.py` to import models and set target_metadata to Base.metadata
- [ ] T021 Create initial migration: `alembic revision --autogenerate -m "Initial auth schema"`
- [ ] T022 Review generated migration in `versions/` to verify users, user_profiles, sessions, chatbot_queries tables with correct ENUMs, indexes, and foreign keys
- [ ] T023 Run migration: `alembic upgrade head`
- [ ] T024 Verify tables created in Neon database using psql or database client

### Authentication Security Utilities

- [ ] T025 [P] Create `backend/src/auth/security.py` with hash_password() function using passlib bcrypt (cost factor 12)
- [ ] T026 [P] Add verify_password() function to `backend/src/auth/security.py`
- [ ] T027 [P] Add create_access_token() function to `backend/src/auth/security.py` using python-jose with HS256, including exp, iat, type="access" in payload
- [ ] T028 [P] Add create_refresh_token() function to `backend/src/auth/security.py` generating UUID4
- [ ] T029 [P] Add verify_access_token() function to `backend/src/auth/security.py` to decode and validate JWT
- [ ] T030 Create `backend/src/auth/__init__.py` exporting all security functions

### Pydantic Schemas (Request/Response Models)

- [ ] T031 [P] Create `backend/src/auth/schemas.py` with SignupRequest schema (email, password with validators, software_experience, hardware_experience, interests optional)
- [ ] T032 [P] Add SigninRequest schema to `backend/src/auth/schemas.py` (email, password)
- [ ] T033 [P] Add AuthResponse schema to `backend/src/auth/schemas.py` (access_token, refresh_token, token_type, expires_in, user object)
- [ ] T034 [P] Add RefreshTokenRequest schema to `backend/src/auth/schemas.py` (refresh_token)
- [ ] T035 [P] Create `backend/src/users/schemas.py` with ProfileDetails schema (software_experience, hardware_experience, interests, timestamps)
- [ ] T036 [P] Add UserWithProfile schema to `backend/src/users/schemas.py` (id, email, profile)
- [ ] T037 [P] Add UserProfileResponse schema to `backend/src/users/schemas.py` (extends UserWithProfile with created_at, last_login_at)
- [ ] T038 [P] Add UpdateProfileRequest schema to `backend/src/users/schemas.py` (all fields optional)

**Checkpoint**: Foundation ready - database schema created, models defined, auth utilities implemented, schemas created. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - New User Account Creation (Priority: P1) 🎯 MVP

**Goal**: Allow visitors to create accounts with email/password and provide background information (software experience, hardware experience, interests). Automatically sign in after successful registration.

**Independent Test**: Navigate to signup endpoint, submit valid registration data, verify account created in database and tokens returned.

### User Services (Business Logic for US1)

- [ ] T039 [US1] Create `backend/src/users/services.py` with create_user() function (validates email uniqueness, hashes password, creates User + UserProfile atomically in transaction)
- [ ] T040 [US1] Add create_user_session() function to `backend/src/users/services.py` (generates access + refresh tokens, creates Session record with user_agent and IP)
- [ ] T041 [P] [US1] Add get_user_with_profile() function to `backend/src/users/services.py` (fetches User with eagerly loaded UserProfile, returns UserWithProfile schema)

### Authentication Routes for US1

- [ ] T042 [US1] Create `backend/src/auth/routes.py` with FastAPI APIRouter
- [ ] T043 [US1] Implement POST /auth/signup endpoint in `backend/src/auth/routes.py` (calls create_user, create_user_session, returns AuthResponse with 201 status)
- [ ] T044 [US1] Add rate limiting decorator @limiter.limit("5/minute") to signup endpoint
- [ ] T045 [US1] Add error handling for signup endpoint (400 for duplicate email, 400 for validation errors with field-specific messages)
- [ ] T046 [US1] Register auth router in `backend/src/main.py` with prefix "/api/v1/auth" and tags ["Authentication"]

### Validation and Error Handling for US1

- [ ] T047 [P] [US1] Add password strength validator to SignupRequest schema (min 8 chars, uppercase, lowercase, digit, special char)
- [ ] T048 [P] [US1] Add email format validation using email-validator library in SignupRequest schema
- [ ] T049 [US1] Update `backend/src/core/exceptions.py` to add AuthenticationError and ValidationError custom exceptions if not already present

**Checkpoint**: At this point, User Story 1 (signup) should be fully functional. Test independently: POST to /api/v1/auth/signup with valid data, verify user + profile created, tokens returned.

---

## Phase 4: User Story 2 - Returning User Authentication (Priority: P1)

**Goal**: Allow registered users to sign in with email/password and receive access/refresh tokens for authenticated sessions.

**Independent Test**: Attempt to sign in with valid credentials from User Story 1, verify tokens returned and session created.

### User Services (Business Logic for US2)

- [ ] T050 [US2] Add authenticate_user() function to `backend/src/users/services.py` (validates email exists, verifies password, checks is_active, updates last_login_at)
- [ ] T051 [US2] Add delete_user_session() function to `backend/src/users/services.py` (deletes Session record by access_token, handles signout)
- [ ] T052 [US2] Add refresh_user_session() function to `backend/src/users/services.py` (validates refresh_token from DB, generates new access + refresh tokens, deletes old session, creates new session)

### Authentication Routes for US2

- [ ] T053 [US2] Implement POST /auth/signin endpoint in `backend/src/auth/routes.py` (calls authenticate_user, create_user_session, returns AuthResponse with 200 status)
- [ ] T054 [US2] Add rate limiting decorator @limiter.limit("5/minute") to signin endpoint
- [ ] T055 [US2] Add error handling for signin endpoint (401 for invalid credentials with generic message "Invalid email or password")
- [ ] T056 [US2] Implement POST /auth/signout endpoint in `backend/src/auth/routes.py` (requires authentication, calls delete_user_session, returns 200 success message)
- [ ] T057 [US2] Implement POST /auth/refresh endpoint in `backend/src/auth/routes.py` (validates RefreshTokenRequest, calls refresh_user_session, returns new AuthResponse)
- [ ] T058 [US2] Add error handling for refresh endpoint (401 for invalid/expired refresh token)

### Authentication Dependencies for US2

- [ ] T059 [US2] Create `backend/src/auth/dependencies.py` with get_current_user() dependency (extracts Bearer token from Authorization header, validates JWT, fetches User from DB, checks is_active)
- [ ] T060 [P] [US2] Add get_current_user_optional() dependency to `backend/src/auth/dependencies.py` (returns None if no token, returns User if valid, used for optional auth)
- [ ] T061 [US2] Add HTTPException handling in get_current_user() for 401 Unauthorized if token invalid/expired or user not found

**Checkpoint**: At this point, User Story 2 (signin/signout/refresh) should be fully functional. Test independently: POST to /api/v1/auth/signin with User Story 1 credentials, verify tokens. Test signout and refresh flows.

---

## Phase 5: User Story 3 - Personalized Chatbot Interactions (Priority: P2)

**Goal**: Tailor chatbot responses based on authenticated user's experience level and interests. Beginner users get simple explanations, advanced users get technical depth.

**Independent Test**: Sign in as users with different profiles (Beginner vs Advanced), ask identical questions, verify response adaptation based on user profile.

### Personalization Engine

- [ ] T062 [P] [US3] Create `backend/src/services/personalization.py` with BEGINNER_TEMPLATE constant (simple language, analogies, no jargon)
- [ ] T063 [P] [US3] Add INTERMEDIATE_TEMPLATE constant to `backend/src/services/personalization.py` (clear technical language, balanced theory/practice)
- [ ] T064 [P] [US3] Add ADVANCED_TEMPLATE constant to `backend/src/services/personalization.py` (technical terminology, formulas, research references)
- [ ] T065 [US3] Implement build_personalized_prompt() function in `backend/src/services/personalization.py` (selects template based on software_experience/hardware_experience, injects interests list)

### RAG Service Integration

- [ ] T066 [US3] Modify query_textbook() method in `backend/src/services/rag_service.py` to add optional system_prompt parameter (defaults to None for backward compatibility)
- [ ] T067 [US3] Update Cohere generation call in `backend/src/services/rag_service.py` to use system_prompt parameter if provided, otherwise use default preamble
- [ ] T068 [US3] Verify Qdrant retrieval logic in `backend/src/services/rag_service.py` is unchanged (no modifications to vector search, embeddings, or chunk retrieval)

### Query Endpoint Enhancement

- [ ] T069 [US3] Modify POST /query endpoint in `backend/src/api/routes/query.py` to add get_current_user_optional dependency
- [ ] T070 [US3] Add profile fetching logic in query endpoint (if current_user exists, fetch UserProfile from DB)
- [ ] T071 [US3] Add personalization logic in query endpoint (if profile exists, call build_personalized_prompt(), pass to rag_service.query_textbook())
- [ ] T072 [US3] Add try-except wrapper around personalization logic with logging.warning() on failure, graceful fallback to non-personalized prompt
- [ ] T073 [US3] Add personalization_applied boolean field to QueryResponse schema in `backend/src/api/schemas/response.py`
- [ ] T074 [US3] Set personalization_applied=True in response if personalized_prompt was used, False otherwise

### Fallback and Error Handling

- [ ] T075 [P] [US3] Add logging statements in query endpoint for personalization success/failure cases
- [ ] T076 [P] [US3] Verify unauthenticated query requests still work with default (non-personalized) prompt

**Checkpoint**: At this point, User Story 3 (personalized chatbot) should be fully functional. Test independently: Query as beginner → simple response, query as advanced → technical response, query unauthenticated → standard response.

---

## Phase 6: User Story 4 - Profile Management (Priority: P3)

**Goal**: Allow authenticated users to view and update their profile information (experience levels, interests) so future chatbot interactions reflect current knowledge level.

**Independent Test**: Sign in, navigate to profile endpoint, update experience level from Beginner to Advanced, verify subsequent chatbot responses reflect updated profile.

### Profile Management Services

- [ ] T077 [US4] Add update_user_profile() function to `backend/src/users/services.py` (updates UserProfile fields, sets updated_at timestamp, returns updated profile)

### Profile Management Routes

- [ ] T078 [US4] Create `backend/src/users/routes.py` with FastAPI APIRouter
- [ ] T079 [US4] Implement GET /profile endpoint in `backend/src/users/routes.py` (requires authentication via get_current_user, calls get_user_with_profile, returns UserProfileResponse)
- [ ] T080 [US4] Implement PUT /profile endpoint in `backend/src/users/routes.py` (requires authentication, validates UpdateProfileRequest, calls update_user_profile, returns updated UserProfileResponse)
- [ ] T081 [US4] Add error handling for profile endpoints (400 for validation errors with enum values in message, 401 for unauthenticated)
- [ ] T082 [US4] Register users router in `backend/src/main.py` with prefix "/api/v1" and tags ["Profile"]

**Checkpoint**: All user stories should now be independently functional. Test: Update profile → verify next query uses updated personalization context.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

### Documentation

- [ ] T083 [P] Update `backend/README.md` with authentication setup instructions (database creation, environment variables, migration commands)
- [ ] T084 [P] Add API endpoint examples to `backend/README.md` for signup, signin, profile management, personalized query
- [ ] T085 [P] Create `backend/docs/AUTHENTICATION.md` documenting Better Auth integration approach, JWT token flow, personalization mechanism

### Validation and Testing

- [ ] T086 Run all manual tests from `plan.md` Phase 5.1 (signup, signin, profile CRUD, personalized vs standard queries)
- [ ] T087 Run edge case tests from `plan.md` Phase 5.2 (duplicate email, wrong password, invalid enum, profile fetch failure)
- [ ] T088 Run end-to-end integration test from `plan.md` Phase 6.3 (signup → query as beginner → update to advanced → query again → signout → query unauthenticated)

### Security Hardening

- [ ] T089 [P] Verify all passwords are hashed with bcrypt cost factor 12 in `backend/src/auth/security.py`
- [ ] T090 [P] Verify JWT secret is read from environment variable (settings.better_auth_secret) and never hardcoded
- [ ] T091 [P] Verify no passwords or tokens are logged in `backend/src/` code
- [ ] T092 [P] Review rate limiting on all auth endpoints (/signup, /signin at 5/min)

### Final Validation

- [ ] T093 Verify `.env` file is in `.gitignore` and not committed
- [ ] T094 Verify `.env.example` has placeholder values for all new environment variables
- [ ] T095 Verify `backend/requirements.txt` has all dependencies with pinned versions
- [ ] T096 Verify database migrations are reversible (`alembic downgrade -1` works)
- [ ] T097 Verify existing RAG functionality works for unauthenticated users (no breaking changes to Qdrant, Cohere, retrieval logic)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (Signup): Can start after Foundational - No dependencies on other stories
  - User Story 2 (Signin): Can start after Foundational - No dependencies on US1 (but logical to complete US1 first for testing)
  - User Story 3 (Personalization): Depends on US1+US2 for testing (need authenticated users with profiles)
  - User Story 4 (Profile Management): Can start after Foundational - Uses same user services as US1
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

```
Foundational Phase (T009-T061)
    ├──> User Story 1: Signup (T039-T049) ──┐
    ├──> User Story 2: Signin (T050-T061) ──┼──> User Story 3: Personalization (T062-T076)
    └──> User Story 4: Profile Mgmt (T077-T082) ─┘
```

**Key Dependencies**:
- US3 (Personalization) requires US1 (Signup) + US2 (Signin) for testing, but could technically be implemented in parallel
- US4 (Profile Management) is independent of other user stories but uses services from US1

### Within Each User Story

**User Story 1 (Signup)**:
1. Services first (T039-T041) - Business logic layer
2. Routes next (T042-T046) - API layer depends on services
3. Validation last (T047-T049) - Error handling depends on routes

**User Story 2 (Signin)**:
1. Services first (T050-T052) - Business logic layer
2. Routes next (T053-T058) - API layer depends on services
3. Dependencies last (T059-T061) - Reusable auth middleware

**User Story 3 (Personalization)**:
1. Personalization engine (T062-T065) - Can be done in parallel with RAG integration
2. RAG service integration (T066-T068) - Can be done in parallel with engine
3. Query endpoint enhancement (T069-T074) - Depends on engine + RAG integration
4. Fallback handling (T075-T076) - Depends on endpoint enhancement

**User Story 4 (Profile Management)**:
1. Services (T077) - Business logic layer
2. Routes (T078-T082) - API layer depends on services

### Parallel Opportunities

**Phase 1: Setup**
- T005 and T006 (dependency additions) can run in parallel
- T008 (directory creation) can run in parallel with T001-T007

**Phase 2: Foundational**
- Database foundation (T010-T011) can run in parallel after T009
- Models (T013-T016) can all run in parallel after T012
- Security utilities (T025-T029) can all run in parallel after T024
- Schemas (T031-T034) and (T035-T038) can all run in parallel after T030

**User Story 1**
- T041 (get_user_with_profile) can run in parallel with T042-T043 (route setup)
- T047-T048 (validation) can run in parallel

**User Story 2**
- T060 (optional dependency) can run in parallel with T053-T058 (route implementations)

**User Story 3**
- T062-T064 (templates) can all run in parallel
- T066-T068 (RAG service) can run in parallel with T062-T065 (engine)
- T075-T076 (logging/verification) can run in parallel

**User Story 4**
- No significant parallel opportunities (sequential flow)

**Phase 7: Polish**
- Documentation tasks (T083-T085) can all run in parallel
- Security verification tasks (T089-T092) can all run in parallel

---

## Parallel Example: User Story 1 (Signup)

```bash
# Launch all User Story 1 models in parallel (if multiple developers):
Task T013: "Create User model in backend/src/users/models.py"
Task T014: "Add UserProfile model to backend/src/users/models.py"
Task T015: "Add Session model to backend/src/users/models.py"
Task T016: "Add ChatbotQuery model to backend/src/users/models.py"

# Then launch services:
Task T039: "create_user() function in backend/src/users/services.py"
Task T040: "create_user_session() function in backend/src/users/services.py"
Task T041: "get_user_with_profile() function in backend/src/users/services.py"

# Then route implementation sequentially:
Task T042-T046 (must be sequential due to same file edits)
```

---

## Parallel Example: Foundational Phase

```bash
# After database setup (T009-T012), launch all models together:
Parallel Launch:
- Task T013: User model
- Task T014: UserProfile model
- Task T015: Session model
- Task T016: ChatbotQuery model

# After models complete, launch all security utilities together:
Parallel Launch:
- Task T025: hash_password()
- Task T026: verify_password()
- Task T027: create_access_token()
- Task T028: create_refresh_token()
- Task T029: verify_access_token()

# After security utilities, launch all schemas together:
Parallel Launch:
- Task T031-T034: Auth schemas
- Task T035-T038: User schemas
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Goal**: Fastest path to demonstrable value - working signup with profile creation

1. Complete Phase 1: Setup (T001-T008) - ~1 hour
2. Complete Phase 2: Foundational (T009-T061) - ~4 hours
   - **CRITICAL CHECKPOINT**: Foundation must be solid before proceeding
3. Complete Phase 3: User Story 1 (T039-T049) - ~1 hour
4. **STOP and VALIDATE**: Test signup independently
   - Can create account with profile?
   - Tokens returned?
   - Data in database?
5. Deploy/demo if ready

**MVP Scope**: ~6 hours for basic working signup with authentication foundation

### Incremental Delivery (Recommended)

**Goal**: Deliver value incrementally, each user story independently testable

1. **Foundation Sprint** (~5 hours):
   - Phase 1: Setup (T001-T008)
   - Phase 2: Foundational (T009-T061)
   - **VALIDATE**: Database schema created, migrations work, can run tests

2. **Auth Sprint** (~2 hours):
   - Phase 3: User Story 1 - Signup (T039-T049)
   - Phase 4: User Story 2 - Signin/Signout/Refresh (T050-T061)
   - **VALIDATE**: Can signup, signin, signout, refresh tokens
   - **DEMO**: Working authentication system

3. **Personalization Sprint** (~1.5 hours):
   - Phase 5: User Story 3 - Personalized Chatbot (T062-T076)
   - **VALIDATE**: Beginner vs Advanced responses differ
   - **DEMO**: Tailored learning experience

4. **Profile Management Sprint** (~1 hour):
   - Phase 6: User Story 4 - Profile Management (T077-T082)
   - **VALIDATE**: Can update profile, subsequent queries reflect changes
   - **DEMO**: User-controlled personalization

5. **Polish Sprint** (~1.5 hours):
   - Phase 7: Documentation, security, final validation (T083-T097)
   - **VALIDATE**: Production-ready, documented, secure
   - **DEMO**: Complete feature ready for deployment

**Total Incremental**: ~11 hours with clear checkpoints

### Parallel Team Strategy (3+ Developers)

**Goal**: Maximum velocity with parallel work streams

**Sprint 1: Foundation Together** (All developers, ~5 hours)
- Everyone works on Phase 1 + Phase 2 together
- Pair programming on critical database/auth infrastructure
- **CHECKPOINT**: Foundation solid, tested, all developers aligned

**Sprint 2: Parallel User Stories** (After foundation complete)
- **Developer A**: User Story 1 - Signup (T039-T049)
- **Developer B**: User Story 2 - Signin (T050-T061)
- **Developer C**: User Story 4 - Profile Management (T077-T082)
- **CHECKPOINT**: Independent stories complete, integrate and test

**Sprint 3: Integration**
- **Developer A**: User Story 3 - Personalization (T062-T076)
- **Developers B+C**: Phase 7 - Polish (T083-T097)
- **CHECKPOINT**: All stories integrated, documented, production-ready

**Parallel Team Total**: ~7-8 hours with 3 developers

---

## Notes

- **[P] tasks**: Different files, no dependencies, safe to parallelize
- **[Story] label**: Maps task to specific user story for traceability and independent testing
- **Each user story** should be independently completable and testable - avoid cross-story dependencies
- **Manual testing strategy**: Per plan.md Phase 5, use curl/Postman to validate each endpoint after implementation
- **Commit strategy**: Commit after each task or logical group (per plan.md git strategy)
- **Stop at checkpoints**: Validate each user story independently before proceeding to next
- **Graceful degradation**: US3 personalization failures must not break standard RAG queries (T072 critical)
- **Security first**: Never commit secrets (T093), always use environment variables (T003)
- **Migration safety**: All Alembic migrations must be reversible (T096)

---

## Task Count Summary

- **Phase 1 (Setup)**: 8 tasks (T001-T008)
- **Phase 2 (Foundational)**: 53 tasks (T009-T061)
- **Phase 3 (User Story 1)**: 11 tasks (T039-T049) - Signup
- **Phase 4 (User Story 2)**: 13 tasks (T050-T061, T053-T061) - Signin/Signout/Refresh
- **Phase 5 (User Story 3)**: 15 tasks (T062-T076) - Personalized Chatbot
- **Phase 6 (User Story 4)**: 6 tasks (T077-T082) - Profile Management
- **Phase 7 (Polish)**: 15 tasks (T083-T097) - Documentation, Security, Validation

**Total Tasks**: 97
**MVP Scope** (US1 only): 61 tasks (Setup + Foundational + US1)
**Core Features** (US1+US2+US3): 89 tasks
**Complete Feature**: 97 tasks

**Estimated Time**: ~11 hours (per plan.md timeline)
