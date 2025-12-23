# Quick Start Guide
## Docusaurus Better Auth Integration

**Last Updated**: 2025-12-21
**Target Audience**: Developers implementing the authentication feature

---

## Overview

This guide provides a quick walkthrough of the authentication integration architecture and implementation approach.

**What's Being Built**:
- Signup/Signin UI inside Docusaurus (React pages and components)
- Integration with existing FastAPI backend authentication
- RAG chatbot access gating (auth required)
- Personalized chatbot responses based on user profile

**What's Already Done**:
- ✅ FastAPI backend with complete authentication (`/auth/signup`, `/signin`, `/signout`, `/refresh`)
- ✅ PostgreSQL database with users, profiles, sessions tables
- ✅ JWT token generation and validation
- ✅ User profile schema (software/hardware experience, interests)
- ✅ RAG chatbot plugin in Docusaurus

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    Docusaurus Frontend                      │
│                    (Vercel Deployment)                      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Auth Pages   │  │ Auth Context │  │ Chatbot Widget  │ │
│  │              │  │              │  │                 │ │
│  │ - signup.tsx │  │ - useAuth()  │  │ - Auth Check    │ │
│  │ - signin.tsx │  │ - signin()   │  │ - Redirect Flow │ │
│  └──────────────┘  │ - signup()   │  └─────────────────┘ │
│                     │ - signout()  │                       │
│                     └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Requests
                              │ (Authorization: Bearer <token>)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│                    (Railway Deployment)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Auth Endpoints                                       │ │
│  │ POST /auth/signup → Create user + profile + session │ │
│  │ POST /auth/signin → Authenticate + create session   │ │
│  │ POST /auth/signout → Invalidate session             │ │
│  │ POST /auth/refresh → New access token               │ │
│  │ GET  /auth/me → Get user + profile                  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ RAG Chatbot Endpoints (Protected)                   │ │
│  │ POST /api/query → Generate answer with              │ │
│  │                   personalized context               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────┐                                          │
│  │  PostgreSQL  │                                          │
│  │              │                                          │
│  │  - users     │                                          │
│  │  - profiles  │                                          │
│  │  - sessions  │                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Authentication Flow

### 1. User Signup

```
User → Signup Page → Fill Form (email, password, background)
     → Submit → POST /auth/signup
     → Backend creates user + profile + session
     → Returns access_token + refresh_token
     → Frontend stores in AuthContext
     → Redirect to chatbot
```

**Key Files**:
- Frontend: `src/pages/auth/signup.tsx`, `src/components/auth/SignupForm.tsx`
- Backend: `backend/src/auth/routes.py:signup()`

### 2. User Signin

```
User → Signin Page → Enter email + password
     → Submit → POST /auth/signin
     → Backend validates credentials
     → Returns access_token + refresh_token
     → Frontend stores in AuthContext
     → Redirect to chatbot
```

**Key Files**:
- Frontend: `src/pages/auth/signin.tsx`, `src/components/auth/SigninForm.tsx`
- Backend: `backend/src/auth/routes.py:signin()`

### 3. Chatbot Access (Authenticated)

```
User clicks chatbot icon → Check isAuthenticated
     → If YES: Open chatbot modal
     → User asks question → POST /api/query with Authorization header
     → Backend validates token → Fetches user profile
     → Injects profile into RAG prompt → Generates personalized answer
     → Returns response to frontend
```

**Key Files**:
- Frontend: `plugins/rag-chatbot/components/ChatWidget.jsx`
- Backend: `backend/src/api/routes/query.py`, `backend/src/services/personalization_service.py`

### 4. Chatbot Access (Unauthenticated)

```
User clicks chatbot icon → Check isAuthenticated
     → If NO: Store current URL in sessionStorage
     → Redirect to /auth/signin?redirect=chatbot
     → After signin: Redirect back to chatbot (open modal)
```

**Key Files**:
- Frontend: `plugins/rag-chatbot/components/ChatWidget.jsx`, `src/components/auth/AuthContext.tsx`

### 5. Token Refresh

```
Frontend makes API request → 401 Unauthorized (token expired)
     → Interceptor catches 401 → POST /auth/refresh with refresh_token
     → Backend validates refresh token → Returns new access_token + refresh_token
     → Frontend updates AuthContext → Retry original request
```

**Key Files**:
- Frontend: `src/lib/api-client.ts` (axios interceptor)
- Backend: `backend/src/auth/routes.py:refresh_token()`

---

## File Structure

### Frontend (Docusaurus)

```
/
├── src/
│   ├── components/
│   │   └── auth/
│   │       ├── AuthContext.tsx          # React Context for auth state
│   │       ├── SignupForm.tsx           # Signup form component
│   │       ├── SigninForm.tsx           # Signin form component
│   │       ├── UserButton.tsx           # User dropdown (email, logout)
│   │       └── auth.css                 # Auth component styles
│   │
│   ├── pages/
│   │   └── auth/
│   │       ├── signup.tsx               # Signup page
│   │       └── signin.tsx               # Signin page
│   │
│   ├── theme/
│   │   └── NavbarItem/
│   │       ├── ComponentTypes.tsx       # Register custom navbar items
│   │       └── CustomLoginLogoutNavbarItem.tsx
│   │
│   └── lib/
│       ├── auth-client.ts               # Better Auth client config
│       └── api-client.ts                # Axios instance with auth interceptor
│
├── plugins/
│   └── rag-chatbot/
│       ├── components/
│       │   ├── ChatWidget.jsx           # Modified with auth check
│       │   └── ChatModal.jsx            # Chatbot modal
│       └── hooks/
│           └── useAuth.js               # Auth hook for chatbot
│
├── package.json                         # Add better-auth dependency
├── .env                                 # BACKEND_URL config
└── docusaurus.config.ts                 # Navbar config (custom item)
```

### Backend (FastAPI)

**Already Implemented** - No changes needed except:
- Add personalization service (`src/services/personalization_service.py`)
- Modify RAG query endpoint to inject user context (`src/api/routes/query.py`)

```
backend/
├── src/
│   ├── auth/
│   │   ├── routes.py                    # ✅ Signup, signin, signout, refresh
│   │   ├── schemas.py                   # ✅ Request/response schemas
│   │   ├── security.py                  # ✅ Password hashing, token creation
│   │   └── dependencies.py              # ✅ get_current_user dependency
│   │
│   ├── users/
│   │   ├── models.py                    # ✅ User, UserProfile, Session models
│   │   └── services.py                  # ✅ User CRUD operations
│   │
│   ├── services/
│   │   ├── personalization_service.py   # ⚠️ NEW: Profile → prompt context
│   │   └── rag_service.py               # ✅ Existing RAG service
│   │
│   └── api/
│       └── routes/
│           └── query.py                 # ⚠️ MODIFY: Add personalization
│
├── .env                                 # SECRET_KEY, DATABASE_URL, CORS_ORIGINS
└── requirements.txt                     # All dependencies already listed
```

---

## Implementation Phases

### Phase 1: Frontend Auth UI (No Backend Changes)
**Goal**: Add signup/signin pages and auth state management

1. Install `better-auth` package
2. Create AuthContext provider
3. Create signup/signin forms
4. Add auth pages (`/auth/signup`, `/auth/signin`)
5. Add custom navbar item (Login/Logout button)
6. Test auth flow end-to-end

**Deliverables**:
- Users can sign up and sign in
- Tokens stored in AuthContext
- Login/Logout button in navbar
- No breaking changes to existing site

### Phase 2: Chatbot Access Gating
**Goal**: Require authentication for chatbot access

1. Modify `ChatWidget.jsx` to check `isAuthenticated`
2. Implement redirect flow (chatbot → signin → chatbot)
3. Add `Depends(get_current_user)` to `/api/query` endpoint
4. Test auth enforcement (frontend + backend)

**Deliverables**:
- Unauthenticated users redirected to signin
- Authenticated users can access chatbot
- Backend validates tokens on query endpoint

### Phase 3: Personalization
**Goal**: Tailor chatbot responses based on user profile

1. Create `personalization_service.py`
2. Modify `/api/query` to inject profile context
3. Test personalization (beginner vs. advanced responses)
4. Add optional personalized content to Docusaurus pages

**Deliverables**:
- Chatbot responses reflect user's software/hardware background
- Analytics track personalization effectiveness

---

## Environment Setup

### Development

**Frontend** (`.env`):
```bash
BACKEND_URL=http://localhost:8000
```

**Backend** (`backend/.env`):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000
```

**Run Development Servers**:
```bash
# Terminal 1: Backend
cd backend
python -m uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
npm start
```

### Production

**Vercel** (Frontend):
- Set environment variable: `BACKEND_URL=https://your-backend.railway.app`
- Deploy command: `npm run build`

**Railway** (Backend):
- Set environment variables: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`
- Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

---

## Testing Checklist

### Manual Testing

- [ ] Signup with all profile options (BEGINNER, INTERMEDIATE, ADVANCED)
- [ ] Signin with correct credentials
- [ ] Signin with incorrect credentials (should show error)
- [ ] Access chatbot while logged in (should open)
- [ ] Access chatbot while logged out (should redirect to signin)
- [ ] Signout and verify session cleared
- [ ] Token refresh after 15 minutes (auto-refresh on 401)
- [ ] CORS works between Vercel and Railway
- [ ] Personalized chatbot responses (beginner vs. advanced)

### Automated Testing

- [ ] Unit tests: AuthContext state management
- [ ] Unit tests: Form validation logic
- [ ] Integration tests: Signup → signin → chatbot access
- [ ] Integration tests: Token refresh flow
- [ ] E2E tests: Complete user journey (Cypress/Playwright)

---

## Common Issues & Solutions

### Issue 1: CORS Errors in Production
**Symptom**: Network errors when calling backend from Vercel

**Solution**:
- Verify `CORS_ORIGINS` includes `https://physical-ai-humanoid-robotics-e3c7.vercel.app`
- Check FastAPI CORS middleware in `src/main.py`
- Ensure `credentials: 'include'` in fetch requests

### Issue 2: Token Refresh Loop
**Symptom**: Infinite redirect loop on token expiry

**Solution**:
- Check interceptor logic in `api-client.ts`
- Ensure refresh token is valid and not expired
- Add flag to prevent multiple concurrent refresh requests

### Issue 3: Better Auth Client API Mismatch
**Symptom**: Better Auth client expects different response format

**Solution**:
- Customize Better Auth client config to map endpoints
- Ensure backend responses match expected schema
- Use adapter pattern if needed

---

## Next Steps

1. ✅ **Planning Complete** (this document)
2. → **Implement Phase 1** (Frontend Auth UI)
3. → **Implement Phase 2** (Chatbot Gating)
4. → **Implement Phase 3** (Personalization)
5. → **Deploy to Production**
6. → **Monitor & Iterate**

---

## Resources

- **Backend API Docs**: `specs/006-docusaurus-better-auth/contracts/auth-api.yaml`
- **Data Model**: `specs/006-docusaurus-better-auth/data-model.md`
- **Research**: `specs/006-docusaurus-better-auth/research.md`
- **Feature Spec**: `specs/006-docusaurus-better-auth/spec.md`

- **Better Auth Docs**: https://www.better-auth.com/docs
- **Docusaurus Docs**: https://docusaurus.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

**Ready to start implementation?** Proceed to `/sp.tasks` to generate the task breakdown!
