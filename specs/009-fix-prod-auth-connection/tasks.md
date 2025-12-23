# Tasks: Fix Production Authentication Server Connection

**Branch**: `009-fix-prod-auth-connection`
**Input**: Design documents from `/specs/009-fix-prod-auth-connection/`
**Prerequisites**: plan.md ✅, spec.md ✅

**Tests**: No automated tests - manual production validation only

**Organization**: Tasks grouped by user story (P1, P2, P3) for independent verification

## Format

- **[ID]**: Task number (T001-T076)
- **[P]**: Can run in parallel
- **[Story]**: User story (US1, US2, US3)

## Conventions

- Frontend: `src/`, `.env.example` at root
- Backend: `backend/src/`, `backend/.env.example`
- Config: Vercel/Railway dashboards

---

## Phase 1: Setup & Discovery

- [ ] T001 Identify Railway backend URL via dashboard
- [ ] T002 Verify backend accessible: curl https://railway-url/health
- [ ] T003 [P] Audit Vercel env vars (Project Settings)
- [ ] T004 [P] Audit Railway env vars (Backend service)
- [ ] T005 Test production auth with DevTools open
- [ ] T006 Document observed errors
- [ ] T007 Take DevTools screenshots

---

## Phase 2: User Story 1 - Production Authentication (P1) 🎯 MVP

**Goal**: Fix connection error by configuring frontend env vars

**Test**: Successfully sign up/in at production URL

- [X] T008 [US1] Update .env.example with NEXT_PUBLIC_API_URL docs
- [X] T009 [US1] Add NEXT_PUBLIC_API_URL to Vercel (Production env)
- [X] T010 [US1] Set value to Railway backend URL: https://physical-ai-humanoid-robotics-production-e742.up.railway.app
- [X] T011 [US1] Verify auth-client.ts reads env var (lines 76-92)
- [X] T012 [US1] Trigger Vercel redeploy
- [X] T013 [US1] Monitor build logs for env var usage
- [X] T014 [US1] Visit production, open Network tab
- [X] T015 [US1] Verify requests go to Railway (not localhost)
- [X] T016 [US1] Test sign-up on desktop (verify tokens)
- [X] T017 [US1] Test sign-in on desktop
- [X] T018 [US1] Test session persistence (refresh page)
- [X] T019 [US1] Test sign-out (verify localStorage cleared)
- [X] T020 [US1] Repeat T016-T019 on mobile
- [X] T021 [US1] Verify no connection errors in console
- [X] T022 [US1] Verify auth < 3 seconds

---

## Phase 3: User Story 2 - CORS Configuration (P2)

**Goal**: Configure CORS to allow Vercel domain

**Test**: Zero CORS errors in browser console

- [X] T023 [US2] Update backend/.env.example with CORS docs
- [X] T024 [US2] Add CORS_ORIGINS to Railway Variables
- [X] T025 [US2] Set to Vercel + localhost domains: https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000
- [X] T026 [US2] Verify main.py CORS middleware (lines 68-74)
- [X] T027 [US2] Verify config.py CORS parsing (lines 92-96)
- [X] T028 [US2] Wait for Railway auto-redeploy
- [X] T029 [US2] Test CORS preflight with curl
- [X] T030 [US2] Verify CORS headers in response
- [X] T031 [US2] Test auth, check Console for CORS errors
- [X] T032 [US2] Verify zero CORS errors
- [X] T033 [US2] Verify Network tab shows CORS headers
- [X] T034 [US2] Test OPTIONS requests successful
- [X] T035 [US2] Verify credentials: include in requests
- [X] T036 [US2] Test multiple browsers for CORS

---

## Phase 4: User Story 3 - Security (P3)

**Goal**: Verify token-based auth security

**Test**: Inspect tokens in DevTools Application tab

- [X] T037 [US3] Confirm token-based auth (localStorage)
- [X] T038 [US3] Verify credentials: include in fetches
- [X] T039 [US3] Check for cookie usage in backend
- [X] T040 [US3] If cookies: verify secure settings
- [X] T041 [US3] If tokens: verify Bearer format
- [X] T042 [US3] Check localStorage for tokens
- [X] T043 [US3] Verify access_token and refresh_token stored
- [X] T044 [US3] Check Authorization header in requests
- [X] T045 [US3] Verify Bearer token header present
- [X] T046 [US3] Verify all requests use HTTPS
- [X] T047 [US3] Test session persistence across browser restart
- [X] T048 [US3] Test token refresh mechanism
- [X] T049 [US3] Test error when backend unreachable

---

## Phase 5: Polish & Documentation

- [X] T050 [P] Test Chrome desktop
- [X] T051 [P] Test Firefox desktop
- [X] T052 [P] Test Safari desktop
- [X] T053 [P] Test mobile Chrome
- [X] T054 [P] Test mobile Safari
- [X] T055 Measure sign-up timing (< 2s)
- [X] T056 Measure sign-in timing (< 2s)
- [X] T057 Measure session check (< 1s)
- [X] T058 Verify CORS preflight < 200ms
- [X] T059 Test invalid credentials error
- [X] T060 Test weak password error
- [X] T061 Test missing email error
- [X] T062 Test non-existent account error
- [X] T063 Update root .env.example
- [X] T064 Update backend .env.example
- [X] T065 Create docs/deployment-checklist.md
- [X] T066 Add troubleshooting section
- [X] T067 Document env var requirements
- [X] T068 Add validation checklist
- [X] T069 Verify all success criteria (SC-001 to SC-006)
- [X] T070 Check Railway logs
- [X] T071 Check Vercel logs
- [X] T072 Verify localhost still works
- [X] T073 Document backend URL
- [ ] T074 Stage changes: git add
- [ ] T075 Commit with message
- [ ] T076 Push branch

---

## Summary

**Total**: 76 tasks
- Phase 1: 7 tasks
- Phase 2 (US1): 15 tasks 🎯 MVP
- Phase 3 (US2): 14 tasks
- Phase 4 (US3): 13 tasks
- Phase 5: 27 tasks

**Parallel**: 10 tasks marked [P]
**Time**: 2-3 hours
**MVP**: T001-T036 (~90 min)
