---
id: 0003
title: auth-frontend-ui-planning
stage: plan
date: 2025-12-20
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-auth-frontend-ui
branch: 005-auth-frontend-ui
user: khawaja naqeeb
command: /sp.plan
labels: ["planning", "authentication", "frontend", "architecture"]
links:
  spec: specs/005-auth-frontend-ui/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-auth-frontend-ui/plan.md
tests:
  - Constitution gates: 4/4 PASS
  - Success criteria mapped: 10/10
---

## Prompt

User executed `/sp.plan` with detailed context about the existing project structure, FastAPI backend, Docusaurus frontend, and the goal to create isolated authentication UI components with signup, signin, profile personalization, and RAG chatbot integration.

**Key Context Provided**:
- Frontend: Docusaurus (React-based)
- Backend: FastAPI with PostgreSQL (Neon) + Better Auth
- Existing auth components partially implemented (need updates)
- Constraints: No modifications to existing Docusaurus pages, isolated components only, no hardcoded secrets
- Requirements: 1-hour session timeout, multi-select interests (10 predefined options), logout button in nav bar, manual network retry

## Response snapshot

Created comprehensive implementation plan for authentication frontend UI feature:

**Summary**: Implement frontend authentication UI with isolated React components for signup/signin/profile within existing Docusaurus site. Components exist but require updates: session timeout (1 hour), multi-select interests checkboxes (vs current text input), navigation bar logout button, and manual retry for network errors.

**Technical Context**:
- TypeScript 4.x + React 18 (Docusaurus 3.x)
- LocalStorage for client-side session + profile storage
- Performance goals: Form validation < 500ms, API requests < 3s
- Constraints: No Docusaurus core modifications, 1-hour session timeout, no hardcoded secrets

**Constitution Check**: ✅ ALL 4 GATES PASS
- Gate 1: Fully Spec-Driven Workflow ✅
- Gate 2: Technical Accuracy ✅
- Gate 3: Modular Documentation ✅
- Gate 4: Toolchain Fidelity ✅

**Project Structure**:
- Documentation: spec.md (done), plan.md (created), research.md (Phase 0), data-model.md (Phase 1), contracts/ (Phase 1), quickstart.md (Phase 1), tasks.md (Phase 2)
- Source: frontend/src/components/auth/ (isolated), theme overrides for navbar, .env for configuration

**Phase 0 Research Tasks** (5 tasks identified):
1. Docusaurus theme swizzling best practices for navbar logout button
2. Session timeout implementation patterns with activity tracking
3. Multi-select checkbox component with 10 predefined interests
4. XSS prevention best practices in React
5. Environment variable handling in Docusaurus (NEXT_PUBLIC_ vs standard)

**Phase 1 Design & Contracts**:
- Data Model: UserProfile, SessionState, AuthFormState entities
- API Contracts: POST /auth/signup, POST /auth/signin, GET /auth/profile
- Component Architecture: UserProvider → Layout → Navbar/Content hierarchy
- Quickstart Guide: Local dev setup, env vars, testing checklist

**Key Decisions** (5 documented):
1. Replace text input with multi-select checkboxes for interests (FR-001a compliance)
2. Client-side session timeout with activity tracking + backend validation fallback
3. Simplify password validation to 8-char minimum only (remove letter+number requirement per spec)
4. Research Docusaurus env var naming (likely drop NEXT_PUBLIC_ prefix)
5. Use existing navbar swizzle pattern for logout button

**Risks & Mitigations** (4 identified):
1. Session timeout edge cases → Simple setTimeout + backend validation fallback
2. Theme swizzling conflicts → Minimal wrapper pattern, document changes
3. CORS mismatch → Verify localhost + Vercel domains, test before release
4. LocalStorage unavailable → Detect availability, show warning, fallback to memory

**Success Criteria Verification**: All 10 success criteria (SC-001 to SC-010) mapped to specific architectural decisions and design choices.

## Outcome

- ✅ Impact: Created production-ready implementation plan with complete technical context, architecture, research tasks, data models, API contracts, risk mitigations, and success criteria mapping. Plan balances existing component reuse with spec compliance updates.
- 🧪 Tests: Constitution compliance - 4/4 gates PASS, Success criteria mapping - 10/10 addressed
- 📁 Files: 1 file created (plan.md)
- 🔁 Next prompts: Complete Phase 0 (research.md), Phase 1 (data-model.md, contracts/, quickstart.md), then `/sp.tasks` for implementation tasks
- 🧠 Reflection: Plan identifies critical updates needed for existing components (multi-select interests, session timeout, password validation simplification) while preserving what already works (UserContext pattern, API integration). Five research tasks ensure architectural decisions are validated before implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution gates - PASS (4/4), Technical context completeness - PASS (no NEEDS CLARIFICATION items), Success criteria coverage - PASS (10/10)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to Phase 0 research tasks to resolve unknowns (Docusaurus env vars, session timeout patterns, multi-select implementation)
