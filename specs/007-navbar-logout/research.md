# Research: Navbar Logout Button Integration

**Feature**: 007-navbar-logout
**Date**: 2025-12-23
**Purpose**: Research Docusaurus navbar patterns, React state management, and Better Auth integration patterns to inform implementation approach

## Research Questions

### Q1: What are the Docusaurus best practices for custom navbar items?

**Decision**: Use custom navbar item component with `@theme/NavbarItem` pattern

**Rationale**:
- Docusaurus 3.9.2 supports custom navbar items via the `type: 'custom-{ComponentName}'` syntax in `docusaurus.config.ts`
- The existing codebase already uses this pattern: `type: 'custom-LoginLogoutNavbarItem'` registered in `docusaurus.config.ts:88-90`
- Custom components are placed in `src/theme/NavbarItem/{ComponentName}.tsx` and registered in `src/theme/NavbarItem/ComponentTypes.tsx`
- This avoids swizzling core Docusaurus components, which is more maintainable and upgrade-friendly

**Alternatives Considered**:
1. **Swizzle `@theme/Navbar`**: More invasive, harder to maintain across Docusaurus upgrades, violates minimal change principle
2. **Inject via plugin**: Overcomplicated for a simple UI fix, adds unnecessary abstraction
3. **Use standard navbar items**: Cannot achieve custom auth-aware rendering logic needed for conditional display

**Supporting Evidence**: Existing code at `src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx:1-86` and `docusaurus.config.ts:88-90`

---

### Q2: How should the logout button be positioned beside the email in the navbar?

**Decision**: Replace dropdown pattern with side-by-side layout using Docusaurus navbar classes

**Rationale**:
- Current implementation (lines 43-73 of CustomLoginLogoutNavbarItem.tsx) uses a dropdown with email as button text and logout hidden in menu
- Spec requirement (FR-001, FR-003) explicitly states logout button must be "adjacent to" and "beside" email, not hidden
- Docusaurus navbar uses flexbox layout - items placed in same `navbar__item` container will naturally flow horizontally
- Can use `navbar__link` class for both email display and logout button for consistent styling

**Implementation Pattern**:
```tsx
// Instead of:
<div className="navbar__item dropdown">
  <button>{user.email}</button>
  <ul className="dropdown__menu">
    <li><button onClick={logout}>Logout</button></li>
  </ul>
</div>

// Use:
<div className="navbar__item">
  <span className="navbar__link">{user.email}</span>
  <button
    className="navbar__link button button--secondary button--sm"
    onClick={handleLogout}
  >
    Logout
  </button>
</div>
```

**Alternatives Considered**:
1. **Keep dropdown, just make it visible by default**: Still hides logout behind interaction, violates spec
2. **Use custom CSS grid/flexbox**: Unnecessary when Docusaurus classes already provide needed layout
3. **Create separate navbar items**: Would require modifying `docusaurus.config.ts` and managing state across components

---

### Q3: How should the component reactively update on auth state changes?

**Decision**: Continue using existing AuthContext + useAuth hook pattern

**Rationale**:
- Existing `AuthContext.tsx` (lines 1-119) already provides reactive auth state via `useAuth()` hook
- Hook exposes `user`, `isAuthenticated`, `isLoading`, and `signout` - exactly what navbar component needs
- React will automatically re-render CustomLoginLogoutNavbarItem when AuthContext state changes (login/logout/session refresh)
- Pattern already proven to work for current email display functionality

**Key Dependencies**:
- `AuthContext.tsx` (src/components/auth) provides centralized state
- `auth-client.ts` (src/lib) handles API calls and localStorage
- `signout()` method (AuthContext.tsx:95-98) already calls API and clears local state

**State Update Flow**:
1. User clicks logout button → calls `signout()` from useAuth
2. `signout()` calls `signoutMutation()` → `authApi.signout()` in auth-client.ts
3. API call to backend `/api/v1/auth/signout`, localStorage cleared
4. `setUser(null)` updates AuthContext state
5. CustomLoginLogoutNavbarItem re-renders, shows Login button instead of email+logout

**Alternatives Considered**:
1. **Local component state**: Would break on page refresh, violates existing architecture
2. **Better Auth native hooks**: Project uses custom FastAPI backend, not Better Auth's built-in backend
3. **Manual event listeners**: Overcomplicated, React context already provides reactivity

---

### Q4: What error handling is needed for logout failures?

**Decision**: Graceful degradation - clear local state even if API call fails

**Rationale**:
- Current `authApi.signout()` (auth-client.ts:101-120) already implements this pattern with try/catch
- Even if backend signout fails (network error, server down), frontend must clear tokens to prevent UX confusion
- Worst case: backend session remains active but user is logged out on frontend - next page load will re-authenticate or show login
- Console warning logged for debugging (line 113) but user flow continues

**Edge Cases to Handle**:
1. **Network failure during logout**: Clear localStorage, redirect to home (FR-006)
2. **Session already expired**: Same flow - localStorage already cleared by refresh token logic
3. **Multi-tab logout**: LocalStorage changes propagate to other tabs naturally (browser behavior)
4. **Logout during RAG chatbot use**: RAG chatbot has its own auth checks (per spec - not modified)

**No Additional Error Handling Needed**: Existing implementation is sufficient

---

### Q5: What accessibility considerations apply?

**Decision**: Ensure logout button has proper ARIA labels and keyboard navigation

**Rationale**:
- Docusaurus navbar is already keyboard-navigable (Tab key focuses navbar items)
- Button elements have native keyboard support (Enter/Space to activate)
- Should add `aria-label` to logout button for screen readers
- Current email dropdown uses `aria-expanded` and `aria-haspopup` (lines 47-48) - not needed for simple button

**Implementation**:
```tsx
<button
  className="navbar__link button button--secondary button--sm"
  onClick={handleLogout}
  aria-label={`Logout from ${user.email}`}
>
  Logout
</button>
```

**Accessibility Checklist**:
- ✅ Semantic HTML (`<button>` for interactive elements)
- ✅ Keyboard navigable (native button behavior)
- ✅ Screen reader friendly (aria-label with context)
- ✅ Visual focus indicators (Docusaurus button classes include :focus styles)
- ✅ Color contrast (Docusaurus theme maintains WCAG AA compliance)

---

## Summary of Technical Approach

### Core Changes Required

1. **Modify CustomLoginLogoutNavbarItem.tsx** (lines 41-74):
   - Remove dropdown container and state management (lines 12-29, 43-73)
   - Replace with side-by-side email (span) + logout button
   - Keep existing `useAuth()` hook for state
   - Keep existing `handleLogout` function (already correct)
   - Keep loading state display (line 37-39)
   - Keep unauthenticated state (lines 76-85) unchanged

2. **Optional CSS adjustments** (if needed for spacing):
   - Add to `src/components/auth/auth.css` for gap between email and button
   - Use existing Docusaurus classes first, only add custom CSS if required

3. **No backend changes** - all auth API endpoints remain unchanged

4. **No AuthContext changes** - signout() already works correctly

### Implementation Complexity: LOW

- **Lines of code changed**: ~30 lines in single file
- **New dependencies**: None
- **API changes**: None
- **Database changes**: None
- **Breaking changes**: None (only UI presentation changes)

### Testing Strategy

**Manual Testing Checklist** (per spec requirements):
1. User signs up → email + logout button appear in navbar
2. User logs in → email + logout button appear in navbar
3. Click logout → session cleared, navbar shows Login button
4. Logout redirect → user sent to home page (/)
5. Page refresh when authenticated → email + logout button persist
6. Page refresh when unauthenticated → only Login button shows
7. Multi-tab test → logout in one tab, verify state in other tab
8. RAG chatbot access → works when authenticated, restricted after logout

**No automated tests** - project has no test framework configured (package.json:83)

---

## Risk Assessment

### Low Risk
- ✅ Single file modification
- ✅ No API changes
- ✅ No state management changes
- ✅ Existing patterns reused
- ✅ Easy to rollback (git revert)

### Minimal Impact
- UI-only change in navbar
- No effect on auth backend
- No effect on RAG chatbot
- No effect on signup/signin flows

### Validation Points
- All 16 functional requirements can be validated through manual testing
- 8 success criteria are measurable (visual inspection + timing)
- No new failure modes introduced
