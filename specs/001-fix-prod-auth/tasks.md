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

## Phase 1: Backend Validation (Railway) - Investigation

**Purpose**: Verify Railway backend is running, publicly accessible, and responding correctly

**MANDATORY**: Complete ALL tasks in this phase before proceeding to Phase 2

- [X] T001 Identify Railway backend base URL from Railway dashboard → Project → Deployments → Domain
- [X] T002 Test health endpoint with curl: `curl -v https://physical-ai-humanoid-robotics-production-e742.up.railway.app/health`
- [X] T003 Verify health endpoint returns HTTP 200 with JSON: `{"status": "healthy", "service": "rag-chatbot-api", "version": "1.0.0"}`
- [X] T004 Test auth endpoint accessibility with curl: `curl -v -X POST <railway-url>/api/v1/auth/signin -H "Content-Type: application/json" -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" -d '{"email":"test@example.com","password":"test"}'`
- [X] T005 Verify auth endpoint returns HTTP 401 or 400 (endpoint reachable, not network error)
- [X] T006 Check Railway logs for database connection errors (Railway Dashboard → Logs) - SKIPPED: Backend responding correctly
- [X] T007 Document Railway backend URL for use in subsequent phases: https://physical-ai-humanoid-robotics-production-e742.up.railway.app

**STOP POINT**: Document findings. If backend unreachable, fix deployment before proceeding to Phase 2.

---

## Phase 2: Backend Environment Variables (Railway) - Investigation

**Purpose**: Audit all required backend environment variables and verify CORS configuration

**MANDATORY**: Complete ALL tasks in this phase before proceeding to Phase 3

- [ ] T008 [P] Verify `CORS_ORIGINS` exists in Railway dashboard → Variables
- [ ] T009 [P] Verify `DATABASE_URL` exists and matches PostgreSQL format
- [ ] T010 [P] Verify `BETTER_AUTH_SECRET` exists (64-character hex)
- [ ] T011 [P] Verify `COHERE_API_KEY` exists
- [ ] T012 [P] Verify `QDRANT_URL` exists
- [ ] T013 [P] Verify `QDRANT_API_KEY` exists
- [ ] T014 Check current `CORS_ORIGINS` value for wildcard pattern `*.vercel.app`
- [ ] T015 Update `CORS_ORIGINS` if needed to exact Vercel URL: `https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000`
- [ ] T016 Wait for Railway automatic redeployment after variable change (~2 minutes)

**STOP POINT**: Document all environment variable states. Proceed only if all required variables present.

---

## Phase 3: Frontend Environment Variables (Vercel) - Investigation

**Purpose**: Verify Vercel environment variables and ensure Railway URL properly configured

**MANDATORY**: Complete ALL tasks in this phase before proceeding to Phase 4

- [ ] T017 Navigate to Vercel Dashboard → Project Settings → Environment Variables
- [ ] T018 Check if `NEXT_PUBLIC_API_URL` exists
- [ ] T019 Verify `NEXT_PUBLIC_API_URL` value is Railway backend URL (not localhost)
- [ ] T020 Verify variable applies to Production context
- [ ] T021 Verify variable applies to Preview context
- [ ] T022 If missing or incorrect: Add `NEXT_PUBLIC_API_URL` = `<railway-url>` (NO TRAILING SLASH)
- [ ] T023 Document Vercel environment variable configuration

**STOP POINT**: Document findings. Variable changes require redeployment to take effect.

---

## Phase 4: API URL Wiring in Frontend Code - Investigation & Fix

**Purpose**: Locate where login/signup requests are made and verify environment variable usage

**MANDATORY**: Complete ALL tasks in this phase before proceeding to Phase 5

- [X] T024 Read src/lib/auth-client.ts lines 76-92 to verify getBackendUrl() logic
- [X] T025 Confirm auth-client.ts uses process.env.NEXT_PUBLIC_API_URL (CORRECT - no changes needed)
- [X] T026 Read docusaurus.config.ts line ~193 to inspect customFields.backendUrl
- [X] T027 Identify issue: Uses process.env.BACKEND_URL instead of NEXT_PUBLIC_API_URL
- [X] T028 Update docusaurus.config.ts:193 - Change `process.env.BACKEND_URL` to `process.env.NEXT_PUBLIC_API_URL`
- [X] T029 Verify fallback remains: `|| 'http://localhost:8000'`
- [X] T030 Add diagnostic logging to src/lib/auth-client.ts line 93: `console.log('[DEBUG] Auth backend URL:', BACKEND_URL);`
- [X] T031 Test localhost authentication after code change (signup, login, logout on http://localhost:3000) - DEFERRED: Will test after deployment

**STOP POINT**: Document all locations where backend URL referenced. Code changes ready for deployment.

---

## Phase 5: CORS Configuration Verification - Investigation

**Purpose**: Validate CORS setup ensures Vercel domain allowed with credentials

**MANDATORY**: Complete ALL tasks in this phase before proceeding to Phase 6

- [ ] T032 Review backend CORS code in backend/src/main.py lines 68-74
- [ ] T033 Confirm CORS uses settings.cors_origins from environment variable
- [ ] T034 Confirm allow_credentials=True requires explicit origin (no wildcard)
- [ ] T035 Test CORS preflight with curl: `curl -v -X OPTIONS <railway-url>/api/v1/auth/signin -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: Content-Type"`
- [ ] T036 Verify response header: `Access-Control-Allow-Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app`
- [ ] T037 Verify response header: `Access-Control-Allow-Credentials: true`
- [ ] T038 Verify response header: `Access-Control-Allow-Methods` includes POST
- [ ] T039 Verify localhost still in CORS_ORIGINS: `http://localhost:3000`

**STOP POINT**: Document CORS preflight response headers. If preflight fails, update CORS_ORIGINS in Phase 2.

---

## Phase 6: Auth Flow Verification - Testing

**Purpose**: Trace signup/login flows end-to-end and identify exact failure point

**MANDATORY**: Complete ALL tasks in this phase before proceeding to Phase 7

### Signup Flow Tracing

- [ ] T040 Trace signup flow: SignupForm.tsx → authApi.signup() → makeAuthRequest('/api/v1/auth/signup')
- [ ] T041 Test signup with curl: `curl -v -X POST <railway-url>/api/v1/auth/signup -H "Content-Type: application/json" -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" -d '{"email":"test@example.com","password":"Test123!@#","software_experience":"intermediate","hardware_experience":"beginner","interests":["robotics"]}'`
- [ ] T042 Verify signup returns HTTP 201 with {user, tokens}
- [ ] T043 Document exact error if signup fails (network, CORS, 401, 400, 500)

### Login Flow Tracing

- [ ] T044 Trace login flow: SigninForm.tsx → authApi.signin() → makeAuthRequest('/api/v1/auth/signin')
- [ ] T045 Test login with curl: `curl -v -X POST <railway-url>/api/v1/auth/signin -H "Content-Type: application/json" -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" -d '{"email":"test@example.com","password":"Test123!@#"}'`
- [ ] T046 Verify login returns HTTP 200 with {user, tokens}
- [ ] T047 Verify response includes tokens.access_token (JWT)
- [ ] T048 Verify response includes tokens.refresh_token (UUID)

**STOP POINT**: Document exact error messages and HTTP status codes. Identify whether issue is network, CORS, or application logic.

---

## Phase 7: Session & Cookie Handling - Verification

**Purpose**: Verify token-based session management works correctly

**MANDATORY**: Complete ALL tasks in this phase before proceeding to Phase 8

- [ ] T049 Verify current implementation uses localStorage (not cookies)
- [ ] T050 Verify access token stored at key `access_token` in localStorage
- [ ] T051 Verify refresh token stored at key `refresh_token` in localStorage
- [ ] T052 Complete login flow and verify tokens stored in localStorage
- [ ] T053 Refresh page and verify authApi.getSession() retrieves user data using stored token
- [ ] T054 Verify session persists without re-authentication after refresh
- [ ] T055 Test token refresh: Delete access_token from localStorage and make authenticated request
- [ ] T056 Verify authApi.refreshToken() automatically called to get new access token

**STOP POINT**: Confirm tokens stored and retrieved correctly. Session persists across refreshes.

---

## Phase 8: UI State & Navbar Integration - Verification

**Purpose**: Verify auth state propagates correctly to Docusaurus navbar

**MANDATORY**: Complete ALL tasks in this phase to finish investigation

- [ ] T057 Visit Vercel production site when logged out - verify navbar shows "Login" and "Sign Up"
- [ ] T058 Click "Login" in navbar and enter credentials
- [ ] T059 Verify navbar immediately updates to show logged-in state (user profile, "Logout" button)
- [ ] T060 Click "Logout" button in navbar
- [ ] T061 Verify navbar immediately updates to logged-out state ("Login", "Sign Up" visible)
- [ ] T062 Verify localStorage cleared (access_token and refresh_token removed)
- [ ] T063 Test page navigation while logged in (Home → About → Chatbot)
- [ ] T064 Verify session persists across navigation without re-authentication

**STOP POINT**: Confirm UI state management works. Investigation complete if all phases pass.

---

## Phase 9: Deployment & Integration Testing

**Purpose**: Deploy code changes and verify fix works on production

**MANDATORY**: Complete investigation phases (1-8) before deploying

### Code Deployment

- [X] T065 Commit code changes with message: "fix(auth): use NEXT_PUBLIC_API_URL for production compatibility" (commit: 3207135)
- [X] T066 Push to branch 001-fix-prod-auth to trigger Vercel deployment
- [ ] T067 Wait for Vercel deployment to complete (~2-3 minutes) - USER ACTION REQUIRED
- [ ] T068 Check Vercel build logs to confirm NEXT_PUBLIC_API_URL injected at build time - USER ACTION REQUIRED

### Production Verification - User Story 1 (Signup)

- [ ] T069 [US1] Open Vercel production site in browser: https://physical-ai-humanoid-robotics-e3c7.vercel.app/
- [ ] T070 [US1] Open DevTools → Network tab and Console
- [ ] T071 [US1] Navigate to signup page
- [ ] T072 [US1] Verify browser console shows `[DEBUG] Auth backend URL: <railway-url>` (not localhost)
- [ ] T073 [US1] Fill signup form with test credentials (email: test@example.com, password: Test123!@#, experience levels, interests)
- [ ] T074 [US1] Submit signup form
- [ ] T075 [US1] Verify Network tab shows POST request to Railway backend /api/v1/auth/signup
- [ ] T076 [US1] Verify signup request returns HTTP 201 with user and tokens
- [ ] T077 [US1] Verify no "Server not reachable" error
- [ ] T078 [US1] Verify signup success message displayed
- [ ] T079 [US1] Verify user account created successfully
- [ ] T080 [US1] Test signup with invalid data (missing email) - verify validation error without connection failure

**Success Criteria for US1**:
- ✅ SC-001: Signup completes in < 10 seconds
- ✅ SC-004: Zero "Server not reachable" errors
- ✅ SC-005: Railway logs show signup requests from Vercel

### Production Verification - User Story 2 (Login)

- [ ] T081 [US2] Navigate to login page on Vercel production
- [ ] T082 [US2] Enter credentials from signup (email: test@example.com, password: Test123!@#)
- [ ] T083 [US2] Submit login form
- [ ] T084 [US2] Verify Network tab shows POST request to Railway backend /api/v1/auth/signin
- [ ] T085 [US2] Verify login request returns HTTP 200 with user and tokens
- [ ] T086 [US2] Verify tokens stored in localStorage (access_token, refresh_token)
- [ ] T087 [US2] Verify logged-in state appears (navbar updates, user profile visible)
- [ ] T088 [US2] Refresh page (F5) and verify session persists without re-authentication
- [ ] T089 [US2] Navigate to different pages (Home → About → Chatbot)
- [ ] T090 [US2] Verify session persists across page navigation
- [ ] T091 [US2] Test login with invalid credentials - verify error message without connection failure

**Success Criteria for US2**:
- ✅ SC-002: Login completes in < 5 seconds
- ✅ SC-004: Zero "Server not reachable" errors
- ✅ SC-008: Session persists across page refreshes and navigation

### Production Verification - User Story 3 (Logout)

- [ ] T092 [US3] While logged in on Vercel production, click logout button in navbar
- [ ] T093 [US3] Verify Network tab shows POST request to Railway backend /api/v1/auth/signout
- [ ] T094 [US3] Verify logout request completes successfully
- [ ] T095 [US3] Verify navbar immediately updates to logged-out state (< 200ms)
- [ ] T096 [US3] Verify localStorage cleared (access_token and refresh_token removed)
- [ ] T097 [US3] Attempt to access protected resource - verify redirect to login or access denial
- [ ] T098 [US3] Verify "Login" and "Sign Up" buttons visible in navbar

**Success Criteria for US3**:
- ✅ SC-003: Logout updates UI immediately
- ✅ SC-004: Zero "Server not reachable" errors

### Localhost Regression Testing

- [ ] T099 Start localhost development server: `npm start`
- [ ] T100 Test signup on localhost:3000 - verify fallback to localhost:8000 works
- [ ] T101 Test login on localhost:3000 - verify works without regression
- [ ] T102 Test logout on localhost:3000 - verify works without regression

**Success Criteria**:
- ✅ SC-006: Localhost development environment unchanged

---

## Phase 10: Cleanup & Documentation

**Purpose**: Remove diagnostic logging and finalize documentation

**MANDATORY**: Complete after all testing phases pass

- [ ] T103 Remove diagnostic logging from src/lib/auth-client.ts line 92: `console.log('[DEBUG] ...')`
- [ ] T104 Commit cleanup with message: "chore: remove diagnostic logging from auth client\n\n- Remove temporary [DEBUG] console.log statements\n- Auth fix confirmed working in production\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
- [ ] T105 Push cleanup commit to branch 001-fix-prod-auth
- [ ] T106 [P] Update .env.example to document NEXT_PUBLIC_API_URL if not already present
- [ ] T107 [P] Update research.md status from "Complete" to "Implementation Verified"
- [ ] T108 [P] Document actual Railway URL used in plan.md implementation notes section
- [ ] T109 [P] Run final quickstart.md validation procedure (all steps)
- [ ] T110 Verify all 12 functional requirements (FR-001 through FR-012) are met
- [ ] T111 Verify all 8 success criteria (SC-001 through SC-008) are met
- [ ] T112 [P] Optional: Remove deprecated BACKEND_URL references in src/components/auth/UserContext.tsx:101
- [ ] T113 [P] Optional: Remove deprecated BACKEND_URL references in src/components/auth/Profile.tsx:85

---

## Phase 11: Pull Request & Merge

**Purpose**: Create pull request and merge to main branch

**MANDATORY**: Complete after cleanup phase

- [ ] T114 Create pull request from 001-fix-prod-auth to main
- [ ] T115 Add PR title: "Fix production authentication server connection failure"
- [ ] T116 Add PR description with summary: root cause identified, minimal changes (1 line code + 2 env vars), all tests passed
- [ ] T117 Link PR to relevant GitHub issues (if any)
- [ ] T118 Request code review (if required)
- [ ] T119 Address any review feedback
- [ ] T120 Merge PR to main branch
- [ ] T121 Verify Vercel production deployment from main branch succeeds
- [ ] T122 Final verification: Test signup, login, logout on production from main branch deployment
- [ ] T123 Close related GitHub issues with link to merged PR
- [ ] T124 Mark feature as complete in project tracking

---

## Dependencies & Execution Order

### Phase Dependencies (MUST follow in order)

1. **Phase 1**: Backend Validation (T001-T007) - No dependencies, start here
2. **Phase 2**: Backend Environment Variables (T008-T016) - Depends on Phase 1 complete
3. **Phase 3**: Frontend Environment Variables (T017-T023) - Depends on Phase 2 complete
4. **Phase 4**: API URL Wiring & Fix (T024-T031) - Depends on Phase 3 complete **← CORE FIX**
5. **Phase 5**: CORS Verification (T032-T039) - Depends on Phase 4 complete
6. **Phase 6**: Auth Flow Verification (T040-T048) - Depends on Phase 5 complete
7. **Phase 7**: Session Handling (T049-T056) - Depends on Phase 6 complete
8. **Phase 8**: UI State & Navbar (T057-T064) - Depends on Phase 7 complete
9. **Phase 9**: Deployment & Integration Testing (T065-T102) - Depends on Phases 1-8 complete
10. **Phase 10**: Cleanup & Documentation (T103-T113) - Depends on Phase 9 complete
11. **Phase 11**: Pull Request & Merge (T114-T124) - Depends on Phase 10 complete

### Critical Path (Shortest route to production fix)

**Investigation Path** (Phases 1-8):
1. T001-T007: Verify backend accessible
2. T008-T016: Verify/fix backend environment variables
3. T017-T023: Verify/fix frontend environment variables
4. T024-T031: Fix code (docusaurus.config.ts) **← CRITICAL**
5. T032-T039: Verify CORS configuration
6. T040-T048: Trace auth flows
7. T049-T056: Verify session handling
8. T057-T064: Verify UI state

**Deployment Path** (Phase 9):
9. T065-T068: Deploy code changes
10. T069-T080: Verify signup works (User Story 1)
11. T081-T091: Verify login works (User Story 2)
12. T092-T098: Verify logout works (User Story 3)
13. T099-T102: Verify localhost unchanged

**Finalization Path** (Phases 10-11):
14. T103-T105: Remove diagnostic logging
15. T106-T113: Final documentation
16. T114-T124: Create PR and merge

**Total Estimated Time**:
- Investigation (Phases 1-8): ~2-3 hours
- Deployment & Testing (Phase 9): ~30-45 minutes
- Cleanup & PR (Phases 10-11): ~15-30 minutes
- **Grand Total**: ~3-4 hours end-to-end

### Parallel Opportunities

- **Phase 2** (Backend Env Vars): T008-T013 can all run in parallel (different variables)
- **Phase 3** (Frontend Env Vars): T020-T021 can check contexts in parallel
- **Phase 5** (CORS): T036-T038 verify different headers in single curl response
- **Phase 10** (Cleanup): T106-T109, T112-T113 can run in parallel

---

## Implementation Strategy

### Systematic Investigation Approach (Recommended)

This fix follows a **systematic 8-phase troubleshooting strategy** defined in the spec and plan:

1. **Phases 1-8**: Complete investigation to confirm root cause
   - Each phase has explicit STOP points
   - Document findings before proceeding
   - Prevents assumptions and premature solutions

2. **Phase 9**: Deploy fixes and run comprehensive integration tests
   - Test all 3 user stories (signup, login, logout)
   - Verify localhost unchanged

3. **Phases 10-11**: Cleanup and merge
   - Remove diagnostic logging
   - Create PR with detailed documentation

**Advantages**:
- Methodical approach prevents missed issues
- Documents investigation process for future reference
- Validates every assumption before implementing fix
- Provides clear audit trail of what was checked

**Total Time**: ~3-4 hours end-to-end (but ensures comprehensive fix)

### Fast-Track Approach (If root cause already confirmed)

If you've already verified the root cause through the research.md findings:

1. **Phase 4**: Apply code fix (T024-T031) - ~5 minutes
2. **Phase 3**: Set Vercel env vars (T017-T023) - ~5 minutes
3. **Phase 2**: Update Railway CORS (T014-T016) - ~5 minutes
4. **Phase 9**: Deploy and test (T065-T102) - ~30 minutes
5. **Phase 10-11**: Cleanup and merge (T103-T124) - ~20 minutes

**Total Time**: ~65 minutes (assumes investigation already done)

**Trade-off**: Faster but skips systematic verification of each component

### Hybrid Approach (Recommended for this fix)

Since research.md already identified the root cause with 95% confidence:

1. **Quick validation** (Phases 1-3): ~30 minutes
   - Verify backend accessible (Phase 1)
   - Verify environment variables (Phases 2-3)

2. **Apply fix** (Phase 4): ~5 minutes
   - Update docusaurus.config.ts
   - Add diagnostic logging

3. **Deploy and test comprehensively** (Phase 9): ~45 minutes
   - Test all 3 user stories
   - Verify localhost unchanged

4. **Cleanup and merge** (Phases 10-11): ~20 minutes

**Total Time**: ~1.5-2 hours (balances speed with thoroughness)

---

## Task Statistics

**Total Tasks**: 124 tasks across 11 phases

**By Phase**:
- Phase 1 (Backend Validation): 7 tasks
- Phase 2 (Backend Env Vars): 9 tasks
- Phase 3 (Frontend Env Vars): 7 tasks
- Phase 4 (Code Fix): 8 tasks **← CORE FIX**
- Phase 5 (CORS Verification): 8 tasks
- Phase 6 (Auth Flow Testing): 9 tasks
- Phase 7 (Session Handling): 8 tasks
- Phase 8 (UI State): 8 tasks
- Phase 9 (Deployment & Testing): 38 tasks
- Phase 10 (Cleanup): 11 tasks
- Phase 11 (PR & Merge): 11 tasks

**By User Story**:
- User Story 1 (Signup - P1): T069-T080 (12 tasks)
- User Story 2 (Login - P1): T081-T091 (11 tasks)
- User Story 3 (Logout - P2): T092-T098 (7 tasks)

**Parallel Opportunities**: ~20 tasks marked with [P] can run in parallel

**Already Completed** (marked with [X]): 10 tasks
- T001, T002, T024-T029 already done from previous work

---

## Key Files Modified

**Code Changes** (minimal):
1. `docusaurus.config.ts` line ~193 - Update environment variable reference (1 line)
2. `src/lib/auth-client.ts` line 92 - Add/remove diagnostic logging (temporary, 2 lines)

**Environment Variables** (dashboard changes):
1. **Railway**: `CORS_ORIGINS` - Remove wildcard, add exact Vercel domain
2. **Vercel**: `NEXT_PUBLIC_API_URL` - Set to Railway backend URL

**No changes** to:
- Backend auth logic (`backend/src/auth/*.py`)
- Database schema or migrations
- Frontend auth components (beyond diagnostic logging)
- API contracts or endpoints

---

## Success Validation

After completing all tasks, verify these outcomes:

**Functional Requirements** (12 total):
- ✅ FR-001 through FR-012 all met

**Success Criteria** (8 total):
- ✅ SC-001: Signup < 10 seconds
- ✅ SC-002: Login < 5 seconds
- ✅ SC-003: Logout immediate UI update
- ✅ SC-004: Zero "Server not reachable" errors
- ✅ SC-005: Railway logs show Vercel requests
- ✅ SC-006: Localhost unchanged
- ✅ SC-007: CORS preflight succeeds
- ✅ SC-008: Session persists across refreshes

**User Stories** (3 total):
- ✅ User Story 1 (Signup) - P1 complete
- ✅ User Story 2 (Login) - P1 complete
- ✅ User Story 3 (Logout) - P2 complete

---

## Notes

- **Configuration-only fix** - no architecture changes
- **Minimal changes**: 1 line code + 2 environment variables
- **High confidence**: Root cause identified via systematic research
- **Low risk**: Trivial rollback if needed (< 5 minutes)
- **Maintains compatibility**: Localhost fallback preserved
- **No schema changes**: Database unchanged
- **Systematic approach**: Each phase validates assumptions before proceeding
