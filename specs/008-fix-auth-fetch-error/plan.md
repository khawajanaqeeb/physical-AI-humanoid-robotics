# Implementation Plan: Fix Authentication Fetch Errors

**Branch**: `008-fix-auth-fetch-error` | **Date**: 2025-12-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-fix-auth-fetch-error/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix "Failed to fetch" errors occurring during authentication operations (signup, signin, session check, logout) by addressing environment configuration issues and CORS misconfiguration. The errors are caused by hardcoded localhost URLs in production and likely missing CORS configuration on the backend. The solution involves updating environment variable handling and configuring proper CORS for both local and production environments.

## Technical Context

**Language/Version**: TypeScript 5.9, Python 3.11
**Primary Dependencies**: Docusaurus 3.9.2, FastAPI 0.104+, Better Auth 1.4.7 (not currently used but planned), React 19+
**Storage**: PostgreSQL (Neon) for auth, Qdrant Cloud for RAG, localStorage for JWT tokens (current implementation)
**Testing**: Jest for frontend, pytest for backend
**Target Platform**: Web application (Docusaurus + FastAPI backend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <200ms p95 auth response time, sub-second login experience
**Constraints**: Must not break existing Docusaurus UI, no separate frontend folder, maintain compatibility with main branch
**Scale/Scope**: 10k users, 50 screens (current textbook application)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Compliant with Constitution**:
- Follows fully spec-driven workflow (spec exists and is comprehensive)
- Maintains technical accuracy and clarity focus
- Adheres to modular documentation principles
- Uses prescribed toolchain (Spec-Kit Plus, Claude Code, Docusaurus, GitHub Pages)
- Content formatting targets grade level 8-12 clarity
- Implementation follows Docusaurus best practices

## Project Structure

### Documentation (this feature)

```text
specs/008-fix-auth-fetch-error/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── query.py
│   │   │   └── health.py
│   │   └── middleware/
│   └── main.py
└── tests/

src/
├── lib/
│   ├── auth-client.ts
│   └── config.ts
├── components/
│   └── auth/
│       ├── AuthContext.tsx
│       ├── LoginLogout.tsx
│       ├── Profile.tsx
│       ├── SigninForm.tsx
│       └── SignupForm.tsx
└── pages/
    └── auth/
        └── auth-demo.tsx
```

**Structure Decision**: Web application with separate backend (FastAPI) and frontend (Docusaurus) components. Backend handles authentication and RAG functionality, frontend provides Docusaurus UI with authentication components. The auth-client.ts currently implements custom JWT-based auth instead of Better Auth, which will be addressed in this fix.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
