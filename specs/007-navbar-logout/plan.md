# Implementation Plan: Navbar Logout Button Integration

**Branch**: `007-navbar-logout` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-navbar-logout/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a visible logout button to the Docusaurus navbar beside the user's email address when authenticated. The current implementation hides the logout button inside a dropdown menu, violating the requirement that users must see a clear, visible logout option next to their email. This corrective fix will modify the CustomLoginLogoutNavbarItem component to display the email and logout button side-by-side in the navbar using Better Auth's existing session management.

## Technical Context

**Language/Version**: TypeScript 5.9.3 (React/TSX components)
**Primary Dependencies**:
- Docusaurus 3.9.2 (@docusaurus/core, @docusaurus/preset-classic)
- React 19.2.7 (via @types/react)
- Better Auth 1.4.7 (authentication - client via custom auth-client.ts)
- Custom auth-client.ts (FastAPI backend integration at `src/lib/auth-client.ts`)
**Storage**: LocalStorage (access tokens, refresh tokens) + FastAPI backend session (PostgreSQL via backend)
**Testing**: Manual testing (no automated test framework currently configured)
**Target Platform**: Web browser (modern browsers supporting ES2020, DOM APIs)
**Project Type**: Web application (Docusaurus static site generator with React components)
**Performance Goals**:
- Logout action completes within 1 second
- Navbar UI updates within 500ms after auth state changes
- No negative impact on page load times
**Constraints**:
- Must use Better Auth's existing session management (via custom auth-client.ts)
- Must follow Docusaurus theming best practices (@theme/NavbarItem pattern)
- Cannot modify RAG chatbot, backend auth, or existing auth flows
- Must preserve existing Docusaurus visual styles
- UI changes limited to navbar only
**Scale/Scope**: Single-component modification (CustomLoginLogoutNavbarItem.tsx)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Fully Spec-Driven Workflow
✅ **PASS** - Specification created at `specs/007-navbar-logout/spec.md` with clear requirements, user scenarios, and success criteria before implementation.

### II. Technical Accuracy, Clarity, and Educational Focus
✅ **PASS** - This is a corrective UI fix, not educational content. Technical accuracy will be maintained by using Better Auth's official APIs and Docusaurus best practices.

### III. Modular Documentation
✅ **PASS** - Change is scoped to a single navbar component (`CustomLoginLogoutNavbarItem.tsx`) following Docusaurus modular theming structure.

### IV. Toolchain Fidelity
✅ **PASS** - Using prescribed tools:
- Spec-Kit Plus for specifications (this plan)
- Docusaurus for site generation (existing setup)
- TypeScript/React for component modification (existing toolchain)
- No new tools or frameworks introduced

### Project Standards & Constraints

**Chapter Structure & Count**: N/A - This is an infrastructure fix, not educational content

**Content Formatting & Code Integrity**: ✅ **PASS** - All code changes will be in TypeScript/TSX following existing patterns in the codebase

**Specification & Generation**: ✅ **PASS** - Following `/sp.specify` → `/sp.plan` → `/sp.tasks` workflow

**Accessibility & Deployment**: ✅ **PASS** - UI changes maintain existing accessibility patterns and Docusaurus deployment configuration remains unchanged

### Summary
**All gates PASS** - No constitution violations. This is a minimal, scoped UI fix following all project standards.

## Project Structure

### Documentation (this feature)

```text
specs/007-navbar-logout/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (this command)
├── data-model.md        # Phase 1 output (this command)
├── quickstart.md        # Phase 1 output (this command)
├── contracts/           # Phase 1 output (this command)
│   └── navbar-api.md    # Component interface contract
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**This is a Web Application** (Docusaurus static site with frontend components only)

```text
src/
├── components/
│   └── auth/
│       ├── AuthContext.tsx          # ✅ Existing - Auth state provider
│       ├── SigninForm.tsx            # ✅ Existing - Not modified
│       ├── SignupForm.tsx            # ✅ Existing - Not modified
│       ├── Profile.tsx               # ✅ Existing - Not modified
│       └── auth.css                  # ✅ Existing - May update for button styles
├── lib/
│   └── auth-client.ts                # ✅ Existing - Better Auth client wrapper (not modified)
├── theme/
│   ├── NavbarItem/
│   │   ├── ComponentTypes.tsx        # ✅ Existing - Navbar item registry
│   │   └── CustomLoginLogoutNavbarItem.tsx  # 🔧 MODIFY - Add visible logout button
│   ├── Layout.tsx                    # ✅ Existing - Not modified
│   └── Root.tsx                      # ✅ Existing - Not modified
└── pages/
    └── auth/                         # ✅ Existing - Auth pages (not modified)

plugins/
└── rag-chatbot/                      # ✅ Existing - Not modified (per spec constraint)

backend/                              # ✅ Existing - Not modified (per spec constraint)
└── src/
    └── api/
        └── routes/
            └── auth.py               # ✅ Existing - Better Auth endpoints (not modified)

docusaurus.config.ts                  # ✅ Existing - Navbar config (already has custom item)
tsconfig.json                         # ✅ Existing - TypeScript config
```

**Structure Decision**: Web application structure selected. This feature modifies only one file:
- **Primary file**: `src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx` (refactor dropdown to show logout button beside email)
- **Optional style update**: `src/components/auth/auth.css` (if button spacing/styling needed)

All other files remain unchanged per spec constraints (FR-014: no modification to auth implementation, RAG chatbot, or backend).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations to track** - All constitution checks passed.
