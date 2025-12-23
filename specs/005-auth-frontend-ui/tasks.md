# Tasks: Authentication Frontend UI

**Input**: Design documents from `/specs/005-auth-frontend-ui/`
**Prerequisites**: plan.md (✅), spec.md (✅)

**Tests**: Not requested in specification - manual testing only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for React components, `frontend/src/components/auth/` for auth isolation
- **Backend**: Existing FastAPI endpoints (not modified in this feature)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [x] T001 [P] Create `.env.example` in `frontend/` with `BACKEND_URL` template and comment explaining Docusaurus env var usage
- [x] T002 [P] Verify `.env` exists in `frontend/` and is in `.gitignore` (should already exist per plan)
- [x] T003 [P] Create `frontend/src/components/auth/auth.module.css` for component-specific styles (mobile-first, responsive 320px-2560px)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Update `frontend/src/components/auth/UserContext.tsx` to add session timeout logic with 1-hour expiration and activity tracking (mouse/keyboard events reset timer)
- [x] T005 Update `frontend/src/components/auth/UserContext.tsx` to add periodic backend token validation (check every 5 minutes if token still valid)
- [x] T006 Update `frontend/src/components/auth/UserContext.tsx` to detect localStorage availability on mount and set fallback flag if unavailable
- [x] T007 [P] Verify `frontend/src/theme/Layout.tsx` wraps app with `UserProvider` for global context access
- [x] T008 [P] Update predefined interests constant to array of 10 options in `frontend/src/components/auth/SignupForm.tsx` (Robotics, AI, ML, Hardware Design, Software Dev, IoT, Computer Vision, NLP, Autonomous Systems, Embedded Systems)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - New User Registration with Profile (Priority: P1) 🎯 MVP

**Goal**: Enable new visitors to create accounts with email, password, and background profile (software/hardware experience, interests)

**Independent Test**: Navigate to `/auth-demo`, fill signup form with valid data (email, matching 8-char passwords, select experience levels, check 2-3 interests), submit, verify success message and account creation

### Implementation for User Story 1

- [x] T009 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - replace interests text input (line 199-209) with multi-select checkbox group using predefined interests array from T008
- [x] T010 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - remove password complexity validation (lines 51-58) keeping only 8-character minimum per FR-003a
- [x] T011 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - add "Try Again" button that appears on network errors (FR-021a), hidden by default, shown when catch block triggers
- [x] T012 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - ensure email validation uses RFC 5322 compliant regex (FR-002)
- [x] T013 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - add validation for required experience level selections (FR-004)
- [x] T014 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - ensure interests are sent as array of selected checkbox values (not comma-separated string)
- [x] T015 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - add disabled state to submit button while loading (FR-023)
- [x] T016 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - add loading spinner/indicator during API request (FR-024)
- [x] T017 [US1] Add responsive styles to `frontend/src/components/auth/auth.module.css` for signup form (mobile 320px, tablet 768px, desktop 1024px+)
- [x] T018 [US1] Update `frontend/src/components/auth/SignupForm.tsx` - verify backend URL is read from environment variable (FR-016) and log warning if not set

**Checkpoint**: User Story 1 complete - Users can create accounts with profile. Test independently before proceeding.

---

## Phase 4: User Story 2 - Existing User Sign In (Priority: P1)

**Goal**: Enable registered users to sign in with email/password and restore their session

**Independent Test**: Create test account via signup, sign out, navigate to signin form, enter correct credentials, verify authentication and session restoration

### Implementation for User Story 2

- [x] T019 [US2] Review `frontend/src/components/auth/SigninForm.tsx` for existing implementation completeness
- [x] T020 [US2] Update `frontend/src/components/auth/SigninForm.tsx` - add "Try Again" button for network errors (FR-021a) matching signup pattern
- [x] T021 [US2] Update `frontend/src/components/auth/SigninForm.tsx` - verify error messages don't reveal which field is wrong (use generic "Invalid credentials" for FR-010, SC-007)
- [x] T022 [US2] Update `frontend/src/components/auth/SigninForm.tsx` - add disabled state to submit button while loading (FR-023)
- [x] T023 [US2] Update `frontend/src/components/auth/SigninForm.tsx` - add loading spinner/indicator during API request (FR-024)
- [x] T024 [US2] Update `frontend/src/components/auth/SigninForm.tsx` - ensure session data (tokens, profile) is stored via UserContext login() method
- [x] T025 [US2] Add responsive styles to `frontend/src/components/auth/auth.module.css` for signin form matching signup responsive breakpoints
- [x] T026 [US2] Update `frontend/src/components/auth/UserContext.tsx` - verify session restoration on page refresh loads from localStorage (FR-013)
- [x] T027 [US2] Update `frontend/src/components/auth/UserContext.tsx` - add session expiry check on mount (if stored timestamp + 1 hour < now, clear session)
- [x] T028 [US2] Verify `frontend/src/theme/NavbarItem/LoginLogoutNavbarItem.js` shows logout button only when user is authenticated (FR-014a)
- [x] T029 [US2] Update `frontend/src/theme/NavbarItem/LoginLogoutNavbarItem.js` - ensure logout button calls UserContext logout() and is visible in navigation bar

**Checkpoint**: User Story 2 complete - Users can sign in and session persists. Test independently (signup → signin → refresh → logout).

---

## Phase 5: User Story 3 - Session-Aware Chatbot Interaction (Priority: P2)

**Goal**: Pass user profile (experience levels, interests) to chatbot API requests for personalized responses

**Independent Test**: Sign in with specific profile (e.g., Beginner software, Advanced hardware, Robotics interest), open DevTools Network tab, interact with chatbot, verify API request includes session token and profile data

### Implementation for User Story 3

- [x] T030 [P] [US3] Locate existing chatbot API integration code (likely in `frontend/src/` or chatbot plugin)
- [x] T031 [US3] Update chatbot API request function to call `useUser()` hook and retrieve current user profile
- [x] T032 [US3] Update chatbot API request to include `Authorization: Bearer {token}` header when user is authenticated (FR-015)
- [x] T033 [US3] Update chatbot API request to include user profile data in request payload (software_experience, hardware_experience, interests) when user is authenticated
- [x] T034 [US3] Add fallback behavior for chatbot when user is not authenticated (send request without auth header or profile data)
- [x] T035 [US3] Verify chatbot continues to function for unauthenticated users (generic responses without personalization per acceptance scenario 3)

**Checkpoint**: User Story 3 complete - Chatbot receives user profile for personalization. Test with different profile combinations.

---

## Phase 6: User Story 4 - User Profile Access and Context (Priority: P3)

**Goal**: Make user profile globally accessible via `useUser()` hook for any component

**Independent Test**: Sign in, open browser DevTools React component tree, verify UserContext contains profile data, refresh page, verify profile persists

### Implementation for User Story 4

- [x] T036 [US4] Review `frontend/src/components/auth/UserContext.tsx` exports to ensure `useUser` hook is exported
- [x] T037 [US4] Review `frontend/src/components/auth/index.tsx` to ensure `UserProvider` and `useUser` are exported from barrel file
- [x] T038 [US4] Verify `useUser()` hook returns null/undefined when no user is signed in (per acceptance scenario 2)
- [x] T039 [US4] Verify `useUser()` hook returns user profile object with all fields when user is signed in (email, software_experience, hardware_experience, interests)
- [x] T040 [US4] Verify logout() method clears all user data from context and localStorage (per acceptance scenario 4)
- [x] T041 [US4] Create simple test component (e.g., `frontend/src/components/auth/Profile.tsx` if not exists) that displays current user profile using `useUser()` hook for manual verification

**Checkpoint**: User Story 4 complete - Profile context works globally. Test hook from different components.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T042 [P] Review all auth components for console.log cleanup and remove debug statements
- [x] T043 [P] Add ARIA labels and keyboard navigation support to multi-select interests checkboxes for accessibility
- [x] T044 [P] Verify responsive design works on actual mobile device (320px width) and large desktop (2560px width) per SC-008
- [x] T045 [P] Scan all auth component files for hardcoded URLs or secrets, ensure all use environment variables (FR-017, SC-010)
- [x] T046 [P] Add CSS transitions/animations to loading states and error messages in `frontend/src/components/auth/auth.module.css`
- [x] T047 [P] Verify form inputs are sanitized (React's built-in escaping should handle this, confirm no `dangerouslySetInnerHTML` usage per FR-020)
- [x] T048 Test complete signup flow: Navigate to `/auth-demo` → fill all fields → submit → verify success → check localStorage contains profile
- [x] T049 Test complete signin flow: Use account from T048 → sign out → sign in again → verify session restored → refresh page → verify persistence
- [x] T050 Test session timeout: Sign in → wait 61 minutes (or modify timeout to 1 minute for testing) → attempt action → verify prompted to re-authenticate
- [x] T051 Test network error handling: Sign in → disable network in DevTools → attempt signup/signin → verify "Try Again" button appears → re-enable network → click "Try Again" → verify success
- [x] T052 Test logout: Sign in → click logout button in nav bar → verify session cleared → verify nav bar no longer shows logout button
- [x] T053 Test multi-device compatibility: Sign in on Chrome → sign in same account on Firefox → verify both sessions work independently
- [x] T054 [P] Update `frontend/.env.example` with complete documentation of all environment variables needed (BACKEND_URL with example)
- [x] T055 Document any Docusaurus theme swizzling changes in `frontend/README.md` or create `frontend/ARCHITECTURE.md` for future maintainers
- [x] T056 Verify no modifications were made to existing Docusaurus content pages (FR-027) or chatbot integration beyond session passing (FR-028)
- [x] T057 Run Docusaurus build (`npm run build` in frontend/) to ensure no build errors introduced
- [x] T058 Deploy to staging/preview environment and test with production backend URL

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 3 (P2): Can start after Foundational - Technically can proceed in parallel but logically builds on US1/US2
  - User Story 4 (P3): Can start after Foundational - Infrastructure story, supports all others
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Signup/Registration - Independent, no dependencies on other stories
- **User Story 2 (P1)**: Signin/Authentication - Independent, but naturally follows US1 (needs accounts to exist)
- **User Story 3 (P2)**: Chatbot Integration - Depends on US2 (needs authentication working) but can be tested with manually created sessions
- **User Story 4 (P3)**: Profile Context - Infrastructure that US1-US3 already use, mainly validation tasks

### Within Each User Story

- **US1**: Signup form updates are all in SignupForm.tsx (T009-T016 can be done sequentially), styles in parallel (T017-T018)
- **US2**: Signin form updates (T019-T025) → UserContext session logic (T026-T027) → Navbar logout (T028-T029)
- **US3**: Locate chatbot code (T030) → Add auth header (T031-T033) → Fallback (T034-T035)
- **US4**: Review/verify tasks only, mostly validation

### Parallel Opportunities

- **Phase 1 Setup**: All 3 tasks (T001-T003) can run in parallel
- **Phase 2 Foundational**: T007 and T008 can run in parallel with T004-T006
- **User Stories**: If team capacity allows, US1 and US2 can be developed in parallel (different components)
- **US3**: T030 must complete first, but T031-T035 modifications can be batched
- **Phase 7 Polish**: T042-T047 (code quality) can run in parallel, T054-T055 (docs) in parallel, tests (T048-T053) sequential

---

## Parallel Example: User Story 1

```bash
# These SignupForm.tsx updates can be bundled in a single editing session:
Task T009: "Replace interests input with checkboxes"
Task T010: "Remove password complexity validation"
Task T011: "Add Try Again button for network errors"
Task T012: "Verify email validation RFC 5322"
Task T013: "Add experience level validation"
Task T014: "Ensure interests array format"
Task T015: "Add submit button disabled state"
Task T016: "Add loading indicator"

# Then in parallel:
Task T017: "Add responsive CSS"
Task T018: "Verify env var usage"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T008) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 - Signup (T009-T018)
4. **VALIDATE**: Test signup flow independently
5. Complete Phase 4: User Story 2 - Signin (T019-T029)
6. **VALIDATE**: Test signin + session persistence
7. **MVP READY**: Users can signup and signin - deploy for early feedback

### Incremental Delivery

1. **Foundation** (Setup + Foundational) → Project ready for auth implementation
2. **MVP** (US1 + US2) → Signup + Signin working → Test & Deploy
3. **Personalization** (US3) → Chatbot integration → Test & Deploy
4. **Infrastructure** (US4) → Profile context validation → Test & Deploy
5. **Polish** (Phase 7) → All refinements → Final deployment

### Parallel Team Strategy

With 2 developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **Split after Foundational**:
   - Developer A: User Story 1 (Signup) + User Story 3 (Chatbot)
   - Developer B: User Story 2 (Signin) + User Story 4 (Context)
3. **Merge & Polish**: Phase 7 together

### Sequential Single-Developer Strategy

Follow phases 1→2→3→4→5→6→7 in order. Each user story builds naturally on the previous.

---

## Notes

- **[P] tasks**: Different files or independent changes, can run concurrently
- **[Story] labels**: Maps to spec.md user stories for traceability
- **File paths**: All use absolute paths from repository root (`frontend/src/...`)
- **Existing code**: Many components already exist (SignupForm, SigninForm, UserContext, Layout) - tasks are UPDATES not creation
- **No tests**: Spec doesn't request automated tests - manual testing only (Tasks T048-T053)
- **Environment vars**: Docusaurus may or may not need `NEXT_PUBLIC_` prefix - verify in T001 and T018
- **Session timeout**: 1 hour inactivity with client-side tracking + backend validation
- **Interests**: 10 predefined checkboxes, optional field
- **Password**: Minimum 8 characters only (no complexity requirements per clarification)
- **Responsive**: Must work 320px (mobile) to 2560px (large desktop)
- **Isolation**: All auth code in `frontend/src/components/auth/` - no Docusaurus core modifications

---

## Task Count Summary

- **Phase 1 (Setup)**: 3 tasks
- **Phase 2 (Foundational)**: 5 tasks
- **Phase 3 (US1 - Signup)**: 10 tasks
- **Phase 4 (US2 - Signin)**: 11 tasks
- **Phase 5 (US3 - Chatbot)**: 6 tasks
- **Phase 6 (US4 - Context)**: 6 tasks
- **Phase 7 (Polish)**: 17 tasks

**Total**: 58 tasks

**MVP Scope** (Recommended first delivery): Phases 1-4 (29 tasks) = Signup + Signin working

**Parallel Opportunities**: 11 tasks marked [P] can run concurrently within their phases
