# Tasks: Docusaurus Better Auth Integration

**Input**: Design documents from `/specs/006-docusaurus-better-auth/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/auth-api.yaml

**Tests**: Tests are included as optional tasks - implement if test coverage is desired.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Docusaurus Frontend**: `src/`, `plugins/` at repository root
- **FastAPI Backend**: `backend/src/`
- Tasks follow hybrid architecture: Better Auth client-side + FastAPI backend

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install better-auth package: `npm install better-auth`
- [X] T002 [P] Install TypeScript support: `npm install --save-dev @types/react typescript`
- [X] T003 [P] Create environment variable file `.env` with BACKEND_URL (http://localhost:8000 for dev)
- [X] T004 [P] Verify backend authentication endpoints exist at backend/src/auth/routes.py (signup, signin, signout, refresh)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Create auth client configuration in src/lib/auth-client.ts
- [X] T006 Create AuthContext provider in src/components/auth/AuthContext.tsx
- [X] T007 Create Root wrapper to provide AuthContext in src/theme/Root.tsx
- [X] T008 [P] Create auth component styles in src/components/auth/auth.css
- [X] T009 [P] Configure Docusaurus to use custom Root component (verify docusaurus.config.ts allows theme swizzling)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 2 - New User Registration with Background Profile (Priority: P1) 🎯 MVP

**Goal**: Users can create accounts with email, password, software experience, and hardware experience

**Independent Test**: Navigate to /auth/signup → Fill form → Submit → Verify redirect to chatbot

### Implementation for User Story 2

- [X] T010 [P] [US2] Create SignupForm component in src/components/auth/SignupForm.tsx
- [X] T011 [P] [US2] Create signup page in src/pages/auth/signup.tsx
- [X] T012 [US2] Implement form validation logic in SignupForm (email format, password strength, field required checks)
- [X] T013 [US2] Implement signup submission handler calling POST /auth/signup via AuthContext
- [X] T014 [US2] Add error handling for signup failures (409 email exists, 422 validation errors, 500 server errors)
- [X] T015 [US2] Add loading state and disable submit button during signup request
- [X] T016 [US2] Implement redirect to chatbot after successful signup (navigate to / and open chatbot modal)
- [X] T017 [P] [US2] Add signup form styling to auth.css

**Checkpoint**: At this point, User Story 2 (signup) should be fully functional and testable independently

---

## Phase 4: User Story 3 - Existing User Sign In (Priority: P1)

**Goal**: Users with existing accounts can sign in with email and password

**Independent Test**: Navigate to /auth/signin → Enter credentials → Submit → Verify redirect to chatbot

### Implementation for User Story 3

- [X] T018 [P] [US3] Create SigninForm component in src/components/auth/SigninForm.tsx
- [X] T019 [P] [US3] Create signin page in src/pages/auth/signin.tsx
- [X] T020 [US3] Implement signin submission handler calling POST /auth/signin via AuthContext
- [X] T021 [US3] Add error handling for signin failures (401 invalid credentials, 500 server errors)
- [X] T022 [US3] Add loading state and disable submit button during signin request
- [X] T023 [US3] Implement redirect to chatbot after successful signin (navigate to / and open chatbot modal)
- [X] T024 [US3] Handle redirect parameter from query string (e.g., /auth/signin?redirect=chatbot)
- [X] T025 [P] [US3] Add signin form styling to auth.css

**Checkpoint**: At this point, User Stories 2 AND 3 (signup + signin) should both work independently

---

## Phase 5: User Story 6 - Session Management and Logout (Priority: P2)

**Goal**: Authenticated users can see their email in navbar and log out

**Independent Test**: Sign in → Verify email shown in navbar → Click logout → Verify redirected to home and unauthenticated

### Implementation for User Story 6

- [X] T026 [P] [US6] Create UserButton component in src/components/auth/UserButton.tsx (displays email + logout button)
- [X] T027 [P] [US6] Create custom navbar item wrapper in src/theme/NavbarItem/ComponentTypes.tsx
- [X] T028 [US6] Create CustomLoginLogoutNavbarItem component in src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx
- [X] T029 [US6] Implement logout handler in CustomLoginLogoutNavbarItem calling signout() from AuthContext
- [X] T030 [US6] Add logout button to navbar config in docusaurus.config.ts (items: [{ type: 'custom-loginLogout' }])
- [X] T031 [US6] Implement session clearing in AuthContext.signout (call POST /auth/signout, clear local state)
- [X] T032 [US6] Verify session persists across page refreshes (AuthContext restores from useSession hook)
- [X] T033 [P] [US6] Add user button dropdown styling to auth.css

**Checkpoint**: At this point, User Stories 2, 3, AND 6 (signup + signin + logout) should all work independently

---

## Phase 6: User Story 1 - Unauthenticated Chatbot Access Gating (Priority: P1)

**Goal**: Unauthenticated users clicking chatbot icon are redirected to signin, then back to chatbot after login

**Independent Test**: Sign out → Click chatbot icon → Verify redirected to /auth/signin?redirect=chatbot → Sign in → Verify chatbot modal opens

### Implementation for User Story 1

- [X] T034 [US1] Modify ChatWidget component in plugins/rag-chatbot/components/ChatWidget.jsx to add authentication check
- [X] T035 [US1] Add useAuth hook import to ChatWidget (import from src/components/auth/AuthContext)
- [X] T036 [US1] Implement handleChatClick authentication gate (if !isAuthenticated, save redirect, navigate to /auth/signin?redirect=chatbot)
- [X] T037 [US1] Implement redirect restoration in signin page (read sessionStorage.auth_redirect, navigate after signin)
- [X] T038 [US1] Add backend authentication dependency to /api/query endpoint in backend/src/api/routes/query.py (Depends(get_current_user))
- [X] T039 [US1] Verify chatbot API client sends Authorization: Bearer {access_token} header in plugins/rag-chatbot/api/client.js
- [X] T040 [US1] Add error handling for 401 Unauthorized responses in chatbot client (trigger refresh token flow)
- [X] T041 [P] [US1] Test full redirect flow: unauthenticated chatbot click → signin → redirect back to chatbot

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 6 (all P1/P2 stories) should be fully functional

---

## Phase 7: User Story 4 - Personalized RAG Chatbot Responses (Priority: P2)

**Goal**: Chatbot responses are tailored based on user's software and hardware experience levels

**Independent Test**: Sign in as beginner user → Ask chatbot "Explain neural networks" → Verify simple explanation; Sign in as advanced user → Ask same question → Verify technical explanation

### Implementation for User Story 4

- [X] T042 [P] [US4] Create personalization service in backend/src/services/personalization_service.py
- [X] T043 [US4] Implement get_personalization_prompt function (input: UserProfile, output: str prompt context)
- [X] T044 [US4] Add personalization logic for software_experience levels (BEGINNER, INTERMEDIATE, ADVANCED)
- [X] T045 [US4] Add personalization logic for hardware_experience levels (NONE, BASIC, ADVANCED)
- [X] T046 [US4] Modify /api/query endpoint in backend/src/api/routes/query.py to inject personalization context
- [X] T047 [US4] Fetch user profile from current_user.profile (relationship already defined in User model)
- [X] T048 [US4] Call get_personalization_prompt and prepend to system prompt before RAG query
- [X] T049 [P] [US4] Add optional logging of personalization context to chatbot_queries table (personalization_context JSONB column)
- [X] T050 [P] [US4] Test personalization with different user profiles (create test users with BEGINNER, INTERMEDIATE, ADVANCED levels)

**Checkpoint**: At this point, personalized chatbot responses should work for all authenticated users

---

## Phase 8: User Story 5 - Personalized Docusaurus Book Content (Priority: P3)

**Goal**: Docusaurus book pages show personalized content recommendations based on user profile (optional enhancement)

**Independent Test**: Sign in as beginner → Navigate to book page → Verify beginner-friendly hints shown; Sign in as advanced → Verify advanced topics highlighted

### Implementation for User Story 5

- [ ] T051 [P] [US5] Create PersonalizedContent component in src/components/personalization/PersonalizedContent.tsx
- [ ] T052 [US5] Implement content filtering logic based on user.profile.software_experience
- [ ] T053 [US5] Create sample personalized hints for beginner, intermediate, advanced users
- [ ] T054 [P] [US5] Add PersonalizedContent component to example doc page (docs/intro.md or similar)
- [ ] T055 [US5] Add conditional rendering: show component only if user is authenticated
- [ ] T056 [P] [US5] Add personalization component styling to src/css/custom.css
- [ ] T057 [P] [US5] Test personalization on multiple doc pages with different user profiles

**Checkpoint**: All user stories (US1-US6) should now be independently functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T058 [P] Add form field validation messages to all forms (signup, signin)
- [ ] T059 [P] Implement responsive styling for auth forms (320px to 2560px viewports)
- [ ] T060 [P] Add loading spinners to all async operations (signup, signin, chatbot query)
- [ ] T061 Add CORS error handling with user-friendly messages ("Cannot connect to backend")
- [ ] T062 Implement token refresh interceptor in src/lib/api-client.ts (catch 401, call /auth/refresh, retry)
- [ ] T063 [P] Add security headers validation (verify HTTP-only cookies in browser DevTools)
- [ ] T064 [P] Test entire flow on localhost:3000 (dev environment)
- [ ] T065 [P] Update .env.example with required environment variables (BACKEND_URL)
- [ ] T066 [P] Verify production CORS configuration in backend/.env (CORS_ORIGINS includes Vercel URL)
- [ ] T067 Run quickstart.md validation checklist (manual testing section)
- [ ] T068 [P] Add error boundary component for auth-related crashes in src/components/auth/ErrorBoundary.tsx

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Integrates with US2/US3 but independently testable
- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Requires US2/US3 for redirect flow
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Requires US1 for chatbot access, but personalization logic is independent
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Optional enhancement, fully independent

### Within Each User Story

- Models before services (backend)
- Services before endpoints (backend)
- Components before pages (frontend)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes:
  - US2 signup form + US3 signin form can be built in parallel (different files)
  - US6 navbar button can be built in parallel with US2/US3 forms
  - US4 backend personalization service can be built in parallel with frontend auth UI
  - US5 personalized content component can be built in parallel with chatbot work
- Within each story, tasks marked [P] can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all foundational tasks together after T005 completes:
Task T006: "Create AuthContext provider in src/components/auth/AuthContext.tsx"
Task T008: "Create auth component styles in src/components/auth/auth.css"
Task T009: "Configure Docusaurus to use custom Root component"
```

## Parallel Example: User Story 2 + 3 + 6

```bash
# After Foundational completes, launch all P1/P2 forms in parallel:
Task T010: "Create SignupForm component in src/components/auth/SignupForm.tsx" [US2]
Task T011: "Create signup page in src/pages/auth/signup.tsx" [US2]
Task T018: "Create SigninForm component in src/components/auth/SigninForm.tsx" [US3]
Task T019: "Create signin page in src/pages/auth/signin.tsx" [US3]
Task T026: "Create UserButton component in src/components/auth/UserButton.tsx" [US6]
Task T027: "Create custom navbar item wrapper" [US6]
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 2 (Signup)
4. Complete Phase 4: User Story 3 (Signin)
5. Complete Phase 6: User Story 1 (Chatbot Gating)
6. **STOP and VALIDATE**: Test all P1 stories independently
7. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US2 (Signup) → Test independently → Deploy/Demo
3. Add US3 (Signin) → Test independently → Deploy/Demo
4. Add US1 (Chatbot Gating) → Test independently → Deploy/Demo (MVP!)
5. Add US6 (Logout) → Test independently → Deploy/Demo
6. Add US4 (Personalization) → Test independently → Deploy/Demo
7. Add US5 (Book Content) → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 2 (Signup)
   - Developer B: User Story 3 (Signin)
   - Developer C: User Story 6 (Logout navbar)
3. Then:
   - Developer A: User Story 1 (Chatbot gating)
   - Developer B: User Story 4 (Personalization backend)
   - Developer C: User Story 5 (Book content)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label (e.g., [US2]) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend authentication (signup, signin, signout, refresh, /auth/me) already exists - NO backend changes except personalization service (US4)
- Frontend uses Better Auth client-side only (better-auth/react hooks)
- Tokens: JWT access tokens (15min) + refresh tokens (7 days, HTTP-only cookies)
- CORS: Configured for Vercel frontend + Railway backend
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
