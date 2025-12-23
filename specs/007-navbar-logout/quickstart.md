# Quick Start: Navbar Logout Button Implementation

**Feature**: 007-navbar-logout
**Date**: 2025-12-23
**Estimated Time**: 30-45 minutes

## What You'll Build

Transform the Docusaurus navbar from hiding the logout button in a dropdown to displaying it prominently beside the user's email address.

**Before**: `[user@email.com ▼]` (click to see logout)
**After**: `[user@email.com] [Logout]` (always visible)

---

## Prerequisites

### Required Knowledge
- ✅ TypeScript/React basics (JSX, hooks, event handlers)
- ✅ Docusaurus theming concepts (custom navbar items)
- ✅ CSS for basic styling (flexbox, spacing)

### Required Access
- ✅ Write access to repository
- ✅ Local development environment (Node.js installed)
- ✅ Branch `007-navbar-logout` checked out

### Required Files (Already Exist)
- ✅ `src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx` (will modify)
- ✅ `src/components/auth/AuthContext.tsx` (read-only reference)
- ✅ `src/lib/auth-client.ts` (read-only reference)
- ✅ `docusaurus.config.ts` (no changes needed)

---

## Step 1: Review Current Implementation (5 min)

### Read the Existing Code

Open `src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx` and identify:

**Lines to Remove** (dropdown pattern):
```tsx
// Line 12-13: Dropdown state
const [isDropdownOpen, setIsDropdownOpen] = useState(false);
const dropdownRef = useRef<HTMLDivElement>(null);

// Line 16-29: Click-outside handler useEffect
useEffect(() => {
  function handleClickOutside(event: MouseEvent) {
    // ... dropdown logic
  }
  // ...
}, [isDropdownOpen]);

// Line 31-35: Dropdown toggle in handleLogout
const handleLogout = async () => {
  await signout();
  setIsDropdownOpen(false);  // REMOVE THIS LINE
  history.push('/');
};

// Line 41-74: Dropdown JSX structure
<div className="navbar__item dropdown dropdown--hoverable" ref={dropdownRef}>
  <button
    className="navbar__link button button--secondary button--sm"
    onClick={() => setIsDropdownOpen(!isDropdownOpen)}  // REMOVE
    aria-expanded={isDropdownOpen}  // REMOVE
    aria-haspopup="true"  // REMOVE
  >
    {user.email}
  </button>
  {isDropdownOpen && (  // REMOVE entire conditional
    <ul className="dropdown__menu" style={{ display: 'block' }}>
      <li>
        <button className="dropdown__link" onClick={handleLogout}>
          Logout
        </button>
      </li>
    </ul>
  )}
</div>
```

**Lines to Keep** (still needed):
```tsx
// Line 6-7: Hooks
import { useAuth } from '@site/src/components/auth/AuthContext';
import { useHistory } from '@docusaurus/router';

// Line 10: useAuth hook
const { user, isAuthenticated, isLoading, signout } = useAuth();

// Line 37-39: Loading state
if (isLoading) {
  return <span className="navbar__item">Loading...</span>;
}

// Line 76-85: Unauthenticated state (no changes)
return (
  <div className="navbar__item">
    <a
      className="navbar__link button button--primary button--sm"
      href="/auth/signin"
    >
      Login
    </a>
  </div>
);
```

---

## Step 2: Modify the Component (15 min)

### 2.1 Remove Dropdown Imports and State

**Delete these lines** (lines 5, 12-13):
```tsx
import React, { useState, useRef, useEffect } from 'react';  // BEFORE
import React from 'react';  // AFTER (remove useState, useRef, useEffect)

const [isDropdownOpen, setIsDropdownOpen] = useState(false);  // DELETE
const dropdownRef = useRef<HTMLDivElement>(null);             // DELETE
```

### 2.2 Remove Click-Outside Effect

**Delete entire useEffect block** (lines 16-29):
```tsx
// DELETE THIS ENTIRE BLOCK
useEffect(() => {
  function handleClickOutside(event: MouseEvent) {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
      setIsDropdownOpen(false);
    }
  }

  if (isDropdownOpen) {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }
}, [isDropdownOpen]);
```

### 2.3 Simplify handleLogout Function

**Replace lines 31-35** with:
```tsx
const handleLogout = async () => {
  await signout();
  history.push('/');
};
```

### 2.4 Replace Dropdown JSX with Side-by-Side Layout

**Replace lines 41-74** with:
```tsx
if (isAuthenticated && user) {
  return (
    <div className="navbar__item navbar__item--auth">
      <span className="navbar__link navbar__link--email">
        {user.email}
      </span>
      <button
        className="navbar__link button button--secondary button--sm"
        onClick={handleLogout}
        aria-label={`Logout from ${user.email}`}
      >
        Logout
      </button>
    </div>
  );
}
```

### 2.5 Keep Unauthenticated State Unchanged

**Lines 76-85 stay exactly the same**:
```tsx
return (
  <div className="navbar__item">
    <a
      className="navbar__link button button--primary button--sm"
      href="/auth/signin"
    >
      Login
    </a>
  </div>
);
```

---

## Step 3: Add Spacing Styles (Optional, 5 min)

If the email and logout button are too close together, add CSS.

### Create or Update `src/components/auth/auth.css`

Add this rule:
```css
.navbar__link--email {
  margin-right: 0.5rem;
  color: var(--ifm-navbar-link-color);
  font-weight: normal;
}

.navbar__item--auth {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
```

### Import the CSS in the Component

Add at the top of `CustomLoginLogoutNavbarItem.tsx`:
```tsx
import '@site/src/components/auth/auth.css';
```

---

## Step 4: Test the Implementation (10 min)

### 4.1 Start Development Server

```bash
npm start
```

Wait for the server to start (usually http://localhost:3000)

### 4.2 Manual Test Checklist

**Test Case 1: Unauthenticated State**
- [ ] Open http://localhost:3000
- [ ] Navbar shows only "Login" button
- [ ] No email or logout button visible

**Test Case 2: Login Flow**
- [ ] Click "Login" button
- [ ] Sign in with test credentials
- [ ] After login, navbar shows **email** and **Logout** button side-by-side
- [ ] Both are visible (not in a dropdown)

**Test Case 3: Logout Flow**
- [ ] Click "Logout" button
- [ ] Wait ~1 second (should complete quickly)
- [ ] Navbar updates to show "Login" button
- [ ] Email and logout button disappear
- [ ] Page redirects to home (/)

**Test Case 4: Page Refresh (Authenticated)**
- [ ] Log in again
- [ ] Refresh the page (F5 or Ctrl+R)
- [ ] Email + logout button still visible
- [ ] No flicker or temporary "Login" button display

**Test Case 5: Page Refresh (Unauthenticated)**
- [ ] Logout
- [ ] Refresh the page
- [ ] "Login" button persists
- [ ] No email or logout button

**Test Case 6: Keyboard Navigation**
- [ ] Log in
- [ ] Press Tab repeatedly until logout button is focused
- [ ] Press Enter
- [ ] Logout action triggers correctly

**Test Case 7: Screen Reader (Optional)**
- [ ] Enable screen reader (NVDA, JAWS, or VoiceOver)
- [ ] Navigate to navbar
- [ ] Verify email is announced
- [ ] Verify logout button announced as "Logout from [email]"

---

## Step 5: Verify No Regressions (5 min)

### Check Other Features Still Work

**RAG Chatbot** (if authenticated):
- [ ] Open chatbot widget
- [ ] Verify it still works for authenticated users
- [ ] Logout and verify chatbot access is restricted

**Signup Flow**:
- [ ] Navigate to /auth/signup
- [ ] Create a new account
- [ ] After signup, email + logout button appear in navbar

**Signin Flow**:
- [ ] Navigate to /auth/signin
- [ ] Login with existing credentials
- [ ] Email + logout button appear in navbar

---

## Step 6: Build for Production (5 min)

### Test Production Build

```bash
npm run build
```

**Expected Output**:
- ✅ Build completes without errors
- ✅ No TypeScript type errors
- ✅ No console warnings about navbar

### Serve Production Build Locally

```bash
npm run serve
```

Open http://localhost:3000 and repeat key test cases (login, logout, refresh).

---

## Troubleshooting

### Problem: Email and Logout Button Stack Vertically

**Cause**: Missing flexbox layout on container

**Solution**: Ensure `.navbar__item--auth` has `display: flex` in CSS (Step 3)

---

### Problem: Logout Button Not Clickable

**Cause**: Missing `onClick` handler or TypeScript error

**Solution**:
1. Check `handleLogout` function is defined
2. Check `onClick={handleLogout}` is on button element (not a string!)
3. Run `npm start` and check console for errors

---

### Problem: "useAuth must be used within AuthProvider" Error

**Cause**: AuthContext not wrapping component

**Solution**: This should already be set up in `src/theme/Root.tsx`. If error persists, verify:
```tsx
// src/theme/Root.tsx should have:
import { AuthProvider } from '@site/src/components/auth/AuthContext';

export default function Root({ children }) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}
```

---

### Problem: Logout Doesn't Redirect

**Cause**: Missing `history.push('/')` or useHistory import

**Solution**: Ensure `handleLogout` includes:
```tsx
const history = useHistory();

const handleLogout = async () => {
  await signout();
  history.push('/');  // THIS LINE IS CRITICAL
};
```

---

### Problem: Styles Look Wrong (Button Colors Off)

**Cause**: Wrong Docusaurus button classes

**Solution**: Use exact classes:
- Logout button: `button button--secondary button--sm`
- Login button: `button button--primary button--sm`

---

## Success Criteria Checklist

Before marking this feature complete, verify:

- [ ] **SC-001**: After logging in, email + logout button both visible in navbar
- [ ] **SC-002**: Logout action completes within 1 second
- [ ] **SC-003**: Navbar updates within 500ms after logout (no page refresh needed)
- [ ] **SC-004**: Unauthenticated users see zero auth elements (only "Login")
- [ ] **SC-005**: Logout button appears on 100% of page loads when authenticated
- [ ] **SC-006**: After logout, redirected to home page within 1 second
- [ ] **SC-007**: RAG chatbot still works for authenticated users
- [ ] **SC-008**: Signup/signin flows unchanged and working

---

## Next Steps

After completing this quick start:

1. **Run `/sp.tasks`** to generate detailed task breakdown for tracking
2. **Create PR** after testing is complete
3. **Request code review** from team
4. **Deploy to staging** for QA testing
5. **Merge to main** after approval

---

## Reference Files

| File | Purpose | Modify? |
|------|---------|---------|
| `src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx` | Navbar component | ✅ YES |
| `src/components/auth/auth.css` | Styling | ✅ YES (optional) |
| `src/components/auth/AuthContext.tsx` | Auth state | ❌ NO |
| `src/lib/auth-client.ts` | API calls | ❌ NO |
| `docusaurus.config.ts` | Navbar config | ❌ NO |
| `specs/007-navbar-logout/spec.md` | Requirements | 📖 READ |
| `specs/007-navbar-logout/contracts/navbar-component-interface.md` | Component interface | 📖 READ |

---

## Estimated Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| Setup & Review | 5 min | Read existing code |
| Implementation | 15 min | Modify component |
| Styling | 5 min | Add CSS (optional) |
| Manual Testing | 10 min | Run through test cases |
| Regression Check | 5 min | Verify other features |
| Production Build | 5 min | Build and serve |
| **Total** | **30-45 min** | End-to-end completion |

---

## Getting Help

If you encounter issues:

1. **Check spec**: `specs/007-navbar-logout/spec.md` for requirements
2. **Check interface**: `specs/007-navbar-logout/contracts/navbar-component-interface.md` for component contract
3. **Check research**: `specs/007-navbar-logout/research.md` for implementation patterns
4. **Check existing code**: `src/components/auth/AuthContext.tsx` to understand useAuth hook

**Common Pitfall**: Don't forget to remove the dropdown state! This is the #1 cause of leftover bugs.
