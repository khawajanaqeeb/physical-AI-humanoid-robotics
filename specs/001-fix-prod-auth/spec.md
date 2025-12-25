# Feature Specification: Fix Production Authentication Server Connection Failure

**Feature Branch**: `001-fix-prod-auth`
**Created**: 2025-12-25
**Updated**: 2025-12-26
**Status**: Draft
**Input**: User description: "Fix persistent LOGIN/SIGNUP failure with 'Server not reachable' error on Vercel production (https://physical-ai-humanoid-robotics-e3c7.vercel.app/) and localhost, where frontend is deployed on Vercel and backend API on Railway"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Registration (Priority: P1)

Users attempting to create an account on the Vercel production frontend must be able to successfully register and authenticate through the Railway backend authentication service.

**Why this priority**: This is the most critical user flow. Without signup working, no new users can join the platform. This represents complete business functionality failure.

**Independent Test**: Can be fully tested by navigating to the signup page on Vercel production, filling the registration form, and successfully creating an account. Delivers immediate value by allowing user onboarding.

**Acceptance Scenarios**:

1. **Given** a new user visits the Vercel production site, **When** they fill out the signup form with valid credentials and submit, **Then** their account is created successfully and they receive confirmation
2. **Given** a user on the Vercel production site, **When** they attempt to signup with invalid data, **Then** they receive appropriate validation errors without connection failures

---

### User Story 2 - Existing User Login (Priority: P1)

Existing users must be able to log into their accounts on the Vercel production frontend through the Railway authentication backend.

**Why this priority**: Equal priority to signup because existing users cannot access the platform without this. Both represent critical authentication flows.

**Independent Test**: Can be fully tested by using pre-existing credentials on the Vercel production login page and successfully authenticating. Delivers value by restoring access for existing users.

**Acceptance Scenarios**:

1. **Given** a registered user visits the Vercel production site, **When** they enter valid credentials and submit the login form, **Then** they are authenticated successfully and see the logged-in state
2. **Given** an authenticated user on Vercel production, **When** they refresh the page or navigate between pages, **Then** their session persists without requiring re-authentication
3. **Given** a user on the Vercel production site, **When** they enter invalid credentials, **Then** they receive appropriate error messages without connection failures

---

### User Story 3 - User Logout (Priority: P2)

Authenticated users must be able to log out of their accounts on the Vercel production frontend, with the logout action properly communicated to the Railway backend.

**Why this priority**: While important for security and user control, the platform can function with users logged in. This is lower priority than the ability to log in or sign up.

**Independent Test**: Can be fully tested by logging in on Vercel production and clicking the logout button in the navbar, confirming the user is logged out and the UI updates accordingly.

**Acceptance Scenarios**:

1. **Given** an authenticated user on Vercel production, **When** they click the logout button in the navbar, **Then** they are logged out successfully and the UI shows the logged-out state
2. **Given** a user who just logged out on Vercel production, **When** they attempt to access protected resources, **Then** they are redirected to login or shown appropriate access denial

---

### Edge Cases

- What happens when the Railway backend is temporarily unavailable during an authentication attempt?
- How does the system handle network timeouts between Vercel and Railway?
- What happens when a user attempts authentication with an expired or invalid session token?
- How does the system handle CORS preflight failures or credential mismatches?
- What happens when environment variables are missing or misconfigured on Vercel?
- How does the system behave when switching between localhost (working) and production (failing)?

## Troubleshooting Strategy *(critical for this feature)*

This feature requires systematic, step-by-step investigation before implementing fixes. Each step MUST be completed and verified before proceeding to the next. Findings must be documented at each stage.

### Investigation Steps (Sequential - DO NOT SKIP)

**STEP 1 — Verify Backend Availability**
- Identify the Railway backend base URL currently configured
- Test backend health endpoints (`/health`, `/`, or auth endpoints) using real HTTP requests
- Confirm backend is running, publicly accessible, and returning non-500 responses
- STOP and report findings before continuing

**STEP 2 — Verify Backend Environment Variables (Railway)**
- Read `.env.example` carefully
- List ONLY environment variables REQUIRED for auth, database, and CORS
- Verify in Railway that variable names match EXACTLY (no frontend-only variables)
- Confirm database connectivity
- STOP and report findings

**STEP 3 — Verify Frontend Environment Variables (Vercel)**
- List all frontend-required variables
- Verify all variables start with `NEXT_PUBLIC_` (if required by framework)
- Ensure backend base URL is correct and reachable
- Confirm no localhost URLs exist in production configuration
- STOP and report findings

**STEP 4 — Verify API URL Wiring in Frontend Code**
- Locate EXACTLY where login/signup requests are made in the codebase
- Confirm base URL usage and no hardcoded localhost references
- Ensure environment variables are actually being read at runtime (not build-time only)
- STOP and report findings

**STEP 5 — Verify CORS Configuration (Critical)**
- Inspect backend CORS configuration code
- Ensure Vercel domain (`https://physical-ai-humanoid-robotics-e3c7.vercel.app`) is explicitly allowed
- Confirm credentials are allowed if cookies/sessions are used
- Verify OPTIONS preflight requests succeed
- STOP and report findings

**STEP 6 — Verify Auth Flow (better-auth)**
- Trace signup request → response flow
- Trace login request → response flow
- Confirm correct HTTP status codes and token/cookie issuance
- Identify EXACT failure point in the authentication chain
- STOP and report findings

**STEP 7 — Verify Session/Cookie Handling**
- Check Secure flag, SameSite policy, and Domain configuration for cookies
- Ensure compatibility between Railway backend and Vercel frontend for cross-origin cookies
- Test session persistence across page refreshes
- STOP and report findings

**STEP 8 — Verify Docusaurus Navbar State**
- Confirm auth state is persisted correctly in application state
- Verify navbar updates correctly after login
- Fix logout visibility ONLY if auth is confirmed working
- STOP and report findings

### Expected Deliverables

- **Root Cause Analysis**: Clear identification of the exact failure point(s)
- **Minimal Code Changes**: Only the necessary fixes to resolve the identified issue
- **Verification**: Confirmation that login and signup work on both localhost and Vercel production
- **Documentation**: Findings from each investigation step recorded in implementation notes

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST successfully route all authentication requests from the Vercel frontend to the Railway backend using production-safe absolute URLs (no localhost references)
- **FR-002**: System MUST use environment variables with the `NEXT_PUBLIC_` prefix for all browser-accessible configuration on Vercel (Docusaurus framework requirement)
- **FR-003**: System MUST properly configure CORS on the Railway backend to allow requests from the exact Vercel production domain (`https://physical-ai-humanoid-robotics-e3c7.vercel.app`) with credentials support
- **FR-004**: System MUST enable credential handling (cookies, authorization headers) in all authentication requests between Vercel and Railway
- **FR-005**: System MUST handle secure cookie transmission over HTTPS with appropriate SameSite and Secure flags for cross-origin scenarios
- **FR-006**: System MUST display clear error messages to users when authentication operations fail, distinguishing between "Server not reachable" (network failures) and validation errors
- **FR-007**: System MUST maintain backward compatibility with the existing localhost development environment (environment-specific configuration)
- **FR-008**: System MUST NOT include localhost URLs, IP addresses, or server-only environment variables in browser-executable code
- **FR-009**: System MUST successfully handle OPTIONS preflight requests for cross-origin authentication requests with appropriate CORS headers
- **FR-010**: System MUST work with the existing Better Auth implementation without breaking changes to auth logic or user data schema
- **FR-011**: System MUST provide diagnostic logging (temporary) to identify exact failure points during troubleshooting phase
- **FR-012**: System MUST ensure Railway backend environment variables match EXACTLY with required auth, database, and CORS configuration

### Key Entities

- **User**: Represents an individual with credentials attempting to authenticate through the system (username, email, password hash, session tokens)
- **Authentication Request**: Represents a signup/login/logout operation initiated from Vercel frontend targeting Railway backend (credentials, request headers, CORS metadata)
- **Session**: Represents an authenticated user state managed between Vercel frontend and Railway backend (session token, cookies, expiration metadata)
- **Environment Configuration**: Represents the collection of environment variables controlling authentication behavior (auth base URLs, CORS origins, cookie settings)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully complete signup on Vercel production domain with Railway backend in under 10 seconds
- **SC-002**: Users can successfully login on Vercel production domain with Railway backend in under 5 seconds
- **SC-003**: Authenticated users can successfully logout on Vercel production domain with immediate UI state update
- **SC-004**: Zero "Unable to connect to authentication server" errors occur during normal authentication flows on production
- **SC-005**: 100% of authentication requests from Vercel production successfully reach the Railway backend (confirmed via backend logs)
- **SC-006**: Localhost development environment continues to function identically to pre-fix behavior
- **SC-007**: All CORS preflight requests complete successfully with appropriate headers
- **SC-008**: Session persistence works across page refreshes and navigation on Vercel production

## Scope *(mandatory)*

### In Scope

- Systematic investigation using the 8-step troubleshooting strategy to identify root cause
- Fixing URL resolution for authentication requests from Vercel to Railway (environment-specific configuration)
- Correcting environment variable naming and usage for browser-accessible auth configuration (NEXT_PUBLIC_ prefix)
- Configuring CORS on Railway backend for Vercel production domain with credentials support
- Ensuring cookie and credential handling works in production HTTPS context (SameSite, Secure flags)
- Adding temporary diagnostic logging to identify exact failure points during investigation
- Validating that signup, login, and logout work on both localhost and Vercel production
- Maintaining compatibility with Better Auth and existing localhost behavior
- Verifying Railway backend is accessible and responding correctly to health checks
- Ensuring frontend code properly reads and uses environment variables at runtime

### Out of Scope

- Refactoring or moving authentication code to a different directory structure
- Creating a separate frontend project folder (Docusaurus is the root-level app)
- Implementing new authentication methods or providers (OAuth, SSO, etc.)
- Adding mock or temporary authentication bypasses
- Changes to the Better Auth library or configuration beyond what's required for production connectivity
- Performance optimization beyond basic functionality (response times specified in success criteria)
- UI/UX improvements to authentication forms
- Adding new authentication features not related to connectivity
- Database schema changes or migrations
- Moving backend from Railway to another platform
- Implementing rate limiting or advanced security features (unless required to fix connectivity)

## Assumptions *(mandatory)*

- The Railway backend authentication service is operational but may have accessibility or configuration issues from external domains
- Vercel production environment variables are configured but may have incorrect naming (missing `NEXT_PUBLIC_` prefix for browser-accessible variables)
- The `.env.example` file contains the definitive list of required environment variables for the project
- Better Auth is properly configured and works correctly in the localhost environment (validation needed for production)
- The issue affects BOTH localhost AND Vercel production (not just production-specific)
- Network connectivity between Vercel and Railway infrastructure is stable (requires verification via health checks)
- The authentication implementation uses standard HTTP/HTTPS protocols for communication
- Cookies and authorization headers are the primary authentication credential mechanisms (Better Auth standard)
- The codebase uses Docusaurus framework with environment variable restrictions for browser code (NEXT_PUBLIC_ prefix required)
- The frontend does not have a separate project folder—Docusaurus is the root-level application
- Login and Signup are part of the Docusaurus UI (not external pages or separate apps)
- The error "Server not reachable" indicates a network-level failure, not an authentication validation error
- Environment variables may be correctly named but not properly accessed at runtime in browser code

## Dependencies *(include if feature relies on external systems/data)*

### External Dependencies

- **Railway Backend**: Hosts the authentication API and must be accessible from Vercel's infrastructure
- **Vercel Platform**: Hosts the frontend and manages environment variable injection at build and runtime
- **Better Auth Library**: Provides the authentication logic and must remain compatible with configuration changes
- **PostgreSQL on Neon**: Stores user data and sessions (accessed by Railway backend)

### Internal Dependencies

- **Environment Configuration**: Requires correct environment variables in both Vercel and Railway deployments
- **CORS Configuration**: Railway backend must explicitly allow Vercel production domain
- **Cookie/Session Management**: Depends on proper HTTPS cookie handling between domains

## Risks *(include if significant risks exist)*

### Technical Risks

- **Environment Variable Mismatch**: Risk that Vercel and Railway have differently named or missing environment variables
  - *Mitigation*: Conduct thorough audit of both platforms' environment configurations in STEP 2 and STEP 3 before any code changes

- **Backend Unreachable**: Risk that Railway backend is not publicly accessible or has network restrictions
  - *Mitigation*: Verify backend availability using real HTTP requests in STEP 1 before investigating other issues

- **CORS Configuration Complexity**: Risk that strict CORS requirements with credentials cause persistent failures even after configuration changes
  - *Mitigation*: Test CORS configuration in isolation with curl/Postman in STEP 5 before frontend integration

- **Cookie SameSite Restrictions**: Risk that browser SameSite policies block cross-site cookie transmission between Vercel and Railway
  - *Mitigation*: Configure cookies with appropriate SameSite=None and Secure flags for cross-origin scenarios (STEP 7)

- **Runtime vs Build-time Variables**: Risk that environment variables are only available at build time but not at runtime in browser code
  - *Mitigation*: Verify in STEP 4 that variables are accessed at runtime, not just bundled at build time

- **Caching Issues**: Risk that Vercel CDN caches incorrect environment variable values or API responses
  - *Mitigation*: Clear Vercel deployment cache and verify fresh deployments after changes

- **Breaking Localhost**: Risk that production fixes inadvertently break the working localhost environment (if localhost is currently working)
  - *Mitigation*: Use conditional environment detection to maintain separate localhost and production configurations; validate localhost still works after each change

- **Multiple Root Causes**: Risk that the issue is caused by a combination of failures across multiple investigation steps
  - *Mitigation*: Document findings from each step; fix issues incrementally and test after each fix

## Non-Functional Requirements *(include if relevant)*

### Performance

- Authentication requests must complete within 10 seconds for signup and 5 seconds for login under normal network conditions
- Backend must respond to OPTIONS preflight requests within 200ms

### Security

- All authentication traffic must use HTTPS encryption
- Credentials must never be logged or exposed in browser console
- CORS configuration must be restrictive (no wildcard origins with credentials)
- Cookies must use Secure and HttpOnly flags where appropriate

### Reliability

- Authentication service must have 99% uptime on both Vercel and Railway
- Network failures between Vercel and Railway must result in user-friendly error messages
- System must gracefully handle Railway backend temporary unavailability

### Compatibility

- Must work on modern browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
- Must maintain compatibility with Better Auth library
- Must work identically in localhost development environment
