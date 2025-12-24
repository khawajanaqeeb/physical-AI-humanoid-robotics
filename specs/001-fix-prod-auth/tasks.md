---
description: "Task list for fixing production authentication server connection failure"
---

# Tasks: Fix Production Authentication Server Connection Failure

**Input**: Design documents from `/specs/001-fix-prod-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested - manual testing only (quickstart.md provides test procedures)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: Repository root (`docusaurus.config.ts`, `src/components/`)
- **Backend**: Repository root (`backend/src/`)
- This is a web app with Vercel frontend + Railway backend

---

## Phase 1: Setup (Investigation & Verification)

**Purpose**: Verify current state and prepare for fix

- [X] T001 Verify Railway backend is accessible by testing endpoint with curl: `curl https://physical-ai-humanoid-robotics-production-e742.up.railway.app/api/v1/health`
- [ ] T002 [P] Review current environment variable configuration in Vercel dashboard (Settings → Environment Variables)
- [ ] T003 [P] Review current CORS configuration in Railway dashboard (Variables → CORS_ORIGINS)
- [X] T004 [P] Read docusaurus.config.ts:193 to confirm current environment variable usage
- [ ] T005 Test localhost authentication to confirm baseline working state (signup, login, logout on http://localhost:3000)

**Checkpoint**: Current state verified - ready to apply fix

---

## Phase 2: User Story 1 - New User Registration (Priority: P1) 🎯 MVP

**Goal**: Enable new users to successfully register on Vercel production frontend through Railway backend

**Independent Test**: Navigate to signup page on Vercel production, fill registration form, successfully create account

### Implementation for User Story 1

- [X] T006 [US1] Update docusaurus.config.ts:193 - Change `process.env.BACKEND_URL` to `process.env.NEXT_PUBLIC_API_URL`
- [X] T007 [US1] Verify fallback remains as `|| 'http://localhost:8000'` in docusaurus.config.ts:193
- [ ] T008 [US1] Test localhost signup after code change to ensure no regression
- [ ] T009 [US1] Set Vercel environment variable `NEXT_PUBLIC_API_URL` in Production context (value: `https://physical-ai-humanoid-robotics-production-e742.up.railway.app`)
- [ ] T010 [US1] Set Vercel environment variable `NEXT_PUBLIC_API_URL` in Preview context (value: `https://physical-ai-humanoid-robotics-production-e742.up.railway.app`)
- [ ] T011 [US1] Commit code changes with message: "fix(auth): use NEXT_PUBLIC_API_URL for production compatibility"
- [X] T012 [US1] Push to branch 001-fix-prod-auth to trigger Vercel deployment
- [ ] T013 [US1] Wait for Vercel deployment to complete (~2-3 minutes)
- [ ] T014 [US1] Update Railway CORS_ORIGINS variable to include exact Vercel URL: `https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000`
- [ ] T015 [US1] Wait for Railway service restart (~30 seconds)
- [ ] T016 [US1] Verify CORS configuration with curl OPTIONS preflight request (see contracts/environment-vars.md for command)
- [ ] T017 [US1] Open Vercel production site in browser with DevTools → Network tab
- [ ] T018 [US1] Test signup on Vercel production with test credentials (email: test@example.com, password: testpass123)
- [ ] T019 [US1] Verify Network tab shows request to Railway backend (not localhost)
- [ ] T020 [US1] Verify signup request returns 200/201 status (not CORS error)
- [ ] T021 [US1] Verify signup success message and user account created
- [ ] T022 [US1] Verify browser console shows correct NEXT_PUBLIC_API_URL (Railway URL, not localhost)
- [ ] T023 [US1] Test signup with invalid data (missing email) to verify validation errors work without connection failures

**Success Criteria**:
- ✅ SC-001: Users can successfully complete signup on Vercel production in under 10 seconds
- ✅ SC-004: Zero "Unable to connect to authentication server" errors during signup
- ✅ SC-005: Railway logs show incoming signup requests from Vercel
- ✅ SC-006: Localhost development environment still works for signup
- ✅ SC-007: CORS preflight requests complete successfully

**Checkpoint**: User Story 1 (signup) complete and independently testable

---

## Phase 3: User Story 2 - Existing User Login (Priority: P1)

**Goal**: Enable existing users to log into their accounts on Vercel production frontend through Railway backend

**Independent Test**: Use pre-existing credentials on Vercel production login page, successfully authenticate, see logged-in state

**Dependencies**: User Story 1 must be complete (uses same environment variable fix)

### Implementation for User Story 2

- [ ] T024 [US2] Navigate to login page on Vercel production with DevTools → Network tab open
- [ ] T025 [US2] Test login with credentials from User Story 1 signup
- [ ] T026 [US2] Verify Network tab shows request to Railway backend for /api/v1/auth/signin
- [ ] T027 [US2] Verify login request returns 200 status with access_token and refresh_token
- [ ] T028 [US2] Verify logged-in state appears (navbar updates, user profile visible)
- [ ] T029 [US2] Refresh the page and verify session persists (no re-authentication required)
- [ ] T030 [US2] Navigate to different pages and verify session persists across navigation
- [ ] T031 [US2] Test login with invalid credentials (wrong password) to verify error messages without connection failures
- [ ] T032 [US2] Verify Railway logs show incoming login requests from Vercel
- [ ] T033 [US2] Test localhost login to ensure no regression in development environment

**Success Criteria**:
- ✅ SC-002: Users can successfully login on Vercel production in under 5 seconds
- ✅ SC-004: Zero "Unable to connect to authentication server" errors during login
- ✅ SC-008: Session persistence works across page refreshes and navigation
- ✅ SC-006: Localhost development environment still works for login

**Checkpoint**: User Story 2 (login) complete and independently testable

---

## Phase 4: User Story 3 - User Logout (Priority: P2)

**Goal**: Enable authenticated users to log out on Vercel production frontend with logout action communicated to Railway backend

**Independent Test**: Log in on Vercel production, click logout button in navbar, confirm logged-out state

**Dependencies**: User Story 2 must be complete (requires logged-in user)

### Implementation for User Story 3

- [ ] T034 [US3] Log in on Vercel production using credentials from User Story 1
- [ ] T035 [US3] Open DevTools → Network tab
- [ ] T036 [US3] Click logout button in navbar
- [ ] T037 [US3] Verify Network tab shows request to Railway backend for /api/v1/auth/signout
- [ ] T038 [US3] Verify logout request completes successfully
- [ ] T039 [US3] Verify UI updates immediately to logged-out state (navbar changes, user profile hidden)
- [ ] T040 [US3] Attempt to access protected resources and verify redirect to login or access denial
- [ ] T041 [US3] Verify Railway logs show incoming logout requests from Vercel
- [ ] T042 [US3] Test localhost logout to ensure no regression in development environment

**Success Criteria**:
- ✅ SC-003: Authenticated users can successfully logout on Vercel production with immediate UI state update
- ✅ SC-004: Zero "Unable to connect to authentication server" errors during logout
- ✅ SC-006: Localhost development environment still works for logout

**Checkpoint**: User Story 3 (logout) complete - all authentication flows working

---

## Phase 5: Edge Cases & Error Handling

**Purpose**: Verify system handles edge cases gracefully

- [ ] T043 [P] Test auth when Railway backend is temporarily unavailable (stop Railway service temporarily)
- [ ] T044 [P] Verify user-friendly error message displays (not "Unable to connect to authentication server" raw error)
- [ ] T045 [P] Test network timeout scenario by throttling network in DevTools
- [ ] T046 [P] Test with expired/invalid session token by manually corrupting localStorage token
- [ ] T047 [P] Test switching between localhost and production environments (clear cache between tests)
- [ ] T048 Verify all edge cases documented in spec.md are handled gracefully

**Checkpoint**: Edge cases validated - system robust

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup and documentation

- [ ] T049 [P] Run complete quickstart.md validation procedure (all steps in quickstart.md)
- [ ] T050 [P] Check browser console for any lingering environment variable warnings
- [ ] T051 [P] Verify Railway logs show clean auth request flow (no errors)
- [ ] T052 [P] Update .env.example to document NEXT_PUBLIC_API_URL if not already present
- [ ] T053 Optional: Remove deprecated BACKEND_URL references in src/components/auth/UserContext.tsx:101
- [ ] T054 Optional: Remove deprecated BACKEND_URL references in src/components/auth/Profile.tsx:85
- [ ] T055 Create pull request with title "Fix production authentication server connection failure"
- [ ] T056 Add PR description with summary of changes and testing performed
- [ ] T057 Verify all success criteria from spec.md are met (SC-001 through SC-008)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Setup verification - THIS IS THE CORE FIX
- **User Story 2 (Phase 3)**: Depends on User Story 1 completion (uses same fix)
- **User Story 3 (Phase 4)**: Depends on User Story 2 completion (requires logged-in user)
- **Edge Cases (Phase 5)**: Depends on all user stories completion
- **Polish (Phase 6)**: Depends on all previous phases

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup - No dependencies on other stories - **CORE FIX**
- **User Story 2 (P1)**: Can start after User Story 1 - Requires working signup for test credentials
- **User Story 3 (P2)**: Can start after User Story 2 - Requires logged-in user to test logout

### Within Each User Story

**User Story 1** (signup):
1. Code change first (T006-T007)
2. Test localhost (T008)
3. Set Vercel env vars (T009-T010)
4. Deploy (T011-T013)
5. Set Railway CORS (T014-T015)
6. Verify and test (T016-T023)

**User Story 2** (login):
1. All tasks can run sequentially (T024-T033)
2. Uses fix from User Story 1

**User Story 3** (logout):
1. All tasks can run sequentially (T034-T042)
2. Uses fix from User Story 1

### Parallel Opportunities

- **Phase 1**: T002, T003, T004 can run in parallel
- **User Story 1**: T009 and T010 can be set simultaneously in Vercel dashboard
- **Edge Cases**: All tasks (T043-T048) can run in parallel after Phase 4 complete
- **Polish**: T049, T050, T051, T052 can run in parallel

---

## Parallel Example: User Story 1 Setup

```bash
# Review configurations in parallel:
Task: "Review current environment variable configuration in Vercel dashboard"
Task: "Review current CORS configuration in Railway dashboard"
Task: "Read docusaurus.config.ts:193 to confirm current environment variable usage"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

This is a **configuration-only fix**, so the MVP is effectively the complete fix:

1. Complete Phase 1: Setup (verify current state)
2. Complete Phase 2: User Story 1 (THE FIX - signup working)
3. **STOP and VALIDATE**: Test signup independently on production
4. If signup works, proceed to validate login and logout

### Incremental Validation

1. Complete Setup → Current state verified
2. Apply User Story 1 fix → Test signup independently → **CRITICAL VALIDATION POINT**
3. Test User Story 2 (login) → Verify login works → Independent validation
4. Test User Story 3 (logout) → Verify logout works → Independent validation
5. Test Edge Cases → Verify robust error handling
6. Polish and document → Ready for PR

### Critical Path

**Shortest path to production fix**:
1. T006: Update docusaurus.config.ts (1 line change)
2. T009: Set Vercel NEXT_PUBLIC_API_URL
3. T011-T013: Deploy to Vercel
4. T014: Update Railway CORS_ORIGINS
5. T018-T021: Test signup on production

Total time: ~15 minutes (as documented in quickstart.md)

---

## Notes

- This is a **configuration-only fix** - no architecture changes, no new features
- **1 line of code** + **2 environment variables** = complete fix
- All user stories use the same fix (environment variable correction)
- User Story dependencies are for **testing validation** (not implementation)
- Focus on User Story 1 first - it contains the actual fix
- User Stories 2 and 3 are **validation** that the fix works for all auth flows
- Localhost compatibility maintained via fallback: `|| 'http://localhost:8000'`
- No database migrations, no schema changes, no auth logic changes
- Rollback is trivial: revert 1 line + delete env var
- Estimated total time: 30-45 minutes including testing
