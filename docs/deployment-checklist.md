# Production Deployment Checklist

**Last Updated**: 2025-12-23
**Purpose**: Ensure smooth deployment of the Physical AI & Humanoid Robotics platform to production

---

## Prerequisites

- [ ] Access to Vercel dashboard (frontend deployment)
- [ ] Access to Railway dashboard (backend deployment)
- [ ] PostgreSQL database on Neon (already configured)
- [ ] Cohere API key (for RAG chatbot)
- [ ] Qdrant Cloud cluster (for vector database)

---

## Backend Deployment (Railway)

### 1. Environment Variables Configuration

Ensure the following environment variables are set in Railway Dashboard → Variables:

| Variable | Required | Example Value | Notes |
|----------|----------|---------------|-------|
| `DATABASE_URL` | ✅ | `postgresql+psycopg://user:pass@host/db` | From Neon dashboard |
| `BETTER_AUTH_SECRET` | ✅ | `64-char-hex-string` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `COHERE_API_KEY` | ✅ | `your-cohere-api-key` | From Cohere dashboard |
| `QDRANT_URL` | ✅ | `https://cluster.qdrant.io` | From Qdrant Cloud |
| `QDRANT_API_KEY` | ✅ | `your-qdrant-api-key` | From Qdrant Cloud |
| `QDRANT_COLLECTION_NAME` | ✅ | `textbook_chunks` | Collection name |
| `CORS_ORIGINS` | ✅ | `https://your-app.vercel.app,http://localhost:3000` | **CRITICAL for auth** |
| `TEXTBOOK_SITEMAP_URL` | ✅ | `https://your-app.vercel.app/sitemap.xml` | Vercel deployment URL |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ⚠️ | `15` | Optional, defaults to 15 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | ⚠️ | `7` | Optional, defaults to 7 |
| `API_KEY` | ⚠️ | `secure-token` | Optional, for /ingest protection |

### 2. CORS Configuration (Critical!)

**Problem**: Frontend cannot authenticate if CORS is not configured correctly.

**Solution**:
```bash
# In Railway Variables tab, set CORS_ORIGINS to:
CORS_ORIGINS=https://your-vercel-deployment.vercel.app,http://localhost:3000
```

**Important Notes**:
- NO SPACES between domains (comma-separated only)
- Must include BOTH production Vercel URL AND localhost for development
- Use exact domain (including https/http protocol)
- Railway auto-redeploys when env vars change

### 3. Verify Deployment

- [ ] Railway build completes successfully
- [ ] Backend health check responds: `curl https://your-railway-url.railway.app/health`
- [ ] Database migrations run automatically (check Railway logs)
- [ ] No errors in Railway deployment logs

### 4. Get Backend URL

After deployment, copy the public Railway URL:
1. Railway Dashboard → Your Service → Settings → Domains
2. Copy the Railway-provided domain (e.g., `https://your-app.up.railway.app`)
3. **You'll need this for Vercel configuration below**

---

## Frontend Deployment (Vercel)

### 1. Environment Variables Configuration

Set this in Vercel Dashboard → Project Settings → Environment Variables:

| Variable | Required | Value | Apply To |
|----------|----------|-------|----------|
| `NEXT_PUBLIC_API_URL` | ✅ | `https://your-railway-url.railway.app` | Production, Preview, Development |

**Important**:
- Must be prefixed with `NEXT_PUBLIC_` to be available in the browser
- Value should be your Railway backend URL from the previous step
- Apply to all environments (Production, Preview, Development)

### 2. Trigger Redeploy

After adding environment variables:
1. Go to Vercel Dashboard → Deployments tab
2. Click "Redeploy" on the latest deployment
3. Select "Use existing Build Cache" = NO (to pick up new env vars)
4. Wait for build to complete

### 3. Verify Deployment

- [ ] Vercel build completes successfully
- [ ] No build errors in Vercel logs
- [ ] Environment variables appear in build logs (check for `NEXT_PUBLIC_API_URL`)

---

## Production Validation

### 1. Authentication Flow Testing

Visit your production site and test with browser DevTools open (F12):

**Desktop Testing**:
- [ ] Sign up with new account
  - Check Network tab: requests go to Railway URL (not localhost)
  - Check Console: no connection errors
  - Check Application → Local Storage: `access_token` and `refresh_token` stored
  - Timing: < 3 seconds
- [ ] Sign in with existing account
  - Verify successful authentication
  - Check tokens in localStorage
  - Timing: < 2 seconds
- [ ] Session persistence
  - Refresh page
  - Verify still authenticated (no re-login required)
  - Timing: < 1 second
- [ ] Sign out
  - Verify localStorage cleared
  - Verify redirected to login

**Mobile Testing** (use device or Chrome DevTools emulation):
- [ ] Repeat all desktop tests on mobile device
- [ ] Test both portrait and landscape orientations

### 2. CORS Validation

Open browser Console and Network tabs:
- [ ] Zero CORS errors in Console
- [ ] Network tab shows CORS headers in responses:
  - `Access-Control-Allow-Origin: https://your-vercel-url`
  - `Access-Control-Allow-Credentials: true`
- [ ] OPTIONS preflight requests return 200 OK
- [ ] OPTIONS response time < 200ms

### 3. Security Validation

Check DevTools → Application tab:
- [ ] Tokens stored in localStorage (not cookies)
- [ ] Network tab shows Authorization headers: `Bearer <token>`
- [ ] All requests use HTTPS (no http:// URLs)
- [ ] Test token refresh mechanism (wait 15+ minutes, make request)

### 4. Error Handling

Test error scenarios:
- [ ] Invalid credentials → proper error message
- [ ] Weak password → validation error
- [ ] Missing email → validation error
- [ ] Non-existent account → proper error
- [ ] Backend unreachable → user-friendly error (stop Railway service temporarily)

### 5. Cross-Browser Testing

- [ ] Chrome (desktop)
- [ ] Firefox (desktop)
- [ ] Safari (desktop)
- [ ] Mobile Chrome
- [ ] Mobile Safari

### 6. Performance Validation

Measure timing (Network tab):
- [ ] Sign-up: < 2 seconds
- [ ] Sign-in: < 2 seconds
- [ ] Session check: < 1 second
- [ ] CORS preflight: < 200ms

---

## Troubleshooting

### Issue: "Failed to fetch" or "Unable to connect to authentication server"

**Diagnosis**:
1. Open DevTools → Network tab
2. Look at failed request URL
3. If URL is `http://localhost:8000/...` → Frontend env var not set

**Solution**:
```bash
# In Vercel Dashboard → Environment Variables:
NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
```
Then redeploy frontend.

---

### Issue: CORS errors in browser console

**Error example**:
```
Access to fetch at 'https://backend.railway.app/api/v1/auth/signup'
from origin 'https://frontend.vercel.app' has been blocked by CORS policy
```

**Diagnosis**:
1. Check Railway Variables → `CORS_ORIGINS`
2. Verify exact Vercel URL is included

**Solution**:
```bash
# In Railway Dashboard → Variables:
CORS_ORIGINS=https://your-exact-vercel-url.vercel.app,http://localhost:3000
```
Railway will auto-redeploy. Wait 2-3 minutes.

**Common mistakes**:
- ❌ Spaces between domains: `https://app.com, http://localhost`
- ❌ Missing protocol: `app.vercel.app` (should be `https://app.vercel.app`)
- ❌ Wildcard in production: `https://*.vercel.app` (use exact domain)
- ❌ Trailing slash: `https://app.vercel.app/` (remove trailing slash)

---

### Issue: Authentication works on desktop but fails on mobile

**Diagnosis**:
1. Check if mobile browser blocks third-party cookies
2. Verify token-based auth is used (not cookies)

**Solution**:
- Current implementation uses localStorage + Bearer tokens (should work)
- If using cookies: ensure `SameSite=None; Secure` attributes set

---

### Issue: Localhost development broken after production config

**Diagnosis**:
1. Check if `NEXT_PUBLIC_API_URL` is set in local `.env` file
2. Should NOT be set locally (let it fall back to localhost)

**Solution**:
```bash
# In local .env file (do NOT commit):
# NEXT_PUBLIC_API_URL should NOT be set
# auth-client.ts will fallback to http://localhost:8000
```

---

### Issue: 500 Internal Server Error from backend

**Diagnosis**:
1. Check Railway logs (Dashboard → Logs tab)
2. Look for Python exceptions

**Common causes**:
- Database connection failed (check `DATABASE_URL`)
- Missing `BETTER_AUTH_SECRET`
- Cohere/Qdrant API keys invalid

**Solution**:
1. Verify all required env vars set
2. Check Railway logs for specific error
3. Verify database is accessible from Railway

---

## Post-Deployment Monitoring

### Railway Logs
```bash
# Monitor backend logs in real-time:
# Railway Dashboard → Your Service → Logs tab
```

Watch for:
- Authentication requests (`POST /api/v1/auth/signup`, `POST /api/v1/auth/signin`)
- CORS preflight (`OPTIONS` requests)
- Database connection errors
- Token validation errors

### Vercel Logs
```bash
# Monitor frontend build and runtime logs:
# Vercel Dashboard → Deployments → Click deployment → Logs
```

Watch for:
- Environment variable usage during build
- Client-side errors (if real-time logging configured)

---

## Rollback Procedures

### If frontend breaks:
1. Vercel Dashboard → Deployments
2. Find last working deployment
3. Click "..." → Promote to Production

### If backend breaks:
1. Railway Dashboard → Deployments tab
2. Click "..." on last working deployment
3. Select "Redeploy"

### If env var issues:
1. Revert env var to previous value
2. Wait for auto-redeploy (Railway) or trigger manual redeploy (Vercel)

---

## Success Criteria Validation

Before marking deployment complete, verify all success criteria from spec:

- [ ] **SC-001**: Users can authenticate within 3 seconds ✅
- [ ] **SC-002**: 100% of auth attempts receive proper response ✅
- [ ] **SC-003**: Zero CORS errors in browser console ✅
- [ ] **SC-004**: Requests routed to production backend (not localhost) ✅
- [ ] **SC-005**: Works on both mobile and desktop ✅
- [ ] **SC-006**: Tokens/cookies have proper security attributes ✅

---

## Quick Reference

**Frontend (Vercel)**:
- URL: `https://physical-ai-humanoid-robotics-e3c7.vercel.app`
- Env var: `NEXT_PUBLIC_API_URL=<railway-backend-url>`

**Backend (Railway)**:
- URL: `https://<your-service>.up.railway.app`
- Env vars: `CORS_ORIGINS`, `DATABASE_URL`, `BETTER_AUTH_SECRET`, etc.

**Code locations**:
- Frontend auth logic: `src/lib/auth-client.ts:76-92`
- Backend CORS: `backend/src/main.py:68-74`
- Backend config: `backend/src/core/config.py:92-96`

---

## Notes

- All environment variables should be set via dashboard (never hardcoded)
- `.env.example` files document required variables but are not deployed
- Railway auto-redeploys on env var changes (2-3 min)
- Vercel requires manual redeploy to pick up new env vars
- Always test in production after deployment changes
