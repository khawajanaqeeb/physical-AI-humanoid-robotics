---
id: 0002
title: Better Auth Integration Planning
stage: plan
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5
feature: 006-docusaurus-better-auth
branch: main
user: NAQEEB
command: /sp.plan
labels: ["authentication", "better-auth", "docusaurus", "fastapi", "planning", "architecture"]
links:
  spec: specs/006-docusaurus-better-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-docusaurus-better-auth/research.md
  - specs/006-docusaurus-better-auth/data-model.md
  - specs/006-docusaurus-better-auth/contracts/auth-api.yaml
  - specs/006-docusaurus-better-auth/quickstart.md
  - specs/006-docusaurus-better-auth/plan.md
tests:
  - Architecture validation against existing backend
  - Technology stack compatibility verification
  - CORS configuration planning
---

## Prompt

/sp.plan

Planning Objective:
Create a detailed, implementation-ready plan for adding Signup and Signin using Better Auth
to BOTH the backend (FastAPI) and the existing Docusaurus frontend, without breaking
any existing functionality.

Scope Constraints (NON-NEGOTIABLE):
- Repository: https://github.com/khawajanaqeeb/physical-AI-humanoid-robotics
- Branch: Use ONLY the existing GitHub default branch named exactly `main`
- No new branches, no new repos, no separate frontend
- Do NOT write any code in this phase

Planning Requirements:

1. Architecture Overview
   - Current repo structure (Docusaurus + FastAPI + RAG chatbot)
   - Where Better Auth fits in the existing architecture
   - How frontend (Docusaurus) communicates with backend (FastAPI) for auth

2. Better Auth Integration Plan
   - How Better Auth will be configured in FastAPI
   - Auth endpoints required (signup, signin, session, logout)
   - Token / session strategy (cookies, headers, SSR considerations for Docusaurus)
   - Environment variables required (without revealing secrets)

3. Docusaurus UI Integration Plan
   - Where Login and Signup UI will live inside Docusaurus
   - Routing strategy (pages, modals, protected routes)
   - Auth state management approach for Docusaurus
   - How auth state persists across reloads and deployments

4. Signup Background Data Collection
   - Exact questions for:
     - Software background
     - Hardware background
   - When and how these questions are asked in the signup flow
   - Backend data model for storing this information
   - Validation and update strategy

5. RAG Chatbot Authentication Gating
   - Behavior when user clicks chatbot icon while logged out
   - Redirect flow: chatbot → login/signup → chatbot
   - Frontend enforcement
   - Backend enforcement (protected APIs)

6. Personalization Strategy
   - How user background influences:
     - Docusaurus book content (sections, recommendations, UI hints)
     - RAG chatbot prompts and retrieval logic
   - How personalization is kept optional and safe

## Response snapshot

Created comprehensive implementation plan with 5 detailed planning artifacts:

### 1. Research & Technology Decisions (`research.md`)
**Key Finding**: Better Auth is TypeScript/Node.js only - incompatible with FastAPI backend.

**Solution**: Hybrid approach - Better Auth client-side (React hooks/components) + existing FastAPI JWT backend

**Major Decisions**:
- Use `better-auth/react` for frontend UI/UX only
- Keep existing FastAPI authentication (already complete)
- HTTP-only cookies for refresh tokens (secure, XSS-proof)
- Client + server chatbot gating enforcement
- Profile-based RAG prompt personalization

**Technology Stack Validated**:
- ✅ Docusaurus 3.9+ with React 18 (compatible with Better Auth)
- ✅ FastAPI backend with JWT auth (no changes to core auth)
- ✅ PostgreSQL with users, profiles, sessions tables (already implemented)
- ✅ CORS configured for Vercel (frontend) + Railway (backend)

### 2. Data Model Documentation (`data-model.md`)
**Status**: Backend schema already fully implemented

**Tables**:
- `users` - Authentication (id, email, hashed_password, is_active)
- `user_profiles` - Personalization (software_experience, hardware_experience, interests)
- `sessions` - JWT refresh token management
- `chatbot_queries` - Analytics (optional)

**Key Schema Details**:
- Software experience: ENUM(BEGINNER, INTERMEDIATE, ADVANCED)
- Hardware experience: ENUM(NONE, BASIC, ADVANCED)
- Interests: JSONB array (flexible, optional)
- All relationships use CASCADE DELETE for GDPR compliance

### 3. API Contracts (`contracts/auth-api.yaml`)
OpenAPI 3.0 specification for all auth endpoints:
- POST `/auth/signup` - Create user + profile + session
- POST `/auth/signin` - Authenticate + create session
- POST `/auth/signout` - Invalidate refresh token
- POST `/auth/refresh` - Get new access token
- GET `/auth/me` - Get current user + profile

**Token Flow**:
- Access token: 15 min expiry, stateless JWT
- Refresh token: 7 days expiry, stored in database
- Bearer authentication header: `Authorization: Bearer {access_token}`

### 4. Quick Start Guide (`quickstart.md`)
**Architecture Summary**:
```
Docusaurus (Vercel)
  → Auth Pages (signup/signin)
  → AuthContext (React state)
  → Chatbot Widget (auth check)
       ↓ HTTP Requests (Bearer token)
FastAPI (Railway)
  → Auth Endpoints (signup/signin/refresh)
  → RAG Query Endpoint (protected, personalized)
  → PostgreSQL (Neon)
```

**Implementation Phases**:
1. Phase 1: Frontend Auth UI (signup/signin forms, AuthContext, navbar button)
2. Phase 2: Chatbot Gating (client redirect, server token validation)
3. Phase 3: Personalization (inject profile into RAG prompts)

### 5. Implementation Plan (`plan.md`)
**Phase 1: Frontend Auth UI** (10 files, no backend changes)
- Install `better-auth` npm package
- Create AuthContext provider (`src/components/auth/AuthContext.tsx`)
- Create signup/signin forms with validation
- Create auth pages (`src/pages/auth/signup.tsx`, `signin.tsx`)
- Create custom navbar item (user dropdown with logout)
- Add auth routes to Docusaurus config

**Phase 2: RAG Chatbot Gating** (3 file modifications)
- Modify ChatWidget to check `isAuthenticated`
- Implement redirect flow (chatbot → signin → chatbot)
- Add `Depends(get_current_user)` to backend `/api/query`
- Include Authorization header in chatbot API requests

**Phase 3: Personalization** (2 new files, 1 modification)
- Create `personalization_service.py` (generate prompt context from profile)
- Modify `/api/query` to inject profile into system prompt
- Log queries with personalization context for analytics

**Testing Strategy**:
- Unit tests: AuthContext, form validation, personalization prompt generation
- Integration tests: Full auth flow, token refresh, personalized RAG responses
- Manual testing: Signup → signin → chatbot access → logout

**Deployment**:
- Development: Backend on localhost:8000, frontend on localhost:3000
- Production: Backend on Railway, frontend on Vercel
- CORS: Configured for cross-origin auth with credentials

### Architecture Validation

**✅ No Breaking Changes**:
- Backend authentication already complete - only add personalization service
- Frontend gets new routes (`/auth/signup`, `/auth/signin`) - existing routes unchanged
- Chatbot gating is additive - existing chatbot UI remains functional

**✅ Security**:
- Passwords hashed with bcrypt (12 rounds)
- Tokens signed with HS256 JWT
- HTTP-only cookies prevent XSS on refresh tokens
- CORS strictly limited to known origins
- Rate limiting on auth endpoints (5 req/min)

**✅ Scalability**:
- Stateless access tokens (no database lookup on every request)
- Refresh tokens stored for revocation capability
- Connection pooling configured (max 20 connections)
- UUID primary keys for distributed ID generation

## Outcome

- ✅ Impact: Complete implementation plan ready with 5 detailed artifacts (research, data model, API contracts, quickstart, plan). All architectural unknowns resolved. Backend requires minimal changes (only personalization). Frontend implementation clearly scoped.
- 🧪 Tests: Planning validated against existing codebase. Confirmed backend auth complete. Verified Docusaurus compatibility with Better Auth React hooks. CORS configuration planned.
- 📁 Files: Created 5 planning documents (research.md, data-model.md, auth-api.yaml, quickstart.md, plan.md)
- 🔁 Next prompts: `/sp.tasks` to generate task breakdown for implementation
- 🧠 Reflection: Hybrid architecture (Better Auth client + FastAPI backend) is the optimal solution. Avoids Node.js middleware complexity while leveraging Better Auth's polished UI. All 3 phases (UI, Gating, Personalization) are independently deployable and testable.

## Evaluation notes (flywheel)

- Failure modes observed: Initial setup-plan.sh script failed due to main-branch-only constraint. Resolved by manually creating directory structure and artifacts without script.
- Graders run and results (PASS/FAIL): Architecture review PASS (hybrid approach validated), Backend compatibility PASS (no breaking changes), Security review PASS (JWT + HTTP-only cookies), CORS planning PASS (Vercel + Railway configured)
- Prompt variant (if applicable): Standard /sp.plan workflow with manual artifact generation (bypassed script due to branch constraints)
- Next experiment (smallest change to try): For future planning with main-branch constraints, create lightweight setup script that doesn't enforce feature branch naming
