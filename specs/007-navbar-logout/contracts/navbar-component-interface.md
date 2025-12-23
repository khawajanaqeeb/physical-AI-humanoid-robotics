# Component Interface Contract: CustomLoginLogoutNavbarItem

**Feature**: 007-navbar-logout
**Component**: `src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx`
**Date**: 2025-12-23
**Type**: React Component (Docusaurus custom navbar item)

## Purpose

Renders authentication-aware UI in the Docusaurus navbar, displaying either:
- Login button (when unauthenticated)
- User email + Logout button (when authenticated)
- Loading state (while session is being fetched)

---

## Component Signature

### Import Path
```typescript
// Registered in Docusaurus config as 'custom-LoginLogoutNavbarItem'
// Implementation: src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx
```

### Props

**This component accepts NO props** (Docusaurus custom navbar items are prop-less)

```typescript
interface CustomLoginLogoutNavbarItemProps {
  // No props - state comes from AuthContext via useAuth()
}

export default function CustomLoginLogoutNavbarItem(): JSX.Element
```

---

## Dependencies (Consumed Interfaces)

### useAuth Hook

**Source**: `src/components/auth/AuthContext.tsx`

**Interface**:
```typescript
interface AuthContextType {
  user: User | null;           // Current user or null if unauthenticated
  isAuthenticated: boolean;    // Derived from !!user
  isLoading: boolean;          // True while session is being fetched
  signout: () => Promise<void>; // Function to logout user
}

interface User {
  id: string;
  email: string;
  profile?: {
    software_experience: string;
    hardware_experience: string;
    interests: string[];
  };
}
```

**Usage Contract**:
- Component MUST call `useAuth()` to get authentication state
- Component MUST NOT directly access localStorage or auth-client.ts
- Component MUST handle all three states: loading, authenticated, unauthenticated

### useHistory Hook

**Source**: `@docusaurus/router`

**Interface**:
```typescript
interface History {
  push: (path: string) => void;
  replace: (path: string) => void;
  go: (n: number) => void;
  // ... other methods not used by this component
}
```

**Usage Contract**:
- Used ONLY for redirect after logout: `history.push('/')`
- Component MUST NOT navigate during render (only in event handlers)

---

## Rendering Contract

### Render Behavior Matrix

| State | Condition | Rendered Output | Classes | Events |
|-------|-----------|-----------------|---------|--------|
| **Loading** | `isLoading === true` | `<span>Loading...</span>` | `navbar__item` | None |
| **Authenticated** | `isAuthenticated && user !== null` | Email text + Logout button | See below | Logout click |
| **Unauthenticated** | `!isAuthenticated && user === null` | Login link | `navbar__item` | None (link navigation) |

### Authenticated State Detailed Output

```tsx
<div className="navbar__item">
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
```

**Constraints**:
- Email and logout button MUST be sibling elements (side-by-side layout)
- Email MUST be displayed as read-only text (span, not button)
- Logout MUST be a button element for accessibility
- Both MUST use `navbar__link` class for consistent styling

### Unauthenticated State Detailed Output

```tsx
<div className="navbar__item">
  <a
    className="navbar__link button button--primary button--sm"
    href="/auth/signin"
  >
    Login
  </a>
</div>
```

**Constraints**:
- MUST link to `/auth/signin` page
- MUST use anchor tag (not button) for page navigation
- MUST use `button--primary` class (different from logout button)

---

## Event Handlers

### handleLogout

**Signature**:
```typescript
const handleLogout = async (): Promise<void> => {
  await signout();  // From useAuth()
  history.push('/'); // Redirect to home page
}
```

**Pre-conditions**:
- User MUST be authenticated (button only rendered when `isAuthenticated === true`)
- `signout` function MUST be available from `useAuth()`

**Post-conditions**:
- User session cleared (handled by AuthContext)
- LocalStorage tokens removed (handled by auth-client.ts)
- Navbar re-renders to show Login button (automatic via React state update)
- User redirected to home page (`/`)

**Error Handling**:
- Network failures during signout → Gracefully handled by auth-client.ts (localStorage still cleared)
- Component does NOT need try/catch (error handling in lower layers)

**Timing Requirements** (from spec):
- Logout API call MUST complete within 1 second (SC-002)
- UI update MUST occur within 500ms (SC-003)

---

## Styling Contract

### CSS Classes Used

| Element | Classes | Purpose |
|---------|---------|---------|
| Container | `navbar__item` | Docusaurus navbar item wrapper |
| Email text | `navbar__link navbar__link--email` | Email display styling |
| Logout button | `navbar__link button button--secondary button--sm` | Button styling (secondary theme) |
| Login link | `navbar__link button button--primary button--sm` | Button styling (primary theme) |
| Loading text | `navbar__item` | Minimal styling for loading state |

**Custom CSS** (if needed):
- File: `src/components/auth/auth.css`
- Purpose: Gap/spacing between email and logout button
- Example:
  ```css
  .navbar__link--email {
    margin-right: 0.5rem;
  }
  ```

**Constraints**:
- MUST NOT override core Docusaurus navbar styles
- MUST NOT introduce custom color schemes (use theme colors)
- MUST respect `colorMode` (light/dark theme compatibility)

---

## Accessibility Requirements

### Semantic HTML
- ✅ Use `<button>` for logout action (not `<a>` or `<div>`)
- ✅ Use `<a>` for login navigation (not `<button>`)
- ✅ Use `<span>` for read-only email text (not interactive element)

### ARIA Attributes
- ✅ `aria-label` on logout button with context: `Logout from ${user.email}`
- ❌ NO `aria-expanded` or `aria-haspopup` (dropdown removed)
- ❌ NO `role` attributes needed (semantic HTML sufficient)

### Keyboard Navigation
- ✅ Logout button MUST be keyboard focusable (native button behavior)
- ✅ Logout button MUST activate on Enter/Space (native button behavior)
- ✅ Login link MUST be keyboard focusable (native anchor behavior)
- ✅ Tab order: Email (not focusable) → Logout button (focusable)

### Screen Reader Compatibility
- ✅ Email text read as static content
- ✅ Logout button announced as "Logout from [email]" button
- ✅ Login link announced as "Login" link

---

## State Management Contract

### Component State

**NO local useState or useRef** - Component is fully controlled by external state

**All state comes from**:
- `useAuth()` → user, isAuthenticated, isLoading, signout

**State Flow**:
```
AuthContext.user changes
  ↓
useAuth() returns new values
  ↓
Component re-renders automatically
  ↓
UI updates (email+logout ↔ login)
```

### Side Effects

**Allowed Side Effects**:
- `handleLogout` calls `signout()` and `history.push('/')`

**Prohibited Side Effects**:
- ❌ Direct localStorage access
- ❌ Direct API calls
- ❌ Modifying AuthContext state
- ❌ Navigation during render (only in event handlers)

---

## Integration Points

### Docusaurus Config Registration

**File**: `docusaurus.config.ts`

**Existing Configuration** (lines 88-90):
```typescript
navbar: {
  items: [
    // ... other items
    {
      type: 'custom-LoginLogoutNavbarItem',
      position: 'right',
    },
    // ... other items
  ],
}
```

**Contract**:
- Component name MUST match: `CustomLoginLogoutNavbarItem.tsx`
- Type MUST be: `'custom-LoginLogoutNavbarItem'` (convention: `custom-{ComponentName}`)
- Position MUST be `'right'` (per existing config)
- Component MUST be registered in `src/theme/NavbarItem/ComponentTypes.tsx`

### Component Types Registration

**File**: `src/theme/NavbarItem/ComponentTypes.tsx`

**Required Export**:
```typescript
import CustomLoginLogoutNavbarItem from './CustomLoginLogoutNavbarItem';

export default {
  'custom-LoginLogoutNavbarItem': CustomLoginLogoutNavbarItem,
};
```

---

## Testing Contract

### Manual Test Cases

| Test Case | Steps | Expected Outcome |
|-----------|-------|------------------|
| **TC-1: Unauthenticated Display** | Open site without logging in | Show "Login" button only |
| **TC-2: Authenticated Display** | Login with valid credentials | Show email + "Logout" button side-by-side |
| **TC-3: Logout Action** | Click "Logout" when authenticated | Session cleared, redirected to `/`, "Login" button shown |
| **TC-4: Logout Network Failure** | Logout while offline/backend down | UI still updates to "Login" button |
| **TC-5: Page Refresh (Authenticated)** | Refresh page while logged in | Email + "Logout" button persist |
| **TC-6: Page Refresh (Unauthenticated)** | Refresh page after logout | "Login" button persists |
| **TC-7: Keyboard Navigation** | Tab to logout button, press Enter | Logout triggered |
| **TC-8: Screen Reader** | Use screen reader on navbar | Email read, logout announced with context |

### Performance Contract

From spec (SC-002, SC-003):
- Logout action: < 1 second
- UI update after logout: < 500ms

**Measurement**:
```typescript
const start = performance.now();
await handleLogout();
const duration = performance.now() - start;
console.log(`Logout took ${duration}ms`); // Should be < 1000ms
```

---

## Breaking Changes Contract

### What is NOT allowed to change:
- ❌ AuthContext interface (would break all auth components)
- ❌ auth-client.ts API (would break backend integration)
- ❌ Backend authentication endpoints (out of scope)
- ❌ RAG chatbot auth integration (per spec constraint FR-014)
- ❌ Existing signup/signin flows (per spec constraint SC-008)

### What CAN change:
- ✅ Component render output (dropdown → side-by-side layout)
- ✅ Component local state (remove dropdown state)
- ✅ CSS classes/styling (for button spacing)

---

## Version Compatibility

**Docusaurus Version**: 3.9.2
- Component uses stable `@theme/NavbarItem` pattern
- No experimental APIs used
- Forward compatible with Docusaurus 4 (per config future flag)

**React Version**: 19.2.7
- Standard hooks (no concurrent features)
- No React 19-specific APIs
- Backward compatible with React 18

**TypeScript Version**: 5.9.3
- ES2020 target (per tsconfig.json)
- Strict mode: false (per tsconfig.json)
- No advanced TS features (decorators, etc.)

---

## Summary

**This component is a pure presentation layer** with no business logic:
- Consumes auth state from AuthContext
- Renders UI based on that state
- Delegates logout action to AuthContext
- Delegates navigation to Docusaurus router

**Total interface surface area**: 4 inputs (user, isAuthenticated, isLoading, signout), 1 output (JSX rendering), 1 side effect (handleLogout)
