# Implementation Plan: Fix Production Authentication Server Connection Failure

**Branch**: `001-fix-prod-auth` | **Date**: 2025-12-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-fix-prod-auth/spec.md`

## Summary

Fix the persistent "Server not reachable" error affecting authentication (login/signup/logout) on both localhost and Vercel production (https://physical-ai-humanoid-robotics-e3c7.vercel.app/). Root cause identified as environment variable misconfiguration: `docusaurus.config.ts` uses `BACKEND_URL` instead of `NEXT_PUBLIC_API_URL`, preventing Vercel from injecting the Railway backend URL at build time. Secondary issue: CORS configuration on Railway may contain wildcard pattern incompatible with credential-based requests.

**Approach**: Systematic 8-phase investigation and remediation following the troubleshooting strategy defined in the spec. Each phase includes verification checkpoints to confirm findings before proceeding.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x, React 18.x, Docusaurus 3.x
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: Docusaurus (static site generator), React (UI framework)
- Backend: FastAPI 0.104+, python-jose 3.3.0 (JWT), passlib 1.7.4 (password hashing)

**Storage**:
- PostgreSQL on Neon (user data, profiles, refresh tokens)
- localStorage (browser-side: access tokens, refresh tokens)

**Testing**:
- Manual verification via browser DevTools (Network tab, Console)
- End-to-end testing: signup → login → logout flows

**Target Platform**:
- Frontend: Vercel (static hosting, CDN)
- Backend: Railway (container platform, PostgreSQL add-on via Neon integration)
- Browsers: Chrome, Firefox, Safari, Edge (latest 2 versions)

**Project Type**: Web application (Docusaurus frontend + FastAPI backend, monorepo structure)

**Performance Goals**:
- Signup: < 10 seconds end-to-end
- Login: < 5 seconds end-to-end
- Logout: Immediate UI update (< 200ms)

**Constraints**:
- No breaking changes to working localhost environment
- No database schema changes
- No refactoring of auth logic
- Minimal code changes (configuration only)
- Must maintain backward compatibility with existing tokens

**Scale/Scope**:
- Educational platform (expected 100-1000 concurrent users)
- Single production deployment (Vercel + Railway)
- 12-18 chapter textbook content

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitutional Compliance

**I. Fully Spec-Driven Workflow**:
- ✅ PASS: Explicit specification exists at `specs/001-fix-prod-auth/spec.md`
- ✅ PASS: Requirements clearly documented before implementation
- ✅ PASS: Troubleshooting strategy explicitly defined in spec

**II. Technical Accuracy, Clarity, and Educational Focus**:
- ✅ PASS: Fix targets production-blocking authentication issue
- ✅ PASS: Implementation preserves educational platform functionality
- ✅ PASS: Clear, systematic approach prevents future issues

**III. Modular Documentation**:
- ✅ PASS: Research findings in `research.md`
- ✅ PASS: Implementation plan in `plan.md`
- ✅ PASS: Data model documented in `data-model.md`
- ✅ PASS: API contracts in `contracts/`
- ✅ PASS: All documentation follows Spec-Kit Plus structure

**IV. Toolchain Fidelity**:
- ✅ PASS: Using Claude Code for planning and implementation guidance
- ✅ PASS: Docusaurus remains primary deployment target
- ✅ PASS: GitHub for version control
- ✅ PASS: Vercel for deployment (already in use)

### Violations & Justifications

**No violations detected**. This is a production bug fix that:
- Maintains existing architecture
- Makes minimal configuration changes
- Follows established patterns
- Improves system reliability without adding complexity

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-prod-auth/
├── spec.md                 # Feature specification (user requirements)
├── plan.md                 # This file (8-phase execution plan)
├── research.md             # Root cause analysis and investigation findings
├── data-model.md           # Auth data model (users, profiles, sessions)
├── quickstart.md           # Quick reference for auth setup
├── contracts/              # API contracts (auth endpoints)
│   └── auth-api.yaml       # OpenAPI specification for auth routes
├── checklists/             # Quality validation checklists
│   └── requirements.md     # Spec quality checklist
└── tasks.md                # Implementation tasks (/sp.tasks command output)
```

### Source Code (repository root)

This is a **monorepo web application** with Docusaurus frontend and FastAPI backend:

```text
# Root-level Docusaurus application (NO separate frontend/ folder)
src/
├── lib/
│   └── auth-client.ts         # ✏️ MODIFY: Add diagnostic logging
├── pages/
│   ├── auth-demo.tsx          # Auth demo page (for testing)
│   └── [other pages]
└── components/
    └── [UI components]

# Configuration files
docusaurus.config.ts            # ✏️ MODIFY: Change BACKEND_URL → NEXT_PUBLIC_API_URL
.env.example                    # Frontend env var documentation

# Backend (separate directory)
backend/
├── src/
│   ├── auth/                   # ✓ No changes needed
│   │   ├── routes.py           # Auth endpoints (signup, signin, signout, refresh)
│   │   ├── security.py         # JWT generation/validation
│   │   ├── schemas.py          # Request/response models
│   │   └── dependencies.py     # Auth dependencies
│   ├── users/                  # ✓ No changes needed
│   │   ├── routes.py           # User profile routes
│   │   ├── models.py           # User/Profile SQLAlchemy models
│   │   └── services.py         # User business logic
│   ├── core/
│   │   ├── config.py           # ✓ Correct: CORS_ORIGINS parsed from env
│   │   └── exceptions.py
│   ├── database/
│   │   ├── base.py             # SQLAlchemy base
│   │   ├── session.py          # Database session management
│   │   └── migrations/         # Alembic migrations
│   └── main.py                 # ✓ Correct: CORS middleware configured
└── .env.example                # Backend env var documentation

# Documentation
specs/001-fix-prod-auth/        # This feature's planning artifacts
history/prompts/001-fix-prod-auth/ # Prompt history records
```

**Structure Decision**: Monorepo with root-level Docusaurus app and separate backend/ directory. Auth fix requires **minimal changes**:
1. `docusaurus.config.ts` - Update environment variable reference (1 line)
2. `src/lib/auth-client.ts` - Add temporary diagnostic logging (2 lines)
3. **No backend code changes** - Only environment variable configuration updates on Railway dashboard

## Complexity Tracking

**No complexity violations** - This fix involves minimal changes:
- 1 line of code change in `docusaurus.config.ts`
- 2 environment variable updates (Vercel + Railway dashboards)
- No new dependencies, frameworks, or patterns introduced

---

## 8-Phase Execution Plan

This systematic plan follows the troubleshooting strategy defined in the specification. Each phase MUST be completed and verified before proceeding to the next.

---

### PHASE 1 — Backend Validation (Railway)

**Purpose**: Verify Railway backend is running, publicly accessible, and responding correctly to health checks and auth endpoint requests.

**Steps**:

1.1. **Identify Railway Backend URL**
   - Check Railway dashboard → Project → Deployments → Domain
   - Expected format: `https://<app-name>.up.railway.app`
   - Document URL for use in subsequent phases

1.2. **Test Health Endpoint**
   ```bash
   curl -v https://<railway-url>/health
   ```
   - **Expected Success**: HTTP 200 OK with JSON: `{"status": "healthy", "service": "rag-chatbot-api", "version": "1.0.0"}`
   - **Failure Indicators**:
     - Connection timeout → Railway deployment not running or network issue
     - 404 Not Found → Routes not registered correctly
     - 500+ errors → Backend application error

1.3. **Test Auth Endpoint Accessibility**
   ```bash
   curl -v -X POST https://<railway-url>/api/v1/auth/signin \
     -H "Content-Type: application/json" \
     -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" \
     -d '{"email":"test@example.com","password":"test"}'
   ```
   - **Expected Success**: HTTP 401 or 400 (endpoint reachable, authentication fails as expected)
   - **Failure Indicators**:
     - Network error → Backend unreachable
     - CORS error → Proceed to Phase 4 (CORS configuration)
     - 404 → Auth routes not registered

1.4. **Verify Database Connectivity**
   - Check Railway logs for database connection errors
   - Confirm PostgreSQL (Neon) connection string is set in `DATABASE_URL`
   - **Expected Success**: No connection errors in logs
   - **Failure Indicators**: SQLAlchemy connection errors, timeout errors

**STOP POINT**: Document Railway URL and health check results. If backend is unreachable, fix deployment before proceeding.

---

### PHASE 2 — Backend Environment Variables (Railway)

**Purpose**: Audit all required backend environment variables on Railway and verify CORS configuration.

**Steps**:

2.1. **List Required Variables** (from `backend/.env.example`):
   ```
   ✓ CORS_ORIGINS
   ✓ DATABASE_URL
   ✓ BETTER_AUTH_SECRET
   ✓ ACCESS_TOKEN_EXPIRE_MINUTES (optional, has default)
   ✓ REFRESH_TOKEN_EXPIRE_DAYS (optional, has default)
   ✓ COHERE_API_KEY
   ✓ QDRANT_URL
   ✓ QDRANT_API_KEY
   ✓ TEXTBOOK_SITEMAP_URL
   ```

2.2. **Verify CORS_ORIGINS Configuration**
   - Navigate to Railway Dashboard → Variables
   - Check current value of `CORS_ORIGINS`
   - **Expected Format**: `https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000`
   - **Common Issues**:
     - Contains wildcard `*.vercel.app` → INVALID with credentials
     - Missing Vercel domain → Add it
     - Contains spaces → Remove spaces (parser strips them but explicit format better)

2.3. **Verify Auth & Database Variables**
   - ✓ `DATABASE_URL` exists and matches Neon PostgreSQL format
   - ✓ `BETTER_AUTH_SECRET` exists (64-character hex string)
   - ✓ `ACCESS_TOKEN_EXPIRE_MINUTES` = 15 (or omit for default)
   - ✓ `REFRESH_TOKEN_EXPIRE_DAYS` = 7 (or omit for default)

2.4. **Apply CORS Fix** (if needed):
   - Update `CORS_ORIGINS` to exact Vercel URL (NO WILDCARD):
     ```
     https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000
     ```
   - Railway will automatically redeploy on variable change
   - Wait for deployment to complete (~2 minutes)

**STOP POINT**: Document all environment variable states. If any required variables are missing, add them before proceeding.

---

### PHASE 3 — Frontend Environment Variables (Vercel)

**Purpose**: Verify Vercel environment variables and ensure Railway backend URL is properly configured for browser access.

**Steps**:

3.1. **Check Vercel Environment Variables**
   - Navigate to Vercel Dashboard → Project Settings → Environment Variables
   - Look for `NEXT_PUBLIC_API_URL`
   - **Required Value**: Railway backend URL from Phase 1.1

3.2. **Verify Variable Contexts**
   - ✓ Production environment: `NEXT_PUBLIC_API_URL` = Railway URL
   - ✓ Preview environment: `NEXT_PUBLIC_API_URL` = Railway URL (or separate staging backend)
   - ✓ Development environment: Can be omitted (falls back to localhost)

3.3. **Add/Update NEXT_PUBLIC_API_URL** (if missing or incorrect):
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://<railway-app>.up.railway.app` (NO TRAILING SLASH)
   - Apply to: ✓ Production, ✓ Preview, ✓ Development

3.4. **Verify No Localhost References**
   - Confirm value is Railway URL, not `http://localhost:8000`
   - Check for typos in URL
   - Ensure HTTPS (not HTTP)

**STOP POINT**: Document Vercel environment variable configuration. Note: Variable changes require redeployment to take effect.

---

### PHASE 4 — API URL Wiring in Frontend Code

**Purpose**: Locate where login/signup requests are made and verify correct environment variable usage.

**Steps**:

4.1. **Inspect `src/lib/auth-client.ts`** (primary auth client):
   - Line 76-92: `getBackendUrl()` function
   - Verify logic:
     1. Checks `process.env.NEXT_PUBLIC_API_URL` (build-time)
     2. Checks `window.__ENV__.API_URL` (runtime, unused in Docusaurus)
     3. Falls back to `http://localhost:8000`
   - **Finding**: This is CORRECT, no changes needed here

4.2. **Inspect `docusaurus.config.ts`** (CRITICAL):
   - Line ~193: `customFields.backendUrl`
   - **Current (INCORRECT)**:
     ```typescript
     backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
     ```
   - **Required Fix**:
     ```typescript
     backendUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
     ```
   - **Impact**: This sets `window.CHATBOT_API_URL` used by auth forms

4.3. **Verify Build-time vs Runtime Access**
   - Docusaurus is static site generator → `process.env` frozen at build time
   - `NEXT_PUBLIC_API_URL` must be set BEFORE building
   - Runtime injection not supported without custom plugin
   - **Decision**: Use build-time environment variable (current approach)

4.4. **Add Diagnostic Logging** (temporary):
   ```typescript
   // src/lib/auth-client.ts, line 92 (after BACKEND_URL assignment)
   console.log('[DEBUG] Auth backend URL:', BACKEND_URL);
   console.log('[DEBUG] NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
   ```
   - This logging will help verify URL resolution in browser console
   - Mark with `[DEBUG]` prefix for easy removal later

**STOP POINT**: Document all locations where backend URL is referenced. Prepare fix for `docusaurus.config.ts`.

---

### PHASE 5 — CORS Configuration Verification

**Purpose**: Validate CORS setup on Railway backend ensures Vercel domain is allowed with credentials.

**Steps**:

5.1. **Review Backend CORS Code** (`backend/src/main.py`, lines 68-74):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.cors_origins,  # From CORS_ORIGINS env var
       allow_credentials=True,               # Requires explicit origins
       allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
       allow_headers=["*"],
   )
   ```
   - **Configuration is CORRECT** - uses dynamic origins from env var
   - **Credentials enabled** - requires explicit origin (no wildcard)

5.2. **Test CORS Preflight Request**:
   ```bash
   curl -v -X OPTIONS https://<railway-url>/api/v1/auth/signin \
     -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type"
   ```
   - **Expected Success Headers**:
     ```
     Access-Control-Allow-Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app
     Access-Control-Allow-Credentials: true
     Access-Control-Allow-Methods: POST, OPTIONS
     Access-Control-Allow-Headers: Content-Type
     ```
   - **Failure Indicators**:
     - `Access-Control-Allow-Origin: *` → Wildcard detected, credentials will fail
     - Missing `Access-Control-Allow-Credentials` → Middleware issue
     - Origin mismatch → CORS_ORIGINS doesn't include Vercel domain

5.3. **Verify Credentials Support**:
   - Frontend uses `credentials: 'include'` in fetch requests
   - Backend must respond with `Access-Control-Allow-Credentials: true`
   - Origin must be explicit (wildcards forbidden by CORS spec)

5.4. **Confirm Local Development Still Works**:
   - `CORS_ORIGINS` should include `http://localhost:3000`
   - Test localhost auth flows to ensure no regression

**STOP POINT**: Document CORS preflight response headers. If preflight fails, CORS_ORIGINS needs updating (Phase 2).

---

### PHASE 6 — Auth Flow Verification (better-auth)

**Purpose**: Trace signup/login flows end-to-end and identify exact failure point.

**Steps**:

6.1. **Trace Signup Flow**:
   - Frontend: `SignupForm.tsx` → `authApi.signup()` → `makeAuthRequest('/api/v1/auth/signup')`
   - Backend: `POST /api/v1/auth/signup` → `create_user()` → Database insert → JWT generation
   - **Expected Success**: HTTP 201 with `{user, tokens}`
   - **Test Command**:
     ```bash
     curl -v -X POST https://<railway-url>/api/v1/auth/signup \
       -H "Content-Type: application/json" \
       -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" \
       -d '{
         "email": "test@example.com",
         "password": "Test123!@#",
         "software_experience": "intermediate",
         "hardware_experience": "beginner",
         "interests": ["robotics"]
       }'
     ```

6.2. **Trace Login Flow**:
   - Frontend: `SigninForm.tsx` → `authApi.signin()` → `makeAuthRequest('/api/v1/auth/signin')`
   - Backend: `POST /api/v1/auth/signin` → Password verification → JWT generation
   - **Expected Success**: HTTP 200 with `{user, tokens}`
   - **Test Command**:
     ```bash
     curl -v -X POST https://<railway-url>/api/v1/auth/signin \
       -H "Content-Type: application/json" \
       -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" \
       -d '{"email": "test@example.com", "password": "Test123!@#"}'
     ```

6.3. **Identify Failure Point**:
   - **Network Error**: Backend unreachable → Check Phase 1
   - **CORS Error**: Preflight blocked → Check Phase 5
   - **401 Unauthorized**: Credentials wrong (expected for test data)
   - **400 Validation**: Request body format issue
   - **500 Server Error**: Backend application error → Check Railway logs

6.4. **Verify Token Structure**:
   - Response includes `tokens.access_token` (JWT)
   - Response includes `tokens.refresh_token` (UUID)
   - Frontend stores both in localStorage

**STOP POINT**: Document exact error messages and HTTP status codes. If flows fail, identify whether issue is network, CORS, or application logic.

---

### PHASE 7 — Session & Cookie Handling

**Purpose**: Verify token-based session management works correctly across page refreshes.

**Steps**:

7.1. **Verify Token Storage Mechanism**:
   - **Current Implementation**: localStorage (not cookies)
   - Access token: Stored at key `access_token`
   - Refresh token: Stored at key `refresh_token`
   - **No cookie configuration required** (tokens sent via Authorization header)

7.2. **Test Session Persistence**:
   - Complete login flow
   - Verify tokens stored in localStorage
   - Refresh page
   - Verify `authApi.getSession()` retrieves user data using stored token
   - **Expected**: Session persists without re-authentication

7.3. **Cookie Flags Review** (informational only):
   - System uses **Bearer token authentication**, not cookie-based sessions
   - `credentials: 'include'` present but redundant (no cookies exchanged)
   - SameSite/Secure flags are NOT applicable
   - **No changes needed** in this phase

7.4. **Test Token Refresh Flow**:
   - Wait 15+ minutes (access token expiration)
   - OR manually delete access_token from localStorage
   - Make authenticated request
   - Verify `authApi.refreshToken()` automatically called
   - **Expected**: New access token obtained using refresh token

**STOP POINT**: Confirm tokens are stored and retrieved correctly. Verify session persists across page refreshes.

---

### PHASE 8 — UI State & Navbar Integration

**Purpose**: Verify authentication state propagates correctly to Docusaurus navbar and UI updates on login/logout.

**Steps**:

8.1. **Test Navbar State on Load**:
   - Visit Vercel production site: https://physical-ai-humanoid-robotics-e3c7.vercel.app/
   - **If logged out**: Navbar shows "Login" and "Sign Up" buttons
   - **If logged in**: Navbar shows user profile and "Logout" button

8.2. **Test Login → Navbar Update**:
   - Click "Login" in navbar
   - Enter credentials and submit
   - **Expected**: Navbar immediately updates to show logged-in state
   - **Verify**: User profile visible, "Logout" button appears

8.3. **Test Logout → Navbar Update**:
   - Click "Logout" button
   - **Expected**: Navbar immediately updates to show logged-out state
   - **Verify**: "Login" and "Sign Up" buttons visible again
   - **Verify**: localStorage cleared (`access_token` and `refresh_token` removed)

8.4. **Test Page Navigation While Logged In**:
   - Navigate between pages (e.g., Home → About → Chatbot)
   - **Expected**: Session persists, navbar stays in logged-in state
   - **Verify**: No re-authentication required

**STOP POINT**: Confirm UI state management works correctly. If navbar doesn't update, check AuthContext integration.

---

## Implementation Checklist

### Code Changes Required

**File 1: `docusaurus.config.ts`** (1 line change)
```diff
- backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
+ backendUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
```
- **Location**: Line ~193 in customFields section
- **Risk**: Low (fallback preserves localhost compatibility)
- **Testing**: Verify localhost still works after change

**File 2: `src/lib/auth-client.ts`** (temporary diagnostic logging)
```typescript
// Line 92, after: const BACKEND_URL = getBackendUrl();
console.log('[DEBUG] Auth backend URL:', BACKEND_URL);
console.log('[DEBUG] NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
```
- **Purpose**: Verify environment variable resolution in browser
- **Removal**: Delete after confirming fix works

---

### Environment Variable Changes

**Vercel Dashboard** (https://vercel.com/dashboard → Project → Settings → Environment Variables):
1. Add or update:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://<railway-app>.up.railway.app` (NO TRAILING SLASH)
   - Contexts: ✓ Production, ✓ Preview, ✓ Development
2. Redeploy from Deployments tab (environment variable changes require rebuild)

**Railway Dashboard** (https://railway.app/dashboard → Project → Variables):
1. Update `CORS_ORIGINS`:
   - Current: `https://*.vercel.app,http://localhost:3000` (INVALID)
   - New: `https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000`
2. Railway auto-redeploys on variable change (wait ~2 minutes)

---

### Deployment Sequence

**Step 1: Update Railway Environment Variables**
- Reason: Backend must be ready to accept requests from Vercel before frontend deploys
- Action: Update `CORS_ORIGINS` as specified above
- Verification: Wait for Railway deployment, test CORS preflight (Phase 5.2)

**Step 2: Update Code and Push to GitHub**
- Branch: `001-fix-prod-auth` (or `main` as per user request)
- Files: `docusaurus.config.ts`, `src/lib/auth-client.ts` (diagnostic logging)
- Commit message:
  ```
  fix(auth): use NEXT_PUBLIC_API_URL for production compatibility

  - Update docusaurus.config.ts to use NEXT_PUBLIC_API_URL instead of BACKEND_URL
  - Add temporary diagnostic logging to verify environment variable resolution
  - Fixes "Server not reachable" error on Vercel production

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

**Step 3: Update Vercel Environment Variables**
- Action: Set `NEXT_PUBLIC_API_URL` as specified above
- **IMPORTANT**: Variable changes don't auto-rebuild; must trigger manual redeploy

**Step 4: Redeploy Vercel**
- Trigger: Push to GitHub OR manual redeploy from Vercel dashboard
- Build: Vercel builds with `NEXT_PUBLIC_API_URL` injected at build time
- Verification: Check build logs for environment variable presence

**Step 5: Verify Production**
- URL: https://physical-ai-humanoid-robotics-e3c7.vercel.app/
- Test: Complete signup → login → logout cycle
- Check: Browser console for `[DEBUG]` logs showing Railway URL
- Confirm: No "Server not reachable" errors

**Step 6: Cleanup**
- Remove `[DEBUG]` console.log statements from `src/lib/auth-client.ts`
- Commit cleanup:
  ```
  chore: remove diagnostic logging from auth client

  - Remove temporary [DEBUG] console.log statements
  - Auth fix confirmed working in production

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

---

## Success Validation

### Functional Requirements Checklist

- [ ] **FR-001**: Auth requests route to Railway backend (not localhost)
  - Verify: Browser Network tab shows requests to `https://<railway-app>.up.railway.app`

- [ ] **FR-002**: `NEXT_PUBLIC_API_URL` used consistently
  - Verify: `[DEBUG]` log shows Railway URL, not localhost

- [ ] **FR-003**: CORS allows Vercel domain explicitly
  - Verify: OPTIONS preflight returns `Access-Control-Allow-Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app`

- [ ] **FR-004**: Credentials handling enabled
  - Verify: Response includes `Access-Control-Allow-Credentials: true`

- [ ] **FR-005**: Secure cookie transmission (N/A - token-based, not cookie-based)

- [ ] **FR-006**: Clear error messages
  - Verify: No "Server not reachable" errors; validation errors are specific

- [ ] **FR-007**: Localhost compatibility maintained
  - Verify: Run `npm start` locally, test signup/login/logout flows

- [ ] **FR-008**: No localhost URLs in production
  - Verify: `[DEBUG]` log in production shows Railway URL

- [ ] **FR-009**: OPTIONS preflight succeeds
  - Verify: curl test (Phase 5.2) returns 200 OK with CORS headers

- [ ] **FR-010**: No breaking changes to auth logic
  - Verify: Only configuration files changed, no auth/*.py or auth-client.ts logic modified

- [ ] **FR-011**: Diagnostic logging present (temporary)
  - Verify: Console shows `[DEBUG]` logs during testing

- [ ] **FR-012**: Railway env vars match requirements
  - Verify: All required variables present in Railway dashboard

### Success Criteria Checklist

- [ ] **SC-001**: Signup completes in < 10 seconds
- [ ] **SC-002**: Login completes in < 5 seconds
- [ ] **SC-003**: Logout updates UI immediately (< 200ms)
- [ ] **SC-004**: Zero "Unable to connect to authentication server" errors
- [ ] **SC-005**: Railway logs show incoming requests from Vercel (check Railway → Logs)
- [ ] **SC-006**: Localhost development unchanged (test local environment)
- [ ] **SC-007**: Browser Network tab shows successful CORS preflight (status 200-204)
- [ ] **SC-008**: Session persists across page refreshes (test F5 after login)

---

## Rollback Plan

### If Production Fix Fails

**Rollback Step 1: Revert Code Changes**
```bash
git revert <commit-hash>
git push origin 001-fix-prod-auth
```
- Vercel auto-deploys on push
- Time: ~2 minutes

**Rollback Step 2: Revert Vercel Environment Variables**
- Delete `NEXT_PUBLIC_API_URL` from Vercel dashboard
- OR set to previous value
- Redeploy from Vercel dashboard
- Time: ~1 minute

**Rollback Step 3: Revert Railway Environment Variables**
- Restore previous `CORS_ORIGINS` value
- Railway auto-redeploys
- Time: ~2 minutes

**Total Rollback Time**: < 5 minutes

### If Localhost Breaks

**Immediate Action**:
1. Check fallback in `docusaurus.config.ts`: `|| 'http://localhost:8000'`
2. Verify backend running on `localhost:8000`
3. If backend port changed, update fallback value

**Prevention**:
- Test localhost thoroughly before deploying to production
- Keep fallback values intact in all environment variable checks

---

## Post-Fix Cleanup

**Step 1: Remove Diagnostic Logging**
- Delete `console.log('[DEBUG] ...')` statements from `src/lib/auth-client.ts`
- Commit with message: `chore: remove diagnostic logging from auth client`

**Step 2: Update Documentation**
- Mark research.md as "Implementation Complete"
- Document actual Railway URL and Vercel URL used
- Archive troubleshooting logs if needed

**Step 3: Close Related Issues**
- Update GitHub issues with fix details
- Link to commit(s) that resolved the issue
- Mark as closed

**Step 4: Monitor Production**
- Watch Railway logs for auth requests from Vercel
- Monitor error rates in application logs
- Verify no new "Server not reachable" errors reported

---

## Risk Assessment

### Probability of Success: 95%

**High Confidence Because**:
- Root cause clearly identified through code analysis
- Fix is minimal (1 line code + 2 env vars)
- No database schema changes
- No auth logic changes
- Localhost fallback prevents regression

**Remaining 5% Risk Factors**:
- Railway backend URL might change (requires env var update)
- Vercel caching might delay env var propagation (requires cache clear)
- Unexpected CORS edge case (mitigated by explicit origin config)

### Worst Case Scenarios

**Scenario 1: Fix doesn't work**
- **Impact**: Production auth still broken (same as current state)
- **Response**: Rollback within 5 minutes
- **Mitigation**: Test on Vercel Preview deployment first

**Scenario 2: Localhost breaks**
- **Impact**: Development environment unusable
- **Response**: Immediate rollback + verify fallback logic
- **Mitigation**: Thorough localhost testing before production deploy

**Scenario 3: Partial fix (production works, localhost breaks)**
- **Impact**: Production fixed but development hindered
- **Response**: Adjust fallback value or add environment detection
- **Mitigation**: Conditional logic based on `window.location.hostname`

---

## Next Steps After Plan Approval

1. Execute Phase 1: Backend Validation
   - Test Railway backend accessibility
   - Document Railway URL
   - Verify health endpoint

2. Proceed through Phases 2-8 sequentially
   - Complete each phase before moving to next
   - Document findings at each STOP POINT
   - Update this plan with actual observations

3. Implement code changes (after investigation confirms root cause)
   - Update `docusaurus.config.ts`
   - Add diagnostic logging
   - Push to feature branch

4. Update environment variables
   - Railway: `CORS_ORIGINS`
   - Vercel: `NEXT_PUBLIC_API_URL`

5. Deploy and verify
   - Test on Vercel production
   - Run through success criteria checklist
   - Monitor for errors

6. Clean up and close
   - Remove diagnostic logging
   - Update documentation
   - Close GitHub issues
   - Mark feature as complete
