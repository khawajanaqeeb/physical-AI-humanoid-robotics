# Environment Variable Contracts

**Feature**: Fix Production Authentication Server Connection Failure
**Date**: 2025-12-25

---

## Frontend (Vercel)

### NEXT_PUBLIC_API_URL

**Type**: String (URL)
**Required**: Yes (production), No (development - has fallback)
**Format**: `https://hostname.domain.tld` (no trailing slash)
**Example**: `https://physical-ai-humanoid-robotics-production-e742.up.railway.app`
**Fallback**: `http://localhost:8000` (development only)
**Deployment Contexts**:
- ✅ Production (required)
- ✅ Preview (recommended, can use same backend)
- ⚪ Development (optional, falls back to localhost)

**Validation**:
- Must be valid HTTPS URL in production
- Should not include trailing slash
- Should be Railway backend URL

**How to Set**:
1. Vercel Dashboard → Project → Settings → Environment Variables
2. Add variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://physical-ai-humanoid-robotics-production-e742.up.railway.app`
   - Contexts: Production ✅, Preview ✅, Development ✅
3. Redeploy after setting (Vercel doesn't auto-rebuild on env change)

**Used By**:
- `docusaurus.config.ts` (sets `window.CHATBOT_API_URL`)
- `src/lib/auth-client.ts` (direct usage)
- All auth components (indirect via `window.CHATBOT_API_URL`)

---

## Backend (Railway)

### CORS_ORIGINS

**Type**: String (comma-separated URLs)
**Required**: Yes
**Format**: `https://url1,https://url2,http://localhost:3000` (NO SPACES between URLs)
**Example**: `https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000`
**Validation**:
- Must include exact Vercel production URL
- Should include localhost for development
- No wildcards with credentials (security risk)
- No spaces between URLs (parser strips whitespace but explicit format is clearer)

**How to Set**:
1. Railway Dashboard → Project → Variables
2. Add/Update variable:
   - Name: `CORS_ORIGINS`
   - Value: `https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000`
3. Railway auto-restarts service on variable change (~30s)

**Used By**:
- `backend/src/core/config.py` (parses into list)
- `backend/src/main.py` (CORS middleware configuration)

**Test Command**:
```bash
curl -I -X OPTIONS \
  -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  https://physical-ai-humanoid-robotics-production-e742.up.railway.app/api/v1/auth/signin
```

**Expected Response**:
```
HTTP/2 200 OK
access-control-allow-origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app
access-control-allow-credentials: true
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
access-control-allow-headers: *
```

---

### BETTER_AUTH_SECRET

**Type**: String (hexadecimal)
**Required**: Yes
**Format**: 64-character hexadecimal string
**Example**: `a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456`
**Purpose**: JWT signing secret (NOTE: Despite name, NOT using Better Auth library - this is custom JWT implementation)
**Security**: Must be kept secret, never commit to git

**How to Generate**:
```bash
# Generate secure 64-char hex string
openssl rand -hex 32
```

**How to Set**:
- Railway Dashboard → Variables → Add `BETTER_AUTH_SECRET`
- Value: Output from openssl command above

**Used By**:
- `backend/src/auth/security.py` (JWT token creation/validation)

**Note**: This fix does NOT require changing this variable (already set in Railway).

---

### DATABASE_URL

**Type**: String (PostgreSQL connection string)
**Required**: Yes
**Format**: `postgresql+psycopg://user:password@hostname:5432/database`
**Example**: `postgresql+psycopg://myuser:mypass@myhost.neon.tech:5432/mydb`
**Provider**: Neon PostgreSQL

**How to Get**:
1. Neon Dashboard → Project → Connection String
2. Copy connection string with `psycopg` driver

**How to Set**:
- Railway Dashboard → Variables → Add `DATABASE_URL`
- Value: Neon connection string

**Used By**:
- `backend/src/core/database.py` (SQLAlchemy engine creation)

**Note**: This fix does NOT require changing this variable.

---

### ACCESS_TOKEN_EXPIRE_MINUTES

**Type**: Integer
**Required**: No (has default)
**Default**: `15`
**Format**: Positive integer (minutes)
**Purpose**: JWT access token expiration time

**How to Set** (optional):
- Railway Dashboard → Variables → Add `ACCESS_TOKEN_EXPIRE_MINUTES`
- Value: Integer (e.g., `15`, `30`, `60`)

**Note**: This fix does NOT require changing this variable.

---

### REFRESH_TOKEN_EXPIRE_DAYS

**Type**: Integer
**Required**: No (has default)
**Default**: `7`
**Format**: Positive integer (days)
**Purpose**: Refresh token expiration time

**How to Set** (optional):
- Railway Dashboard → Variables → Add `REFRESH_TOKEN_EXPIRE_DAYS`
- Value: Integer (e.g., `7`, `14`, `30`)

**Note**: This fix does NOT require changing this variable.

---

## Legacy/Deprecated Variables

### BACKEND_URL (Frontend)

**Status**: ⚠️ Deprecated
**Problem**: Not accessible in browser on Vercel (missing `NEXT_PUBLIC_` prefix)
**Replacement**: `NEXT_PUBLIC_API_URL`
**Action**: Remove references from code (optional cleanup)

**Currently Used In** (should be updated):
- `docusaurus.config.ts:193` (PRIMARY FIX LOCATION)
- `src/components/auth/UserContext.tsx:101` (optional cleanup)
- `src/components/auth/Profile.tsx:85` (optional cleanup)

---

## Deployment Checklist

### Pre-Deployment

- [ ] Verify `.env.example` documents `NEXT_PUBLIC_API_URL`
- [ ] Verify Railway has all required env vars set
- [ ] Test localhost with unset `NEXT_PUBLIC_API_URL` (should fallback to localhost:8000)

### Vercel Setup

- [ ] Set `NEXT_PUBLIC_API_URL` in Production context
- [ ] Set `NEXT_PUBLIC_API_URL` in Preview context (recommended)
- [ ] Redeploy after setting variable

### Railway Setup

- [ ] Update `CORS_ORIGINS` to include exact Vercel URL
- [ ] Wait for automatic service restart (~30s)
- [ ] Test CORS with curl command (see above)

### Post-Deployment Verification

- [ ] Browser console: Check `process.env.NEXT_PUBLIC_API_URL` resolves to Railway URL
- [ ] Browser console: Check `window.CHATBOT_API_URL` resolves to Railway URL
- [ ] Network tab: Verify auth requests target Railway (not localhost)
- [ ] Railway logs: Confirm incoming requests from Vercel IP
- [ ] Test full auth cycle: signup → login → logout

---

## Troubleshooting

**Problem**: "Unable to connect to authentication server" persists after fix

**Check**:
1. Vercel env var is actually set (Settings → Environment Variables)
2. Vercel deployment happened AFTER env var was set (redeploy if needed)
3. Browser console shows correct `NEXT_PUBLIC_API_URL` value
4. Railway `CORS_ORIGINS` includes exact Vercel URL (no typos)
5. Railway service restarted after CORS change

**Verify URL Resolution**:
```javascript
// In browser console on Vercel production
console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('CHATBOT_API_URL:', window.CHATBOT_API_URL);
```

**Verify CORS**:
```bash
# From terminal
curl -I -X OPTIONS \
  -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" \
  https://physical-ai-humanoid-robotics-production-e742.up.railway.app/api/v1/auth/signin | grep -i access-control
```

Should see:
```
access-control-allow-origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app
access-control-allow-credentials: true
```
