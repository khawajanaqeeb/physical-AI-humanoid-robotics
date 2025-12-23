# Research & Technology Decisions
## Feature: Docusaurus Better Auth Integration with Profile Personalization

**Created**: 2025-12-21
**Phase**: Planning (Phase 0)
**Status**: Complete

---

## Executive Summary

This document captures all architectural research and technology decisions for integrating authentication into the Docusaurus frontend to work with the existing FastAPI backend authentication system.

**Key Finding**: Better Auth is a TypeScript/Node.js library incompatible with the existing FastAPI (Python) backend. The solution is to use Better Auth **client-side only** for UI/UX while keeping the existing FastAPI JWT authentication backend.

---

## 1. Authentication Architecture Decision

### Problem Statement
The user requested Better Auth integration for both frontend and backend, but:
- Better Auth is a TypeScript/Node.js framework
- The existing backend is FastAPI (Python)
- Backend authentication is already implemented with JWT tokens, PostgreSQL, and user profiles

### Decision: Hybrid Approach (Client-Side Better Auth + FastAPI Backend)

**Rationale**:
1. **Preserve Existing Backend**: The FastAPI backend already has complete authentication (`backend/src/auth/`, `backend/src/users/`)
2. **Leverage Better Auth for UI**: Use Better Auth's React components/hooks for polished frontend UX
3. **Maintain Single Stack**: Avoid introducing a Node.js middleware layer

**Implementation**:
- **Frontend (Docusaurus)**: Use `better-auth/react` for UI components, hooks, and client-side auth state
- **Backend (FastAPI)**: Keep existing JWT authentication with `/auth/signup`, `/auth/signin`, `/auth/signout`, `/auth/refresh` endpoints
- **Integration**: Better Auth client configured to call FastAPI endpoints instead of Better Auth server

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **A: Client-side Better Auth only** | Single backend stack, leverages existing FastAPI auth, Good UX from Better Auth components | Need to adapt Better Auth client to FastAPI API format | ✅ **SELECTED** |
| **B: Add Node.js middleware for Better Auth** | Full Better Auth features, Official Better Auth server integration | Two backend services to deploy/maintain, Increased complexity, Service-to-service auth needed | ❌ Rejected - too complex |
| **C: Remove Better Auth, use Python auth lib** | Simplest architecture, Single technology stack | Need to build auth UI from scratch, No Better Auth UX benefits | ❌ Rejected - loses Better Auth UI value |

---

## 2. Frontend Technology Stack

### Docusaurus Integration Approach

**Decision**: Integrate auth UI as Docusaurus **custom React components and pages**, NOT as a separate application.

**Components**:
1. **Auth Pages** (`src/pages/auth/`):
   - `signup.tsx` - Signup page with background collection
   - `signin.tsx` - Signin page

2. **Auth Components** (`src/components/auth/`):
   - `SignupForm.tsx` - Form with email, password, software/hardware background
   - `SigninForm.tsx` - Email/password form
   - `AuthContext.tsx` - React Context for auth state
   - `UserButton.tsx` - Navbar component showing user email/logout

3. **Custom Navbar Item** (`src/theme/NavbarItem/`):
   - `ComponentTypes.tsx` - Register custom navbar item type
   - `CustomLoginLogoutNavbarItem.tsx` - Login/Logout button for navbar

**Rationale**:
- Docusaurus uses React 18 - compatible with Better Auth React hooks
- Docusaurus supports custom pages (`src/pages/`)
- Docusaurus supports theme swizzling for navbar customization
- No build conflicts - everything runs in same React app

### Better Auth Client Configuration

**Library**: `better-auth` (client-side only)

```typescript
// src/lib/auth-client.ts
import { createAuthClient } from 'better-auth/react'

export const authClient = createAuthClient({
  baseURL: process.env.BACKEND_URL || 'http://localhost:8000',
  // Configure to call FastAPI endpoints
  endpoints: {
    signIn: '/auth/signin',
    signUp: '/auth/signup',
    signOut: '/auth/signout',
    getSession: '/auth/me',
  }
})
```

**Hooks Available**:
- `useSession()` - Get current user session
- `useSignIn()` - Signin mutation
- `useSignUp()` - Signup mutation
- `useSignOut()` - Signout mutation

---

## 3. Session & Token Management

### Token Strategy: JWT with HTTP-Only Cookies

**Decision**: Use HTTP-only cookies for refresh tokens, bearer tokens for access tokens.

**Flow**:
1. User signs in → FastAPI returns `{ access_token, refresh_token, expires_in }`
2. Frontend stores `refresh_token` in HTTP-only cookie (set by backend)
3. Frontend stores `access_token` in memory (React state)
4. All API requests include `Authorization: Bearer {access_token}` header
5. On token expiry, use refresh token to get new access token

**FastAPI Backend** (already implemented):
- Access token expiry: 15 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Refresh token expiry: 7 days (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)
- Tokens signed with `SECRET_KEY` using HS256

**Frontend State Management**:
- **AuthContext** (`src/components/auth/AuthContext.tsx`): React Context Provider
  - Stores: `{ user, accessToken, isAuthenticated, isLoading }`
  - Methods: `signin()`, `signup()`, `signout()`, `refreshToken()`
- **Persistence**: On page load, check for refresh token → call `/auth/refresh` → restore session

---

## 4. RAG Chatbot Access Gating

### Problem Statement
Chatbot must only be accessible to authenticated users. Users clicking the chatbot icon while logged out should be redirected to auth.

### Decision: Client + Server Enforcement

**Client-Side Gating** (`plugins/rag-chatbot/components/ChatWidget.jsx`):
```javascript
function ChatWidget() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const handleChatClick = () => {
    if (!isAuthenticated) {
      // Store return URL
      sessionStorage.setItem('chatbot_return', window.location.pathname)
      navigate('/auth/signin?redirect=chatbot')
      return
    }
    setIsOpen(true)
  }

  return <button onClick={handleChatClick}>...</button>
}
```

**Server-Side Enforcement** (`backend/src/api/routes/query.py`):
- Add `Depends(get_current_user)` to chatbot query endpoint
- Verify JWT token before processing request
- Return 401 Unauthorized if token invalid/missing

**Redirect Flow**:
1. User clicks chatbot icon
2. If unauthenticated: redirect to `/auth/signin?redirect=chatbot`
3. After successful signin: redirect to `/?chatbot=open` (query param triggers chatbot)
4. Frontend reads query param, opens chatbot modal

---

## 5. User Profile & Personalization

### Background Data Collection

**Signup Form Fields**:
1. **Email** (string, required, unique, validated)
2. **Password** (string, required, min 8 chars, validated)
3. **Confirm Password** (string, required, must match password)
4. **Software Background** (enum, required):
   - BEGINNER: "I'm new to programming"
   - INTERMEDIATE: "I have some programming experience"
   - ADVANCED: "I'm an experienced developer"
5. **Hardware Background** (enum, required):
   - NONE: "No hardware/robotics experience"
   - BASIC: "Some electronics or maker experience"
   - ADVANCED: "Experienced with robotics/embedded systems"
6. **Interests** (multi-select checkboxes, optional):
   - Robotics
   - Artificial Intelligence
   - Machine Learning
   - Hardware Design
   - Software Development
   - IoT
   - Computer Vision
   - Natural Language Processing
   - Autonomous Systems
   - Embedded Systems

**Database Schema** (already implemented in `backend/src/users/models.py`):
```python
# users table
id: UUID (PK)
email: String(255) UNIQUE
hashed_password: String(255)
is_active: Boolean
created_at: DateTime
last_login_at: DateTime

# user_profiles table
id: UUID (PK)
user_id: UUID (FK → users.id, CASCADE DELETE)
software_experience: ENUM(BEGINNER, INTERMEDIATE, ADVANCED)
hardware_experience: ENUM(NONE, BASIC, ADVANCED)
interests: JSON (array of strings)
created_at: DateTime
updated_at: DateTime
```

### Personalization Strategy

**1. RAG Chatbot Personalization**:

Inject user background into system prompt when generating responses:

```python
# backend/src/services/personalization_service.py
def get_personalization_context(user_profile: UserProfile) -> str:
    return f"""
    User Background:
    - Software Experience: {user_profile.software_experience.value}
    - Hardware Experience: {user_profile.hardware_experience.value}
    - Interests: {', '.join(user_profile.interests)}

    Tailor your response to match their experience level.
    For beginners, use simple explanations and avoid jargon.
    For advanced users, provide technical depth.
    """

# backend/src/api/routes/query.py (RAG endpoint)
@router.post("/query")
async def query_chatbot(
    query: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = current_user.profile
    personalization_context = get_personalization_context(profile)

    # Inject into RAG prompt
    system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n{personalization_context}"
    response = await rag_service.generate_answer(
        query=query.text,
        system_prompt=system_prompt,
        ...
    )
    return response
```

**2. Docusaurus Book Content Personalization**:

Add conditional rendering based on user background:

```tsx
// src/components/PersonalizedContent.tsx
export function PersonalizedContent({ children, level }) {
  const { user } = useAuth()
  const shouldShow = matchesUserLevel(user?.profile, level)
  return shouldShow ? children : null
}

// In MDX content
<PersonalizedContent level="beginner">
  This section explains basic concepts...
</PersonalizedContent>

<PersonalizedContent level="advanced">
  Advanced implementation details...
</PersonalizedContent>
```

**3. Content Recommendations**:

Homepage widget showing recommended chapters based on background:

```tsx
// src/components/RecommendedChapters.tsx
export function RecommendedChapters() {
  const { user } = useAuth()
  const recommendations = getRecommendations(user?.profile)

  return (
    <div className="recommended-chapters">
      <h3>Recommended for You</h3>
      {recommendations.map(chapter => (
        <ChapterCard key={chapter.id} {...chapter} />
      ))}
    </div>
  )
}
```

---

## 6. Environment Configuration

### Required Environment Variables

**Frontend** (Docusaurus build-time, `.env`):
```bash
# Backend API URL
BACKEND_URL=http://localhost:8000  # Development
BACKEND_URL=https://your-backend.railway.app  # Production

# Public variables (available to browser)
NEXT_PUBLIC_BACKEND_URL=${BACKEND_URL}
```

**Backend** (FastAPI runtime, `.env`):
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Auth secrets
SECRET_KEY=your-secret-key-here  # Used for JWT signing
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,https://physical-ai-humanoid-robotics-e3c7.vercel.app
```

### Deployment Configuration

**Vercel (Frontend)**:
- Build command: `npm run build`
- Output directory: `build`
- Environment variables: Set `BACKEND_URL` in Vercel dashboard

**Railway/Render (Backend)**:
- Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: Set `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`

---

## 7. CORS Configuration

### Problem Statement
Docusaurus (Vercel) and FastAPI (Railway) run on different domains. CORS must be configured to allow authenticated requests.

### Decision: Explicit CORS with Credentials

**FastAPI CORS Middleware** (`backend/src/main.py`):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://physical-ai-humanoid-robotics-e3c7.vercel.app",  # Production
    ],
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Set-Cookie"],
)
```

**Frontend Fetch Configuration**:
```javascript
fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
  },
  credentials: 'include',  // Send cookies cross-origin
  body: JSON.stringify(data),
})
```

---

## 8. Security Considerations

### Password Security
- **Hashing**: Use `passlib[bcrypt]` with 12 rounds (already implemented)
- **Validation**: Min 8 characters, must contain letter and number
- **Storage**: Never log or expose passwords in API responses

### Token Security
- **Access tokens**: Short-lived (15min), stateless JWT
- **Refresh tokens**: Long-lived (7 days), stored in database for revocation
- **HTTP-only cookies**: Prevent XSS attacks on refresh tokens
- **Secure flag**: Enable in production (HTTPS only)

### XSS Prevention
- **Input Sanitization**: Validate and escape all form inputs
- **Content Security Policy**: Set CSP headers in Docusaurus config
- **React**: Built-in XSS protection via JSX escaping

### CSRF Protection
- **SameSite Cookies**: Set `SameSite=Lax` on cookies
- **CORS**: Strict origin checking
- **State-changing operations**: Require valid access token (not just refresh token)

### Rate Limiting
- **FastAPI**: Use `slowapi` for endpoint rate limiting (already implemented)
  - Signup: 5/minute
  - Signin: 5/minute
  - Query: 20/minute per user

---

## 9. Testing Strategy

### Unit Tests
- **Frontend**: Jest + React Testing Library
  - AuthContext state management
  - Form validation logic
  - Token refresh logic

- **Backend**: pytest (already implemented)
  - User creation with profile
  - Token generation and validation
  - Session management

### Integration Tests
- **Auth Flow**: End-to-end signup → signin → chatbot access
- **Token Refresh**: Expired token → refresh → new token
- **Personalization**: User profile → customized RAG response

### Manual Testing Checklist
1. Sign up with all profile options
2. Sign in with correct/incorrect credentials
3. Access chatbot while logged in
4. Access chatbot while logged out (should redirect)
5. Sign out and verify session cleared
6. Token refresh after 15 minutes
7. CORS works on Vercel + Railway
8. Personalized chatbot responses reflect user background

---

## 10. Migration & Rollout Strategy

### Phase 1: Frontend Auth UI (No Breaking Changes)
1. Add auth pages and components to Docusaurus
2. Add login/logout button to navbar
3. Deploy to Vercel (new routes only, existing routes unaffected)

### Phase 2: Chatbot Gating (Feature Flag)
1. Add `CHATBOT_AUTH_REQUIRED` feature flag (default: false)
2. Implement client-side auth check with flag
3. Test with flag enabled
4. Enable flag in production

### Phase 3: Personalization (Gradual Rollout)
1. Add personalization context to RAG service (no UI changes yet)
2. Log personalization effectiveness (A/B test metrics)
3. Add personalized content components to book
4. Monitor user engagement

### Rollback Plan
- **Frontend**: Revert Vercel deployment to previous commit
- **Backend**: Feature flag disables chatbot gating
- **Database**: User/profile tables remain (no data loss)

---

## 11. Success Metrics

### Adoption Metrics
- **Signup Rate**: % of visitors who create accounts
- **Chatbot Usage**: % of authenticated users who use chatbot
- **Session Duration**: Avg time between signin and signout

### Personalization Effectiveness
- **Response Quality**: User feedback on chatbot answers (helpful/not helpful)
- **Engagement**: Users with profiles vs. without profiles - message count
- **Retention**: Return rate of authenticated users

### Technical Metrics
- **Auth Latency**: Signup/signin response time (target: <2s)
- **Token Refresh Success**: % of successful token refreshes
- **Error Rate**: % of failed auth requests (target: <1%)

---

## 12. Dependencies & Prerequisites

### NPM Packages (Frontend)
```json
{
  "dependencies": {
    "better-auth": "^1.0.0",  // Auth client library
    "@docusaurus/core": "^3.9.2",  // Already installed
    "react": "^18.0.0",  // Already installed
    "react-dom": "^18.0.0"  // Already installed
  },
  "devDependencies": {
    "@types/react": "^18.0.0",  // TypeScript support
    "typescript": "^5.0.0"  // TypeScript compiler
  }
}
```

### Python Packages (Backend)
```txt
# Already installed in backend/requirements.txt
fastapi==0.104.1
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
slowapi==0.1.9
```

### Database Migrations
- Migrations already exist in `backend/src/database/migrations/`
- Run `alembic upgrade head` to apply

### External Services
- **PostgreSQL**: Neon serverless Postgres (already configured)
- **Qdrant Cloud**: Vector database for RAG (already configured)
- **Cohere**: LLM API for RAG generation (already configured)

---

## 13. Open Questions & Risks

### Open Questions
1. **Session Timeout**: Should we auto-logout after 1 hour of inactivity? (Spec says yes)
2. **Remember Me**: Do we want a "Remember Me" checkbox for longer sessions? (Not in spec, assume no)
3. **Email Verification**: Should we require email verification before chatbot access? (Not in spec, assume no for MVP)
4. **Password Reset**: Is password reset in scope? (Not in spec, defer to future)

### Risks & Mitigation
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Better Auth API mismatch with FastAPI** | High | Medium | Customize Better Auth client config to map endpoints correctly; test thoroughly |
| **CORS issues in production** | High | Low | Test Vercel + Railway integration early; have fallback to proxy |
| **Token refresh race conditions** | Medium | Low | Implement token refresh locking; use single refresh request |
| **User confusion with redirect flow** | Low | Medium | Clear messaging on chatbot access requirement; smooth redirect UX |

---

## Conclusion

**Architecture Summary**:
- **Frontend**: Docusaurus + Better Auth (client-only) + React Context for auth state
- **Backend**: FastAPI + JWT + PostgreSQL (existing, no changes to core auth logic)
- **Integration**: Better Auth client configured to call FastAPI endpoints
- **Chatbot Gating**: Client + server enforcement with redirect flow
- **Personalization**: Inject user profile into RAG prompts; conditional content rendering

**Next Steps**:
1. ✅ Research complete
2. → Create data-model.md (document existing backend schema)
3. → Create API contracts (OpenAPI spec for auth endpoints)
4. → Create implementation plan template
5. → Generate tasks.md for execution

**Decision Confidence**: HIGH - All major technical unknowns resolved through codebase exploration and Better Auth documentation research.
