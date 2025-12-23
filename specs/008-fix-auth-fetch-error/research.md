# Research: Authentication Fetch Error Diagnosis

**Feature**: 008-fix-auth-fetch-error
**Date**: 2025-12-23
**Purpose**: Identify root causes of "Failed to fetch" errors during authentication operations

## Investigation Summary

Based on codebase analysis, several potential root causes have been identified for the "Failed to fetch" errors occurring during authentication operations (signup, signin, session check, logout).

## Current Architecture

### Authentication Implementation

**Location**: `src/lib/auth-client.ts`

**Current Setup**:
- Custom authentication client (NOT using Better Auth's built-in client)
- JWT tokens stored in localStorage (access_token, refresh_token)
- Backend FastAPI service at `http://localhost:8000` (hardcoded fallback)
- Runtime configuration via `window.CHATBOT_API_URL`

**Authentication Endpoints**:
- Signup: `POST ${BACKEND_URL}/api/v1/auth/signup`
- Signin: `POST ${BACKEND_URL}/api/v1/auth/signin`
- Signout: `POST ${BACKEND_URL}/api/v1/auth/signout`
- Session/Profile: `GET ${BACKEND_URL}/api/v1/profile/`
- Token Refresh: `POST ${BACKEND_URL}/api/v1/auth/refresh`

### Environment Configuration Analysis

**Backend URL Determination** (src/lib/auth-client.ts:8-10):
```typescript
const BACKEND_URL = (typeof window !== 'undefined' && (window as any).CHATBOT_API_URL)
  ? (window as any).CHATBOT_API_URL
  : 'http://localhost:8000';
```

**Issues Identified**:
1. ❌ **No environment variable support** - relies on window global or hardcoded localhost
2. ❌ **Production will default to localhost** - `window.CHATBOT_API_URL` not set in Vercel
3. ❌ **No .env file usage** - `.env.example` exists but not being read by frontend

### Fetch Request Analysis

**Credentials Handling**:
- ✅ All auth requests include `credentials: 'include'`
- ✅ Authorization headers used for authenticated endpoints
- ❌ **But using localStorage for tokens, not cookies** - contradicts `credentials: 'include'`

**Current Pattern** (example from signin):
```typescript
const response = await fetch(`${BACKEND_URL}/api/v1/auth/signin`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // ← Used but tokens are in localStorage
  body: JSON.stringify({ email, password }),
});
```

### CORS Configuration

**Status**: NEEDS INVESTIGATION

**What We Don't Know Yet**:
- Is CORS configured in the FastAPI backend?
- What origins are allowed (localhost:3000, Vercel production domain)?
- Are credentials allowed in CORS policy?
- Are proper preflight response headers set?

**Backend Location**: `backend/src/` (auth routes exist but CORS middleware not yet examined)

### Cookie vs Token Strategy

**Current Implementation**:
- Uses JWT tokens in localStorage (see auth-client.ts:73-74, 95-96)
- Includes `credentials: 'include'` in fetch (contradictory)
- No evidence of HTTP-only cookies being set by backend

**Conflict**:
- Spec assumes Better Auth cookie-based sessions
- Implementation uses custom JWT + localStorage approach
- This mismatch may be causing session management issues

## Root Cause Hypotheses

### 1. **Environment URL Misconfiguration** (HIGH CONFIDENCE)

**Problem**: Production deployments on Vercel will use `http://localhost:8000` because `window.CHATBOT_API_URL` is not set.

**Evidence**:
- Hardcoded fallback to localhost in auth-client.ts
- No environment variable injection in build process
- No Vercel-specific environment configuration found

**Impact**: All production auth requests will fail with "Failed to fetch" (cannot reach localhost from browser)

**Resolution Needed**:
- Use Docusaurus environment variables (process.env.*)
- Configure Vercel environment variables
- Implement proper runtime config for different environments

### 2. **CORS Misconfiguration** (MEDIUM-HIGH CONFIDENCE)

**Problem**: Backend may not allow requests from Vercel production origin or may not permit credentials.

**Evidence** (circumstantial):
- No CORS middleware found in examined code
- FastAPI requires explicit CORS configuration
- Credentials mode requires specific CORS headers

**Impact**: Preflight requests fail or credentials are blocked

**Resolution Needed**:
- Add CORSMiddleware to FastAPI app
- Allow both localhost:3000 and Vercel production origin
- Enable credentials: `allow_credentials=True`
- Set proper allowed headers and methods

### 3. **Better Auth Not Actually Used** (HIGH CONFIDENCE)

**Problem**: Despite project description mentioning Better Auth, the codebase uses a custom authentication implementation.

**Evidence**:
- Custom auth client in src/lib/auth-client.ts
- No Better Auth configuration files found
- Custom JWT + localStorage pattern instead of Better Auth's session cookies
- FastAPI backend instead of Better Auth's expected setup

**Impact**: Mismatch between expected behavior (cookie-based sessions) and actual implementation (JWT tokens)

**Resolution Options**:
A. Acknowledge custom implementation and fix environment/CORS issues
B. Migrate to actual Better Auth setup (significant refactor)

**Recommendation**: Option A - fix current implementation while maintaining existing architecture

### 4. **Vercel SSR/SSG Compatibility** (MEDIUM CONFIDENCE)

**Problem**: Docusaurus static site generation may have issues with client-side auth during build.

**Evidence**:
- Window checks in auth-client.ts (lines 8, 41-52, 213)
- localStorage usage breaks during SSR
- useEffect dependencies for client-side initialization

**Impact**: Build-time vs runtime behavior differences

**Resolution Needed**:
- Ensure all browser APIs are guarded by typeof window checks (already done)
- Consider using clientModules in Docusaurus config
- Lazy load auth components

### 5. **Error Handling Insufficient** (LOW-MEDIUM CONFIDENCE)

**Problem**: Generic "Failed to fetch" doesn't distinguish between network, CORS, 404, 500, etc.

**Evidence**:
- Catch blocks use generic error messages
- No detailed logging of response status/headers
- Error differentiation only for 401 (unauthorized)

**Impact**: Debugging difficulty, poor user experience

**Resolution Needed**:
- Add detailed error logging
- Differentiate network errors vs HTTP errors
- Provide actionable error messages to users

## Technology Decisions

### Decision 1: Environment Configuration Strategy

**Chosen**: Use environment variables with build-time injection for static values and runtime globals for dynamic values

**Rationale**:
- Docusaurus supports environment variables via webpack
- Vercel can inject env vars at build time
- Runtime globals needed for scenarios where backend URL differs per deployment

**Implementation**:
```typescript
// Build-time: process.env.NEXT_PUBLIC_API_URL (Vercel)
// Runtime: window.__ENV__?.API_URL (fallback)
// Development: http://localhost:8000
```

**Alternatives Considered**:
- Pure runtime config: Requires additional config endpoint, delays app initialization
- Hardcoded per environment: Not maintainable, requires separate builds
- .env file only: Doesn't work for static site deployments

### Decision 2: CORS Configuration

**Chosen**: FastAPI CORSMiddleware with environment-specific allowed origins

**Rationale**:
- FastAPI standard approach
- Supports multiple origins (localhost + Vercel)
- Can be configured via environment variables

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Alternatives Considered**:
- Allow all origins (`allow_origins=["*"]`): Security risk, doesn't work with credentials
- Proxy through Docusaurus: Adds complexity, doesn't solve production issue
- API Gateway: Over-engineered for current scale

### Decision 3: Authentication Token Storage

**Chosen**: Keep current JWT + localStorage approach (do not migrate to Better Auth)

**Rationale**:
- Already implemented and working (except for URL/CORS issues)
- Migrating to Better Auth is out of scope for this bug fix
- Spec constraint: "MUST use Better Auth idiomatically" needs clarification with user

**Implementation**: Fix existing implementation
- Correct environment configuration
- Add proper CORS
- Improve error handling

**Alternatives Considered**:
- Full Better Auth migration: Too large for bug fix, breaks existing code
- HTTP-only cookies: Requires backend changes, better security but bigger scope

### Decision 4: Error Messaging Strategy

**Chosen**: Structured error responses with user-friendly messages and detailed logging

**Rationale**:
- Helps debugging
- Improves user experience
- Distinguishes error types (network, CORS, auth, server)

**Implementation**:
```typescript
class AuthError extends Error {
  type: 'network' | 'cors' | 'unauthorized' | 'server';
  statusCode?: number;
  originalError: any;
}

// User sees: "Unable to connect to authentication server"
// Console logs: Full error with type, status, headers
```

**Alternatives Considered**:
- Keep generic errors: Poor UX, hard to debug
- Expose technical details to user: Security risk, confusing
- Error monitoring service: Good long-term, but out of scope

## Research Findings Summary

### Confirmed Issues

1. ✅ **Environment URL Problem**: Production will use localhost, guaranteed failure
2. ✅ **No Better Auth**: Custom implementation despite project description
3. ✅ **JWT + localStorage**: Not cookie-based sessions as spec assumed
4. ✅ **No environment variable usage**: Reliance on window global or hardcoded values

### Needs Backend Investigation

1. ❓ **CORS Configuration**: Not examined yet in backend code
2. ❓ **Cookie Settings**: Are any cookies being set by backend?
3. ❓ **Auth Middleware**: How does backend handle auth validation?

### Architecture Clarifications Needed

1. **Better Auth Expectation**: Spec mentions Better Auth but implementation is custom
   - Resolution: Acknowledge custom implementation, update spec assumptions, or plan migration

2. **Session vs Token Strategy**: Spec assumes cookies, implementation uses localStorage
   - Resolution: Continue with current approach, update spec accordingly

## Next Steps for Planning

1. **Update Technical Context** with confirmed technology stack
2. **Design Fixes** for identified root causes:
   - Environment configuration module
   - CORS setup for backend
   - Error handling improvements
3. **Create Contracts** defining:
   - Environment variable schema
   - Error response formats
   - Configuration interfaces
4. **Update Spec Assumptions** if needed based on findings

## Dependencies for Implementation

### Frontend
- No new dependencies needed
- Use existing: TypeScript, React, Docusaurus

### Backend (requires verification)
- FastAPI (already installed)
- CORS middleware (built into FastAPI)
- python-dotenv (likely already installed)

### DevOps/Deployment
- Vercel environment variable configuration
- Local .env file for development

## Risk Assessment

**Low Risk**:
- Environment variable configuration changes
- CORS middleware addition
- Error message improvements

**Medium Risk**:
- Changes to auth-client.ts URL determination (affects all environments)
- Backend CORS configuration (could break existing integrations if any)

**High Risk**:
- Migrating to actual Better Auth (out of scope, would be separate feature)

## Conclusion

The "Failed to fetch" errors are primarily caused by:
1. **Missing environment configuration** for production deployments
2. **Likely missing or misconfigured CORS** on backend
3. **Insufficient error handling** making diagnosis difficult

These are all fixable without major architecture changes. The fixes are surgical and low-risk.

The spec's assumption about Better Auth cookies is incorrect - the project uses a custom JWT + localStorage implementation. This should be acknowledged and the plan should focus on fixing the existing architecture rather than rewriting it.
