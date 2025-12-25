---
id: 0001
title: Fix Prod Auth Connection
stage: spec
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-fix-prod-auth
branch: 001-fix-prod-auth
user: khawajanaqeeb
command: /sp.specify
labels: ["authentication", "production", "vercel", "railway", "cors", "environment-variables"]
links:
  spec: specs/001-fix-prod-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-fix-prod-auth/spec.md
  - specs/001-fix-prod-auth/checklists/requirements.md
tests:
  - none
---

## Prompt

## 🚨 PRODUCTION-ONLY AUTH FAILURE (Vercel + Railway)

### Project
- GitHub (main branch): https://github.com/khawajanaqeeb/physical-AI-humanoid-robotics
- Frontend (Vercel): https://physical-ai-humanoid-robotics-e3c7.vercel.app
- Backend / Auth / RAG API (Railway): https://physical-ai-humanoid-robotics-production-e742.up.railway.app

### Error (Production Only)
> "Unable to connect to authentication server. Please check your internet connection and try again."

✔️ Works perfectly on localhost
❌ Fails only on Vercel production domain

---

## NON-NEGOTIABLE CONSTRAINTS
1. DO NOT break or refactor working localhost logic
2. DO NOT move auth code out of the Docusaurus root
3. DO NOT create a separate frontend folder
4. DO NOT assume missing environment variables
5. DO NOT add mock or temporary auth
6. MUST remain compatible with **Better Auth**
7. All fixes must be committed to **GitHub `main` branch**
8. Final solution must work on **Vercel + Railway**

---

## REQUIRED INVESTIGATION (MANDATORY)

### 1️⃣ AUTH BASE URL RESOLUTION (CRITICAL)
- Inspect every auth-related fetch / axios call
- Detect and FIX:
  - relative URLs that work on localhost but fail on Vercel
  - any usage of `localhost`, `127.0.0.1`, or server-only env vars in browser code
- Enforce a **single, explicit, production-safe auth base URL**
- Ensure frontend reads it via `NEXT_PUBLIC_*` env variables only

---

### 2️⃣ ENVIRONMENT VARIABLE RUNTIME AUDIT
- Compare:
  - `.env`
  - Vercel Production env
  - actual runtime usage in browser
- Identify env vars that:
  - exist in Vercel but are not readable in frontend
  - are incorrectly named (missing `NEXT_PUBLIC_`)
- Fix naming and usage WITHOUT changing variable values

---

### 3️⃣ CORS + AUTH CREDENTIALS (PRODUCTION SAFE)
On Railway backend:
- CORS must allow exactly:
https://physical-ai-humanoid-robotics-e3c7.vercel.app

- Confirm:
- credentials enabled
- cookies / headers allowed
- no wildcard CORS with credentials
- Ensure preflight OPTIONS requests succeed

---

### 4️⃣ COOKIE / TOKEN BEHAVIOR (DEV VS PROD)
Explicitly validate:
- Secure cookies required in HTTPS
- SameSite policy compatibility
- Authorization headers vs cookies
- Vercel Node vs Edge runtime compatibility

Fix ONLY what breaks production.

---

### 5️⃣ NETWORK-LEVEL VERIFICATION
Add TEMPORARY diagnostics (remove after fix):
- Log auth request URL + status on frontend
- Log incoming auth requests on backend
- Confirm whether auth requests reach Railway from Vercel

---

## REQUIRED DELIVERABLES
Claude MUST:
1. Identify the **exact root cause** (not a guess)
2. Apply minimal, targeted fixes
3. Show file-by-file changes
4. Remove temporary logs
5. Ensure:
 - signup works
 - login works
 - logout button appears in navbar
6. Commit all fixes to `main`

---

## SUCCESS CRITERIA
✅ No "Unable to connect to authentication server" error
✅ Auth works on Vercel production
✅ Localhost behavior unchanged
✅ Clean production deployment

END.

## Response snapshot

Created comprehensive feature specification for fixing production-only authentication failure between Vercel frontend and Railway backend.

**Branch Created**: `001-fix-prod-auth`

**Key Deliverables**:
1. Complete feature specification (specs/001-fix-prod-auth/spec.md)
2. Quality validation checklist (specs/001-fix-prod-auth/checklists/requirements.md)

**Specification Highlights**:
- Three prioritized user stories (P1: Signup, P1: Login, P2: Logout)
- 10 functional requirements covering URL resolution, environment variables, CORS, cookies, and Better Auth compatibility
- 8 measurable success criteria with specific metrics (10s signup, 5s login, zero connection errors)
- Clear scope boundaries (in/out of scope explicitly defined)
- Technical risks identified with mitigation strategies
- All requirements testable and unambiguous
- Zero [NEEDS CLARIFICATION] markers - specification is complete

**Validation Results**: All quality checklist items PASSED
- Content is technology-agnostic and user-focused
- Requirements are testable and unambiguous
- Success criteria are measurable without implementation details
- Edge cases and dependencies documented

**Feature is ready for**: `/sp.clarify` or `/sp.plan`

## Outcome

- ✅ Impact: Created production-critical specification addressing authentication connectivity failure affecting all users on Vercel deployment
- 🧪 Tests: None (specification phase - no code changes)
- 📁 Files: Created spec.md and requirements.md checklist
- 🔁 Next prompts: "/sp.plan to create architectural design" or "/sp.clarify if requirements need refinement"
- 🧠 Reflection: Specification focuses on root cause investigation (URL resolution, env vars, CORS, cookies) with strict constraints to avoid breaking working localhost. All requirements are concrete and testable.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification completed successfully with all validation checks passing
- Graders run and results (PASS/FAIL): Quality checklist PASS on all 14 criteria
- Prompt variant (if applicable): Standard sp.specify workflow
- Next experiment (smallest change to try): Proceed to /sp.plan for implementation planning
