# Implementation Plan: Fix Production Authentication Server Connection

**Branch**: `009-fix-prod-auth-connection` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-fix-prod-auth-connection/spec.md`

## Summary

Fix the "Unable to connect to authentication server" error occurring on the production Vercel deployment while maintaining working localhost functionality. The issue stems from frontend environment variables not being configured for production, hardcoded localhost references in auth client code, missing CORS configuration for Vercel domain, and potential cookie security settings incompatible with cross-origin HTTPS.

**Technical Approach**:
1. Configure frontend environment variables in Vercel (`NEXT_PUBLIC_API_URL`)
2. Update auth-client.ts to use environment-based backend URL (already partially implemented)
3. Add Vercel production domain to backend CORS whitelist
4. Ensure backend cookie settings support HTTPS cross-origin (Secure, SameSite=None)
5. Validate deployment with comprehensive production testing

## Technical Context

**Language/Version**:
- Frontend: TypeScript/React (Docusaurus 3.9.2, Node.js)
- Backend: Python 3.11+ (FastAPI 0.104+, uvicorn)

**Primary Dependencies**:
- Frontend: Docusaurus, React, custom auth-client.ts (FastAPI integration)
- Backend: FastAPI, passlib[bcrypt], python-jose[cryptography], SQLAlchemy 2.0, psycopg2-binary

**Storage**: PostgreSQL (Neon) for user authentication, profiles, and sessions

**Testing**: Manual production validation (no automated tests for this fix)

**Target Platform**:
- Frontend: Vercel (static site deployment with client-side authentication)
- Backend: Railway (Python/FastAPI server with public HTTPS endpoint)

**Project Type**: Web application (Docusaurus frontend + FastAPI backend)

**Performance Goals**: Authentication requests < 2 seconds, 100% connection success rate

**Constraints**:
- Must maintain localhost development functionality
- Zero breaking changes to existing authentication flow
- CORS must only whitelist specific domains (no wildcards)
- Cookies must be Secure + HttpOnly + SameSite appropriate for cross-origin

**Scale/Scope**: Small-scale educational platform, <100 concurrent users expected

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS

This fix aligns with project constitution principles:
- **Code Quality**: Minimal changes, focused on configuration not code refactoring
- **Security**: Explicitly configuring secure cookie settings and CORS whitelist
- **Testing**: Production validation testing will be performed
- **Architecture**: No architectural changes, only environment configuration
- **Performance**: Targeting <2s authentication (within acceptable range)

No constitution violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/009-fix-prod-auth-connection/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation plan)
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (✅ passed)
└── tasks.md             # Will be created by /sp.tasks command
```

### Source Code (repository root)

```text
# Web application structure (Docusaurus + FastAPI)

# Frontend (Docusaurus - deployed to Vercel)
src/
├── components/
│   └── auth/
│       ├── AuthContext.tsx       # Auth state management
│       ├── SigninForm.tsx        # Sign-in UI
│       ├── SignupForm.tsx        # Sign-up UI
│       └── LoginLogout.tsx       # Navbar auth component
├── lib/
│   └── auth-client.ts            # 🔧 MODIFY: Backend URL configuration
└── pages/
    └── auth-demo.tsx             # Authentication demo page

docusaurus.config.ts              # 🔧 MODIFY: Add customFields for API URL

.env.example                      # 🔧 UPDATE: Document NEXT_PUBLIC_API_URL

# Backend (FastAPI - deployed to Railway)
backend/
├── src/
│   ├── main.py                   # 🔧 MODIFY: CORS configuration
│   ├── core/
│   │   └── config.py             # Backend settings (reads from .env)
│   ├── auth/
│   │   ├── routes.py             # Authentication endpoints
│   │   └── security.py           # 🔧 VERIFY: Cookie security settings
│   └── users/
│       └── routes.py             # User profile endpoints
├── .env.example                  # 🔧 UPDATE: Document CORS_ORIGINS
└── railway.json                  # Railway deployment config (already exists)

# Deployment Configuration
# (Vercel dashboard - no file changes needed, just env var configuration)
```

**Structure Decision**: This is a web application with separated frontend (Docusaurus/React on Vercel) and backend (FastAPI on Railway). The fix focuses on environment configuration and CORS settings to enable cross-origin authentication between the two deployed services.

## Complexity Tracking

N/A - No constitution violations. This is a configuration fix, not a feature requiring complexity justification.

## Implementation Phases

###  Phase 0: Current State Analysis & Root Cause Confirmation

**Objective**: Verify the exact root causes of authentication failure in production

**Key Tasks**:
1. Identify and document backend Railway deployment URL
2. Audit Vercel environment variables (verify `NEXT_PUBLIC_API_URL` is NOT set)
3. Audit Railway environment variables (verify `CORS_ORIGINS` may be missing Vercel domain)
4. Test current production state with browser DevTools
5. Document observed errors (console + network tab)

**Acceptance Criteria**:
- Backend public URL documented  
- Frontend env vars confirmed missing/incorrect  
- Backend CORS origins confirmed missing Vercel domain
- Production error confirmed with DevTools screenshots

---

### Phase 1: Frontend Environment Configuration

**Objective**: Configure Vercel to provide correct backend URL at build time

**Key Tasks**:
1. Update `.env.example` to document `NEXT_PUBLIC_API_URL`
2. Configure Vercel environment variable: `NEXT_PUBLIC_API_URL=https://<railway-backend>`
3. Verify `auth-client.ts:76-92` reads `process.env.NEXT_PUBLIC_API_URL` (already correct)
4. Trigger Vercel redeploy with new environment variable
5. Verify build logs and production requests go to Railway URL

**Acceptance Criteria**:
- `.env.example` documents `NEXT_PUBLIC_API_URL`
- Vercel environment variable configured
- Frontend deploys successfully
- Browser Network tab shows requests to Railway (not localhost)

**Rollback**: Remove Vercel env var and redeploy (restores original state)

---

### Phase 2: Backend CORS Configuration

**Objective**: Whitelist Vercel production domain in backend CORS middleware

**Key Tasks**:
1. Update `backend/.env.example` to document CORS configuration
2. Configure Railway environment variable:  
   `CORS_ORIGINS=https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000,http://localhost:8080`
3. Verify `backend/src/main.py:68-74` CORS middleware (already correct)
4. Wait for Railway auto-redeploy
5. Test CORS with curl preflight request

**Acceptance Criteria**:
- `backend/.env.example` documents `CORS_ORIGINS`
- Railway environment variable updated
- CORS preflight requests succeed from Vercel  
- Browser console shows no CORS errors

**Rollback**: Revert Railway env var to previous value

---

### Phase 3: Cookie Security Configuration (Verification)

**Objective**: Ensure cookies configured for HTTPS cross-origin (if used)

**Key Tasks**:
1. Review authentication mechanism (token-based vs cookie-based)
2. Verify current implementation uses `localStorage` + Bearer tokens (based on `auth-client.ts`)
3. Confirm `credentials: 'include'` is set (for potential future cookie support)
4. If cookies used: verify `Secure=True`, `HttpOnly=True`, `SameSite=None`

**Acceptance Criteria**:
- Authentication mechanism identified (likely token-based)
- No cookie-related errors in DevTools
- Authorization headers sent correctly

**Note**: Current implementation appears to be token-based (localStorage), so cookie configuration is likely N/A.

---

### Phase 4: Production Validation & Testing

**Objective**: Comprehensive end-to-end authentication testing in production

**Key Tasks**:
1. Test sign-up flow on desktop (DevTools open)
2. Test sign-in flow on desktop
3. Test session persistence (page refresh)
4. Test sign-out flow
5. Repeat all tests on mobile device/emulation
6. Test error handling (invalid credentials)
7. Test cross-browser compatibility (Chrome + Firefox/Safari)
8. Measure performance (authentication < 3s target)
9. Monitor Railway logs for errors

**Acceptance Criteria**:
- Sign-up works on desktop and mobile
- Sign-in works on desktop and mobile
- Session persists across refreshes
- Sign-out clears session correctly
- No network/CORS errors in console
- All requests go to Railway backend
- Response times meet targets
- Works in multiple browsers

**Rollback**: If critical failure, check Vercel env vars, Railway CORS, or remove Vercel `NEXT_PUBLIC_API_URL`

---

### Phase 5: Documentation & Deployment Guide

**Objective**: Document fix for future reference

**Key Tasks**:
1. Update main README with production deployment section
2. Create deployment checklist (`docs/deployment-checklist.md`)
3. Add troubleshooting section to deployment guide
4. Commit changes with descriptive message

**Acceptance Criteria**:
- Environment variables documented in `.env.example` files
- Deployment checklist created
- Troubleshooting guide added
- Changes committed to version control

---

## Key Technical Decisions

### Decision 1: Environment Variable Strategy  
**Chosen**: Use `NEXT_PUBLIC_API_URL` (Vercel standard, build-time injection)  
**Rationale**: Already partially implemented, standard pattern, no code changes needed

### Decision 2: CORS Configuration  
**Chosen**: Whitelist specific Vercel domain  
**Rationale**: Secure, supports `allow_credentials=True`, already implemented

### Decision 3: Authentication Mechanism  
**Chosen**: Token-based with localStorage + Bearer headers  
**Rationale**: Simpler than cookies for cross-origin, already implemented

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Vercel env var not applied | Low | High | Verify in build logs, manual redeploy |
| Railway URL changes | Low | High | Document URL, set up monitoring |
| CORS still blocks | Low | Medium | Test with curl, verify exact domain |
| Token storage fails | Very Low | High | Test localStorage in production |
| Performance degradation | Very Low | Low | HTTPS adds minimal latency |
| Breaking localhost | Very Low | High | Fallback maintains localhost behavior |

**Overall Risk**: **LOW** - Configuration-only fix with clear rollback paths

---

## Implementation Summary

**Total Estimated Time**: 2-3 hours (mostly testing and documentation)

**Dependencies**:
- Access to Vercel dashboard
- Access to Railway dashboard
- Backend Railway URL from deployment

**Success Metrics** (from spec.md):
- Users authenticate in production within 3 seconds
- 100% authentication attempts receive proper response  
- Zero CORS errors in browser console
- Works on mobile and desktop
- Proper security attributes on tokens/cookies

**Next Steps**:
1. Run `/sp.tasks` to generate detailed task breakdown
2. Execute tasks in order (Phase 0 → Phase 5)
3. Validate all acceptance criteria
4. Create pull request
5. Deploy and verify

---

## Files to Modify

| File | Type | Changes |
|------|------|---------|
| `.env.example` | Docs | Add `NEXT_PUBLIC_API_URL` documentation |
| `backend/.env.example` | Docs | Update `CORS_ORIGINS` documentation |
| Vercel Dashboard | Config | Set `NEXT_PUBLIC_API_URL` env var |
| Railway Dashboard | Config | Update `CORS_ORIGINS` env var |
| `docs/deployment-checklist.md` | Docs | Create checklist (new file) |

**Files NOT Modified** (already correct):
- `src/lib/auth-client.ts` - Already reads `NEXT_PUBLIC_API_URL`
- `backend/src/main.py` - CORS middleware configured
- `backend/src/core/config.py` - CORS parsing implemented

---

## References

- **Specification**: [spec.md](./spec.md)
- **Vercel Env Vars**: https://vercel.com/docs/concepts/projects/environment-variables
- **Railway Env Vars**: https://docs.railway.app/deploy/variables
- **FastAPI CORS**: https://fastapi.tiangolo.com/tutorial/cors/

