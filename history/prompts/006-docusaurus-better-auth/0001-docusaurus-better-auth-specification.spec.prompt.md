---
id: 0001
title: Docusaurus Better Auth Specification
stage: spec
date: 2025-12-21
surface: agent
model: claude-sonnet-4-5
feature: 006-docusaurus-better-auth
branch: main
user: NAQEEB
command: /sp.specify
labels: ["authentication", "better-auth", "docusaurus", "fastapi", "personalization", "rag-chatbot"]
links:
  spec: specs/006-docusaurus-better-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-docusaurus-better-auth/spec.md
  - specs/006-docusaurus-better-auth/checklists/requirements.md
tests:
  - Manual validation of spec completeness checklist
  - Architectural clarification resolved (Option A: Better Auth client-side with FastAPI backend)
---

## Prompt

/sp.specify

Project Context:
- Repository (ONLY): https://github.com/khawajanaqeeb/physical-AI-humanoid-robotics
- Branch: main (STRICT — do not create or use any other branch)
- Frontend: Docusaurus (already deployed on Vercel and working)
- Backend: FastAPI
- Existing systems: RAG chatbot, Cohere, Qdrant
- Auth system: https://www.better-auth.com/
- Context7 is enabled and MUST be used

Problem:
- Signup and Signin were implemented only in the backend
- Docusaurus UI does NOT show login/signup
- Auth UI was incorrectly placed outside Docusaurus earlier
- A new git branch was created (this is NOT allowed)

Requirements (STRICT):
1. Use Better Auth for BOTH backend and frontend
2. Learn Better Auth completely using Context7 before coding
3. Implement Signup and Signin UI INSIDE Docusaurus (not a separate frontend)
4. Signup flow MUST ask users about:
   - Software background
   - Hardware background
5. Store this background in the backend user profile
6. Use this background to personalize:
   - Docusaurus book content
   - RAG chatbot responses
7. Do NOT break existing Docusaurus layout or routing
8. Auth must work on:
   - http://localhost:3000
   - https://physical-ai-humanoid-robotics-e3c7.vercel.app
9. No new frontend folders
10. No new repositories
11. No new git branches
12. ALL changes must be committed directly to `main`
13. RAG Chatbot Access Rule:
    - When a user clicks the RAG chatbot icon:
      - If the user is NOT authenticated → redirect to Login/Signup
      - After successful login/signup → redirect back to the RAG chatbot
    - Auth gating must be enforced both in UI and backend

Output expected from /sp.specify:
- Clear understanding of current architecture
- Correct placement of auth UI in Docusaurus
- Clear backend–frontend auth flow
- Auth gating behavior for the RAG chatbot
- User background data flow and storage
- Personalization logic for book and chatbot
- Step-by-step implementation plan
- Explicit confirmation that ONLY the main branch will be used

## Response snapshot

Created feature specification `006-docusaurus-better-auth` directly on the main branch (no feature branch created per user requirements).

**Key Architectural Decision (Resolved via User Clarification)**:
- Better Auth is a TypeScript/Node.js library, but the backend is FastAPI (Python)
- **Selected Approach (Option A)**: Use Better Auth client-side only (React components and hooks from `better-auth/react`) with custom FastAPI authentication endpoints
- Backend will implement JWT/session authentication using Python libraries (python-jose, passlib)
- This maintains the existing FastAPI stack while leveraging Better Auth's frontend UI/UX

**Specification Highlights**:

1. **User Stories (Prioritized P1-P3)**:
   - P1: Unauthenticated chatbot access gating (redirect to auth)
   - P1: New user registration with software/hardware background
   - P1: Existing user sign-in
   - P2: Personalized RAG chatbot responses based on profile
   - P3: Personalized Docusaurus book content
   - P2: Session management and logout

2. **Core Requirements**:
   - FR-001: Better Auth client-side (React components/hooks)
   - FR-001a: Custom FastAPI auth endpoints compatible with Better Auth client
   - FR-001b: JWT/session auth with Python libraries
   - FR-021-026: RAG chatbot access gating (UI + backend enforcement)
   - FR-027-030: Personalization based on user background
   - FR-031-035: Docusaurus integration constraints
   - FR-054-059: FastAPI backend endpoint requirements

3. **Success Criteria**:
   - Users can register with profile in under 2 minutes
   - Users can sign in in under 30 seconds
   - Unauthenticated chatbot access redirects within 500ms
   - 100% of chatbot requests include user profile context
   - Works on both localhost and Vercel deployment

**Validation**:
- All checklist items passed
- No [NEEDS CLARIFICATION] markers remaining
- Specification is ready for `/sp.clarify` or `/sp.plan`

**Files Created**:
- specs/006-docusaurus-better-auth/spec.md
- specs/006-docusaurus-better-auth/checklists/requirements.md

**Work performed on**: main branch (no feature branch created)

## Outcome

- ✅ Impact: Created comprehensive feature specification for Better Auth integration with Docusaurus and FastAPI, including user profile personalization and RAG chatbot access gating
- 🧪 Tests: Specification quality checklist validated (all items passed)
- 📁 Files: Created spec.md and requirements checklist in specs/006-docusaurus-better-auth/
- 🔁 Next prompts: `/sp.clarify` (optional for additional clarifications) or `/sp.plan` (to create implementation plan)
- 🧠 Reflection: Successfully navigated the Better Auth / FastAPI architectural incompatibility by proposing three options and implementing user's choice (client-side Better Auth with custom FastAPI backend). The spec correctly works directly on main branch per strict user requirements.

## Evaluation notes (flywheel)

- Failure modes observed: Initial confusion about creating a feature branch when user explicitly required working on main - resolved by asking for clarification first
- Graders run and results (PASS/FAIL): Spec quality checklist PASS (all items validated)
- Prompt variant (if applicable): Standard /sp.specify workflow with architectural clarification step
- Next experiment (smallest change to try): For future specs with technology incompatibilities, proactively present architecture options earlier in the workflow rather than embedding in FR-001
