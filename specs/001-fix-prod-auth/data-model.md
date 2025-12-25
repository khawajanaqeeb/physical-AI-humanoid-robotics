# Data Model: Authentication Environment Configuration

**Feature**: Fix Production Authentication Server Connection Failure
**Date**: 2025-12-25

## Overview

This fix does **NOT** modify database schemas or authentication logic. It only changes environment variable configuration to enable proper runtime URL resolution in production.

---

## Environment Configuration Entity

### Browser-Side Configuration (Frontend)

**Entity**: `BrowserEnvironmentConfig`

| Attribute | Type | Source | Accessibility | Purpose |
|-----------|------|--------|---------------|---------|
| `NEXT_PUBLIC_API_URL` | String (URL) | Vercel env vars | ✅ Browser-accessible | Backend API base URL |
| `window.CHATBOT_API_URL` | String (URL) | Set by docusaurus.config.ts | ✅ Browser-accessible | RAG plugin + auth components |
| `window.__ENV__.API_URL` | String (URL) | Runtime injection (unused) | ✅ Browser-accessible | Future extensibility |

**Current Problem**:
- `docusaurus.config.ts` reads `process.env.BACKEND_URL` (not browser-accessible)
- Should read `process.env.NEXT_PUBLIC_API_URL` instead
- Components use `window.CHATBOT_API_URL` which is set to undefined/fallback

**After Fix**:
- `docusaurus.config.ts` reads `process.env.NEXT_PUBLIC_API_URL` (browser-accessible)
- `window.CHATBOT_API_URL` correctly set to Railway backend URL
- Auth components receive proper backend URL

---

### Server-Side Configuration (Backend)

**Entity**: `ServerEnvironmentConfig`

| Attribute | Type | Source | Purpose |
|-----------|------|--------|---------|
| `CORS_ORIGINS` | String (comma-separated URLs) | Railway env vars | Allowed frontend origins |
| `BETTER_AUTH_SECRET` | String (64-char hex) | Railway env vars | JWT signing secret |
| `DATABASE_URL` | String (PostgreSQL URL) | Railway/Neon env vars | Database connection |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Integer | Railway env vars | JWT expiry (default: 15) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Integer | Railway env vars | Refresh token expiry (default: 7) |

**Current State**:
- `CORS_ORIGINS` may have wildcard `https://*.vercel.app` or missing explicit Vercel URL
- All other vars are correctly configured (not part of this fix)

**After Fix**:
- `CORS_ORIGINS` explicitly includes `https://physical-ai-humanoid-robotics-e3c7.vercel.app`
- Ensures CORS allows production frontend requests

---

## Authentication Request Flow

### Request Entity

**Entity**: `AuthenticationRequest`

| Attribute | Type | Description |
|-----------|------|-------------|
| `method` | Enum (POST) | HTTP method (signup, signin, signout, refresh) |
| `url` | String (URL) | Target endpoint (e.g., `${BACKEND_URL}/api/v1/auth/signin`) |
| `headers` | Object | Includes `Content-Type`, `Authorization` (if token present), `Origin` |
| `credentials` | Enum ('include') | Indicates cookies should be included (currently redundant) |
| `body` | Object | Request payload (email, password, etc.) |

**Current Problem (Production)**:
- `url` resolves to `http://localhost:8000/api/v1/auth/signin` (fallback)
- Browser blocks cross-origin request from Vercel to localhost
- Results in "Unable to connect to authentication server" error

**After Fix (Production)**:
- `url` resolves to `https://physical-ai-humanoid-robotics-production-e742.up.railway.app/api/v1/auth/signin`
- Browser makes cross-origin request from Vercel to Railway
- CORS middleware validates origin and allows request
- Auth succeeds

---

## Session Management (No Changes)

### Token Entity

**Entity**: `AuthTokens`

| Attribute | Type | Storage | Expiry |
|-----------|------|---------|--------|
| `access_token` | String (JWT) | localStorage | 15 minutes |
| `refresh_token` | String (UUID) | localStorage | 7 days |

**Flow**:
1. User signs in → Backend returns `access_token` + `refresh_token`
2. Frontend stores both in localStorage
3. All API requests include `Authorization: Bearer ${access_token}` header
4. When access token expires (401 error) → Call `/api/v1/auth/refresh` with refresh token
5. Backend validates refresh token (DB lookup) → Returns new access token
6. Frontend updates localStorage and retries original request

**Note**: This fix does NOT change token flow, storage, or validation logic.

---

## CORS Validation Entity

### Preflight Request

**Entity**: `CORSPreflightRequest`

| Attribute | Type | Value |
|-----------|------|-------|
| `method` | String | OPTIONS |
| `Origin` | String | `https://physical-ai-humanoid-robotics-e3c7.vercel.app` |
| `Access-Control-Request-Method` | String | POST (or GET, PUT, DELETE) |
| `Access-Control-Request-Headers` | String | `Content-Type, Authorization` |

**Expected Response** (after fix):
```
HTTP/2 200 OK
Access-Control-Allow-Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

**Current Problem**:
- If `CORS_ORIGINS` doesn't include exact Vercel URL, preflight fails
- Browser blocks actual auth request

**After Fix**:
- Railway `CORS_ORIGINS` includes exact Vercel URL
- Preflight succeeds → Auth requests allowed

---

## Environment Variable Resolution Logic

### Frontend URL Resolution Pseudocode

```typescript
function getBackendUrl(): string {
  // 1. Check build-time env var (Vercel)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;  // ✅ After fix: Returns Railway URL
  }

  // 2. Check runtime injection (unused but available)
  if (window.__ENV__?.API_URL) {
    return window.__ENV__.API_URL;
  }

  // 3. Fallback to localhost (development)
  return 'http://localhost:8000';  // ✅ Safe fallback for dev
}
```

**Before Fix**:
- Production: `process.env.NEXT_PUBLIC_API_URL` is undefined (docusaurus.config.ts reads wrong var)
- Falls back to localhost → Connection fails

**After Fix**:
- Production: `process.env.NEXT_PUBLIC_API_URL` is set → Returns Railway URL
- No fallback needed → Connection succeeds

---

## Database Schema (No Changes)

**Tables Involved** (not modified by this fix):
- `users` - User accounts (id, username, email, password_hash, created_at, updated_at)
- `user_profiles` - User profiles (user_id FK, software_experience, hardware_experience, interests, created_at, updated_at)
- `refresh_tokens` - Active refresh tokens (id, user_id FK, token UUID, expires_at, created_at)

**Note**: This fix is configuration-only. No migrations, schema changes, or data modifications.

---

## Summary

**Entity Changes**: None (config-only fix)
**Data Flow Changes**: None (auth logic unchanged)
**Environment Config Changes**:
- ✅ Frontend: Use `NEXT_PUBLIC_API_URL` instead of `BACKEND_URL`
- ✅ Backend: Ensure `CORS_ORIGINS` includes exact Vercel URL

**Result**: Production auth requests route to Railway backend instead of falling back to localhost.
