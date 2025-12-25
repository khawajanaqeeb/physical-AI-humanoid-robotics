# Pull Request: Fix production authentication server connection failure

## Summary

Fixes production-only authentication server connection failure on Vercel deployment with Railway backend.

**Root Cause**: `docusaurus.config.ts` was using `process.env.BACKEND_URL` which is not accessible in browser on Vercel (missing `NEXT_PUBLIC_` prefix). This caused all auth requests to fall back to `http://localhost:8000` in production, resulting in "Unable to connect to authentication server" errors.

**Solution**: Changed to `process.env.NEXT_PUBLIC_API_URL` - a Vercel-compatible environment variable that is accessible in browser code.

## Changes

### Code Changes (1 file, 1 line)
- **docusaurus.config.ts:193**: Changed `process.env.BACKEND_URL` to `process.env.NEXT_PUBLIC_API_URL`
- Preserved fallback to `http://localhost:8000` for development environment

### Environment Configuration Required

**Vercel** (must be set for fix to work):
```
NEXT_PUBLIC_API_URL=https://physical-ai-humanoid-robotics-production-e742.up.railway.app
```
- Set in: Production, Preview, Development contexts
- **Must redeploy after setting**

**Railway** (recommended):
```
CORS_ORIGINS=https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000
```

## Testing

### Automated Testing
- ✅ Railway backend verified accessible
- ✅ Code change verified (grep confirms NEXT_PUBLIC_API_URL on line 193)
- ✅ Fallback to localhost preserved
- ✅ Localhost development environment unaffected

### Manual Testing Required

**User Story 1 - New User Registration (P1)**:
- [ ] Navigate to signup page on Vercel production
- [ ] Test signup with valid credentials
- [ ] Verify Network tab shows request to Railway backend (not localhost)
- [ ] Verify signup returns 200/201 status (not CORS error)
- [ ] Verify user account created successfully

**User Story 2 - Existing User Login (P1)**:
- [ ] Test login with registered credentials
- [ ] Verify logged-in state appears
- [ ] Verify session persists across page refreshes

**User Story 3 - User Logout (P2)**:
- [ ] Click logout button
- [ ] Verify UI updates to logged-out state

## Success Criteria (from spec.md)

- [ ] SC-001: Users can successfully complete signup on Vercel production in under 10 seconds
- [ ] SC-002: Users can successfully login on Vercel production in under 5 seconds
- [ ] SC-003: Authenticated users can successfully logout on Vercel production with immediate UI state update
- [ ] SC-004: Zero "Unable to connect to authentication server" errors occur during normal authentication flows
- [ ] SC-005: 100% of authentication requests from Vercel production successfully reach the Railway backend
- [ ] SC-006: Localhost development environment continues to function identically to pre-fix behavior
- [ ] SC-007: All CORS preflight requests complete successfully with appropriate headers
- [ ] SC-008: Session persistence works across page refreshes and navigation on Vercel production

## Deployment Instructions

1. **Merge this PR** (code change only)
2. **Set Vercel environment variable**:
   - Dashboard → Settings → Environment Variables
   - Add `NEXT_PUBLIC_API_URL` with Railway backend URL
   - **CRITICAL**: Redeploy after setting variable
3. **Update Railway CORS** (optional but recommended):
   - Dashboard → Variables
   - Update `CORS_ORIGINS` to include exact Vercel URL
4. **Test on production** using manual testing checklist above

## Rollback Plan

If issues occur:
1. Revert this PR (1 commit)
2. Remove `NEXT_PUBLIC_API_URL` from Vercel
3. Redeploy
4. Recovery time: < 5 minutes

## Related Documentation

- Feature Spec: `specs/001-fix-prod-auth/spec.md`
- Implementation Plan: `specs/001-fix-prod-auth/plan.md`
- Root Cause Analysis: `specs/001-fix-prod-auth/research.md`
- Quickstart Guide: `specs/001-fix-prod-auth/quickstart.md`
- Task List: `specs/001-fix-prod-auth/tasks.md`

## Impact

- **Risk**: Minimal (configuration-only, 1 line change)
- **Complexity**: Very Low
- **Rollback**: Trivial (git revert)
- **Breaking Changes**: None (backward compatible via fallback)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
