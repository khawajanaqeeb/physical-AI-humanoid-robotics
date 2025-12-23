# Implementation Plan: Authentication Frontend UI

**Branch**: `005-auth-frontend-ui` | **Date**: 2025-12-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-auth-frontend-ui/spec.md`

## Summary

Implement frontend authentication UI for user signup, signin, and profile personalization integrated with FastAPI backend. The feature will provide isolated React components within the existing Docusaurus site to collect user background information (software/hardware experience, interests via multi-select checkboxes) and enable personalized RAG chatbot responses. Components exist but require updates to match specification requirements including session timeout (1 hour), multi-select interests (vs current text input), navigation bar logout button, and manual retry for network errors.

## Technical Context

**Language/Version**: TypeScript 4.x + React 18 (Docusaurus 3.x)
**Primary Dependencies**: Docusaurus 3.x, React 18, TypeScript 4.x
**Storage**: LocalStorage for session tokens + user profile (client-side), PostgreSQL (Neon) via FastAPI backend
**Testing**: Manual testing + browser DevTools (no automated tests in spec)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) - desktop and mobile viewports (320px - 2560px)
**Project Type**: Web (Docusaurus frontend + FastAPI backend)
**Performance Goals**: Form validation < 500ms, API requests < 3s, registration completion < 3min
**Constraints**: No modifications to existing Docusaurus core, isolated auth components only, 1-hour session timeout, no hardcoded secrets
**Scale/Scope**: Single-user focused, 10 predefined interest categories, 3 experience levels each for software/hardware

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Fully Spec-Driven Workflow
**Status**: ✅ PASS
**Evidence**: Feature spec exists at `specs/005-auth-frontend-ui/spec.md` with comprehensive requirements (FR-001 through FR-028) and 4 prioritized user stories.

### Gate 2: Technical Accuracy, Clarity, and Educational Focus
**Status**: ✅ PASS
**Evidence**: This is a functional auth feature for the textbook platform, not educational content itself. Implementation will follow React/TypeScript best practices and maintain clarity in code organization.

### Gate 3: Modular Documentation
**Status**: ✅ PASS
**Evidence**: Auth components are isolated in `frontend/src/components/auth/` per FR-026. Docusaurus structure remains untouched per FR-027.

### Gate 4: Toolchain Fidelity
**Status**: ✅ PASS
**Evidence**: Using Spec-Kit Plus for specification, Claude Code for planning, Docusaurus for frontend, FastAPI for backend. Plan follows prescribed workflow.

**Overall Constitution Compliance**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/005-auth-frontend-ui/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── signup-api.md    # POST /auth/signup contract
│   ├── signin-api.md    # POST /auth/signin contract
│   └── profile-api.md   # GET /auth/profile contract (if needed)
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   └── auth/                          # Auth components (isolated, FR-026)
│   │       ├── SignupForm.tsx             # EXISTS - needs updates
│   │       ├── SigninForm.tsx             # EXISTS - needs review
│   │       ├── UserContext.tsx            # EXISTS - needs session timeout logic
│   │       ├── LoginLogout.tsx            # EXISTS - needs review
│   │       ├── Profile.tsx                # EXISTS - needs review
│   │       ├── index.tsx                  # EXISTS - export barrel
│   │       ├── SimpleLoginLogout.js       # EXISTS - may need removal
│   │       └── auth.module.css            # TO CREATE - component styles
│   │
│   ├── theme/                              # Docusaurus theme overrides
│   │   ├── Layout.tsx                      # EXISTS - wraps UserProvider
│   │   └── NavbarItem/
│   │       └── LoginLogoutNavbarItem.js    # EXISTS - needs review for logout button
│   │
│   ├── pages/
│   │   ├── auth-demo.js                    # EXISTS - demo page
│   │   └── index.js                        # Homepage (do not modify per FR-027)
│   │
│   └── css/
│       └── custom.css                      # Global styles (minimal additions only)
│
├── .env                                    # Environment variables (gitignored)
├── .env.example                            # Example env vars (committed)
└── docusaurus.config.js                   # Docusaurus config (minimal changes)

backend/
└── src/
    └── (existing FastAPI auth endpoints - not modified in this feature)
```

**Structure Decision**: Web application structure with frontend (Docusaurus) and backend (FastAPI) separation. Auth components are isolated in `frontend/src/components/auth/` per requirement FR-026. No modifications to existing Docusaurus pages or chatbot integration code per FR-027 and FR-028.

## Complexity Tracking

**No Constitution violations**. Complexity is justified by:
- React Context for state management: Industry standard for auth state in React applications
- LocalStorage for session persistence: Required by FR-013 (restore session on page refresh)
- TypeScript interfaces: Already in use, maintains type safety across components

---

## Phase 0 Research Tasks

Phase 0 will be documented in `research.md`. The following research tasks must be completed before proceeding to Phase 1:

### Research Task 1: Docusaurus Theme Swizzling Best Practices
**Unknown**: How to safely add logout button to navigation bar without breaking Docusaurus theme updates (FR-014a)

**Research Goal**: Determine best approach for adding custom navbar item in Docusaurus:
- Swizzle vs plugin vs theme component override
- Safe update patterns for Docusaurus 3.x
- Integration with UserContext for auth state

**Expected Output**: Decision on navbar customization approach with migration safety considerations

### Research Task 2: Session Timeout Implementation Patterns
**Unknown**: Best practice for implementing 1-hour session timeout with activity tracking (FR-013a)

**Research Goal**: Evaluate approaches:
- setTimeout/setInterval vs event listeners for activity detection
- Token expiration validation strategies
- Graceful session expiry UX patterns

**Expected Output**: Recommended pattern for session timeout with fallback for expired backend sessions

### Research Task 3: Multi-Select Checkbox Component
**Unknown**: React component pattern for multi-select checkboxes with 10 predefined interests (FR-001a)

**Research Goal**: Determine implementation:
- Controlled component pattern with array state
- Accessibility considerations (ARIA labels, keyboard navigation)
- Responsive layout for 10 checkboxes

**Expected Output**: Component structure for multi-select interests field

### Research Task 4: XSS Prevention Best Practices in React
**Unknown**: Specific sanitization approach for form inputs (FR-020)

**Research Goal**: Validate current React built-in XSS protection:
- React's automatic escaping capabilities
- DOMPurify or alternative libraries needed?
- Input validation vs output encoding

**Expected Output**: Confirmation of XSS prevention strategy (likely: rely on React's built-in protection + backend validation)

### Research Task 5: Environment Variable Handling in Docusaurus
**Unknown**: Correct naming convention and access pattern for backend URL (FR-016)

**Research Goal**: Understand Docusaurus env var requirements:
- `NEXT_PUBLIC_` prefix (from Next.js pattern) vs Docusaurus actual requirement
- Build-time vs runtime variable access
- Differences between `docusaurus.config.js` and component-level access

**Expected Output**: Correct env var naming (likely no prefix needed for Docusaurus) and access pattern

---

## Phase 1 Design & Contracts

Phase 1 will generate the following artifacts:

### Data Model (data-model.md)

Will contain:

#### Client-Side Entities

**UserProfile**
- Fields: user_id, email, software_experience, hardware_experience, interests[], created_at, last_login_at
- Validation rules from FR-002, FR-003, FR-003a, FR-004
- Storage: LocalStorage

**SessionState**
- Fields: access_token, refresh_token, expires_at, last_activity
- Lifecycle: 1 hour timeout with activity tracking
- Storage: LocalStorage

**AuthFormState** (ephemeral)
- Fields: Form fields, errors, loading state, network error state
- Lifecycle: Component-level only

**Predefined Interest List** (FR-001a):
Robotics, Artificial Intelligence, Machine Learning, Hardware Design, Software Development, IoT, Computer Vision, Natural Language Processing, Autonomous Systems, Embedded Systems

### API Contracts (contracts/ directory)

Will generate:
- `signup-api.md`: POST /auth/signup contract
- `signin-api.md`: POST /auth/signin contract
- `profile-api.md`: GET /auth/profile contract (optional)

Each contract will specify:
- Endpoint URL structure
- Request/response schemas
- Error response formats
- Success/failure scenarios

### Component Architecture

Will document:

**Component Hierarchy**
```
UserProvider (Context)
├── Layout (Docusaurus theme)
│   ├── Navbar
│   │   └── LoginLogoutNavbarItem (logout button)
│   └── Main Content
│       ├── SignupForm
│       ├── SigninForm
│       └── Chatbot (existing, enhanced)
```

**Component Responsibilities**
- UserProvider: Session management, 1-hour timeout, localStorage persistence
- SignupForm: Multi-select interests, password validation (8 chars), network retry
- SigninForm: Authentication, error handling, network retry
- LoginLogoutNavbarItem: Logout button in nav bar

### Quickstart Guide (quickstart.md)

Will provide:
- Local development setup instructions
- Environment variable configuration
- Testing checklist aligned with success criteria
- Production deployment notes

---

## Phase 2: Implementation Readiness

**STOP HERE - Phase 2 (tasks.md generation) is handled by `/sp.tasks` command**

This plan provides:
1. ✅ Complete technical context
2. ✅ Constitution compliance verification
3. ✅ Research tasks identified for Phase 0
4. ✅ Data model and API contracts outline for Phase 1
5. ✅ Component architecture design for Phase 1
6. ✅ Quickstart guide outline for Phase 1

**Next Steps**:
1. Complete Phase 0: Create `research.md` with research task findings
2. Complete Phase 1: Generate `data-model.md`, `contracts/`, `quickstart.md`
3. Run `/sp.tasks` to generate `tasks.md` with atomic implementation tasks

---

## Key Decisions Log

### Decision 1: Multi-Select Interests Implementation
**Context**: FR-001a specifies 10 predefined interest options with multi-select checkboxes. Current implementation uses free-text input.

**Decision**: Replace text input with controlled checkbox group component.

**Rationale**: Structured data improves RAG personalization quality, prevents typos/inconsistencies, aligns with spec requirement.

**Alternative Rejected**: Keep text input - would violate FR-001a and provide lower-quality structured data.

### Decision 2: Session Timeout Strategy
**Context**: FR-013a requires 1-hour session timeout with inactivity tracking.

**Decision**: Implement client-side timer that resets on user activity (mouse/keyboard events), with periodic backend validation.

**Rationale**: Provides immediate UX feedback, reduces unnecessary backend calls, gracefully handles backend token expiration.

**Alternative Rejected**: Backend-only timeout - would require constant heartbeat requests or surprise logouts.

### Decision 3: Password Validation Simplification
**Context**: Existing SignupForm.tsx (lines 51-58) validates password has letter + number. Spec FR-003a only requires min 8 characters.

**Decision**: Remove complexity requirement, keep only 8-character minimum.

**Rationale**: Align with spec clarification (Q1 answer: "Minimum 8 characters, no other requirements"). Simpler requirement improves UX without compromising security for this use case.

**Alternative Rejected**: Keep strict validation - would violate spec and create unnecessary friction.

### Decision 4: Environment Variable Naming
**Context**: Current code uses `process.env.NEXT_PUBLIC_BACKEND_URL` (Next.js convention). Docusaurus doesn't require NEXT_PUBLIC_ prefix.

**Decision**: Research actual Docusaurus env var requirements in Phase 0, likely change to `BACKEND_URL` or confirm current naming works.

**Rationale**: Use framework-appropriate conventions, avoid confusion with Next.js patterns.

**Alternative Rejected**: Keep NEXT_PUBLIC_ - may not work correctly in Docusaurus build process.

### Decision 5: Logout Button Placement
**Context**: FR-014a requires logout button in navigation bar. Current implementation exists in `NavbarItem/LoginLogoutNavbarItem.js`.

**Decision**: Verify and potentially enhance existing implementation to ensure visibility and UX compliance.

**Rationale**: Leverage existing Docusaurus theme swizzling pattern, maintain consistency with site navigation.

**Alternative Rejected**: Create separate logout page - less discoverable, violates spec requirement for nav bar placement.

---

## Risks & Mitigations

### Risk 1: Session Timeout Complexity
**Risk**: Implementing accurate 1-hour timeout with activity tracking may introduce edge cases (background tabs, mobile sleep mode).

**Mitigation**: Start with simple setTimeout approach, add activity event listeners, include backend token validation fallback.

**Contingency**: If client-side tracking proves unreliable, rely on backend token expiration and handle gracefully in API error responses.

### Risk 2: Docusaurus Theme Swizzling Conflicts
**Risk**: Swizzling NavbarItem may conflict with future Docusaurus updates or break existing navbar functionality.

**Mitigation**: Use minimal swizzling (wrapper pattern), document swizzled components, test navbar functionality after updates.

**Contingency**: Fall back to custom navbar plugin if swizzling proves unmaintainable.

### Risk 3: CORS Configuration Mismatch
**Risk**: Production deployment may fail if CORS not properly configured for Vercel domain.

**Mitigation**: Verify CORS settings include both localhost (dev) and Vercel (prod) domains. Test with actual deployed URLs before final release.

**Contingency**: Add wildcard CORS for testing (NOT for production), then restrict to specific domains.

### Risk 4: LocalStorage Limitations
**Risk**: Users with cookies disabled or private browsing may lose session state.

**Mitigation**: Detect localStorage availability on mount, show warning message if unavailable.

**Contingency**: Implement fallback to session-only memory storage (loses persistence but maintains function within single session).

---

## Success Criteria Verification

### Mapping Plan to Success Criteria

- **SC-001** (Registration < 3min): SignupForm design minimizes fields, multi-select interests faster than text input
- **SC-002** (Signin < 30sec): SigninForm has only email/password, autofocus on email field
- **SC-003** (Validation < 500ms): Client-side validation runs synchronously, no API calls for field validation
- **SC-004** (API requests < 3s): Network timeout configuration, progress indicators during requests
- **SC-005** (Session persistence): UserContext restores from localStorage on mount (FR-013)
- **SC-006** (XSS protection): React's built-in escaping + backend validation, no dangerouslySetInnerHTML usage
- **SC-007** (User-friendly errors): Generic "Invalid credentials" for auth errors, no stack traces exposed
- **SC-008** (Responsive 320px-2560px): CSS modules with mobile-first design, flexbox/grid layouts
- **SC-009** (No breaking changes): Isolated components in `/auth/`, no modifications to existing Docusaurus pages
- **SC-010** (No hardcoded secrets): All API URLs from environment variables, .env in .gitignore

**Plan Completeness**: All 10 success criteria addressed in component design and architecture decisions.
