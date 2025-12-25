# Quickstart: Fix Production Authentication

**Feature**: Fix Production Authentication Server Connection Failure
**Estimated Time**: 15 minutes
**Difficulty**: Low (configuration-only)

---

## TL;DR - The Fix

1. **Code Change** (1 line):
   - File: `docusaurus.config.ts` line 193
   - Change: `BACKEND_URL` → `NEXT_PUBLIC_API_URL`

2. **Vercel Environment Variable**:
   - Set: `NEXT_PUBLIC_API_URL=https://physical-ai-humanoid-robotics-production-e742.up.railway.app`
   - Redeploy after setting

3. **Railway Environment Variable**:
   - Set: `CORS_ORIGINS=https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000`

4. **Test**: Signup on Vercel production → Should work ✅

---

## Detailed Steps

### Step 1: Update Code (Local)

**File**: `docusaurus.config.ts`
**Location**: Repository root
**Line**: 193

**Current**:
```typescript
backendUrl: process.env.BACKEND_URL || 'http://localhost:8000',
```

**New**:
```typescript
backendUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
```

**How to Edit**:
```bash
# Open file in editor
# Find line 193 (search for "backendUrl: process.env")
# Replace BACKEND_URL with NEXT_PUBLIC_API_URL
# Save file
```

---

### Step 2: Test Localhost (Critical)

**Verify no regression before deploying**:

```bash
# Ensure .env does NOT have NEXT_PUBLIC_API_URL set (or set to localhost)
cat .env | grep NEXT_PUBLIC_API_URL
# Should be empty or: NEXT_PUBLIC_API_URL=http://localhost:8000

# Start dev server
npm start

# Open browser: http://localhost:3000
# Navigate to auth demo page
# Test signup, login, logout
# All should work (using localhost:8000 backend)
```

**Expected**: Auth works on localhost (fallback to localhost:8000) ✅

---

### Step 3: Set Vercel Environment Variable

**Location**: [Vercel Dashboard](https://vercel.com/dashboard) → Your Project → Settings → Environment Variables

**Steps**:
1. Click "Add Variable"
2. **Name**: `NEXT_PUBLIC_API_URL`
3. **Value**: `https://physical-ai-humanoid-robotics-production-e742.up.railway.app`
4. **Environments**: Check all three:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
5. Click "Save"

**IMPORTANT**: Vercel does NOT auto-rebuild when you change environment variables. You must manually redeploy.

---

### Step 4: Redeploy on Vercel

**Option A: Via Dashboard**:
1. Navigate to Deployments tab
2. Find latest deployment
3. Click "..." menu → "Redeploy"
4. Click "Redeploy" button

**Option B: Via Git Push**:
```bash
git add docusaurus.config.ts
git commit -m "fix(auth): use NEXT_PUBLIC_API_URL for production compatibility"
git push origin 001-fix-prod-auth
# Vercel auto-deploys on push
```

**Wait**: ~2-3 minutes for deployment to complete

---

### Step 5: Set Railway Environment Variable

**Location**: [Railway Dashboard](https://railway.app/dashboard) → Your Project → Variables tab

**Steps**:
1. Find or add variable: `CORS_ORIGINS`
2. **Value**: `https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000`
   - ⚠️ **No spaces** between URLs
   - Include exact Vercel production URL
   - Include localhost for development
3. Click "Save" or "Add"

**Auto-Restart**: Railway automatically restarts your service when you change variables (~30 seconds)

**Wait**: 30 seconds for service restart

---

### Step 6: Verify CORS (Optional but Recommended)

**Test CORS with curl**:
```bash
curl -I -X OPTIONS \
  -H "Origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  https://physical-ai-humanoid-robotics-production-e742.up.railway.app/api/v1/auth/signin
```

**Expected Response** (look for these headers):
```
HTTP/2 200 OK
access-control-allow-origin: https://physical-ai-humanoid-robotics-e3c7.vercel.app
access-control-allow-credentials: true
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS
access-control-allow-headers: *
```

**If headers missing**: Check Railway `CORS_ORIGINS` variable, ensure no typos

---

### Step 7: Test on Vercel Production

**Navigate**: https://physical-ai-humanoid-robotics-e3c7.vercel.app

**Open Browser DevTools**:
1. Press F12 (or right-click → Inspect)
2. Go to **Network** tab
3. Clear network log (trash icon)

**Test Signup**:
1. Navigate to signup page (or auth demo page)
2. Fill signup form with test credentials:
   - Email: `test@example.com`
   - Password: `testpass123`
3. Click "Sign Up"

**Verify in Network Tab**:
- Look for request to: `https://physical-ai-humanoid-robotics-production-e742.up.railway.app/api/v1/auth/signup`
- **NOT**: `http://localhost:8000/api/v1/auth/signup`
- Status should be: `200 OK` or `201 Created`
- Response should include `access_token` and `refresh_token`

**Test Login**:
1. Navigate to login page
2. Enter same credentials
3. Click "Log In"
4. Verify request goes to Railway backend (Network tab)
5. Should see logged-in state (navbar updates)

**Test Logout**:
1. Click logout button in navbar
2. Verify UI updates (logged-out state)

**Success**: All three flows work without "Unable to connect to authentication server" error ✅

---

### Step 8: Verify Browser Console (Debugging)

**If auth still fails**, check browser console:

```javascript
// In browser console (F12 → Console tab)
console.log('NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
console.log('CHATBOT_API_URL:', window.CHATBOT_API_URL);
```

**Expected Output**:
```
NEXT_PUBLIC_API_URL: "https://physical-ai-humanoid-robotics-production-e742.up.railway.app"
CHATBOT_API_URL: "https://physical-ai-humanoid-robotics-production-e742.up.railway.app"
```

**If showing `undefined` or `localhost`**:
- Vercel env var not set correctly → Go back to Step 3
- Vercel not redeployed after setting var → Go back to Step 4

---

## Troubleshooting

### Problem: Auth Still Fails

**Checklist**:
- [ ] Vercel has `NEXT_PUBLIC_API_URL` set in Production environment
- [ ] Vercel was redeployed AFTER env var was set
- [ ] Railway has `CORS_ORIGINS` with exact Vercel URL (no typo)
- [ ] Railway service restarted (check Deployments → Logs)
- [ ] Browser console shows correct Railway URL (not localhost)

**Common Mistakes**:
1. **Forgot to redeploy Vercel** → Env var exists but not in build
2. **Typo in CORS_ORIGINS** → Check exact Vercel URL
3. **Spaces in CORS_ORIGINS** → Use `url1,url2` not `url1, url2`
4. **Wrong deployment context** → Set var in Production, not just Development

---

### Problem: Localhost Broken

**Check**:
- `.env` should NOT have `NEXT_PUBLIC_API_URL` set (or set to `http://localhost:8000`)
- Fallback `|| 'http://localhost:8000'` should still be in code
- Restart dev server: `npm start`

**Verify**:
```bash
# Should show empty or localhost:8000
cat .env | grep NEXT_PUBLIC_API_URL
```

---

### Problem: CORS Errors in Browser

**Symptoms**:
- Network tab shows: "has been blocked by CORS policy"
- Request reaches Railway but returns error

**Fix**:
1. Verify Railway `CORS_ORIGINS` includes exact Vercel URL
2. Test with curl (Step 6)
3. Check Railway logs for CORS-related errors
4. Ensure `CORS_ORIGINS` has no trailing slashes in URLs

---

## Rollback Procedure

**If fix doesn't work or breaks something**:

1. **Revert Code**:
   ```bash
   git revert HEAD
   git push origin 001-fix-prod-auth
   # Vercel auto-deploys revert
   ```

2. **Remove Vercel Env Var** (optional):
   - Vercel Dashboard → Environment Variables → Delete `NEXT_PUBLIC_API_URL`

3. **Keep Railway CORS** (safe to keep):
   - Railway CORS change is non-breaking
   - Can leave `CORS_ORIGINS` as-is

**Recovery Time**: 2 minutes

---

## Success Criteria

### Must Pass (from spec.md)

- [ ] **SC-001**: Signup completes in < 10 seconds
- [ ] **SC-002**: Login completes in < 5 seconds
- [ ] **SC-003**: Logout updates UI immediately
- [ ] **SC-004**: Zero "Unable to connect to authentication server" errors
- [ ] **SC-005**: Railway logs show requests from Vercel IP
- [ ] **SC-006**: Localhost still works (verify after production fix)
- [ ] **SC-007**: Browser Network tab shows 200 OK for OPTIONS preflight
- [ ] **SC-008**: Session persists after page refresh

---

## Next Steps After Fix

1. **Monitor**: Check Railway logs for any auth errors
2. **Clean Up** (optional): Remove `process.env.BACKEND_URL` references in other components
3. **Document**: Update README with correct env var usage
4. **Close Issue**: Mark feature as complete, archive planning docs

---

## Quick Reference

| Platform | Variable | Value |
|----------|----------|-------|
| **Vercel** | `NEXT_PUBLIC_API_URL` | `https://physical-ai-humanoid-robotics-production-e742.up.railway.app` |
| **Railway** | `CORS_ORIGINS` | `https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000` |

**Code Change**: `docusaurus.config.ts:193` → `BACKEND_URL` to `NEXT_PUBLIC_API_URL`

**Test URL**: https://physical-ai-humanoid-robotics-e3c7.vercel.app
