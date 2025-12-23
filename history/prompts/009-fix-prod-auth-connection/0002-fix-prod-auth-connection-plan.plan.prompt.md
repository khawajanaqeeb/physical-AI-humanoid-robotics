---
id: 0002
title: Fix Prod Auth Connection Plan
stage: plan
date: 2025-12-23
surface: agent
model: claude-sonnet-4-5-20250929
feature: 009-fix-prod-auth-connection
branch: 009-fix-prod-auth-connection
user: naqeeb
command: /sp.plan
labels: ["authentication", "production", "deployment", "vercel", "railway", "cors", "environment-config"]
links:
  spec: specs/009-fix-prod-auth-connection/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-fix-prod-auth-connection/plan.md
tests:
  - Manual production validation (Phase 4)
---

## Prompt

/sp.plan

## Objective
Create a safe, step-by-step implementation plan to fix the production authentication failure on Vercel for the Docusaurus-based project. Authentication works correctly on localhost when both backend and frontend are running, but fails in production with "Unable to connect to authentication server."

## Project Context
- Main UI: Docusaurus (root directory)
- Authentication: Better Auth
- Backend: Separate authentication server
- Frontend hosting: Vercel
- Backend hosting: Publicly deployed service
- Context7 MCP: Enabled
- GitHub MCP: Not connected

## High-Level Plan Goals
1. Verify & discover current deployment state
2. Configure frontend environment (Vercel)
3. Configure backend CORS (Railway)
4. Validate cookie/token security
5. Test production authentication
6. Document deployment process

## Response snapshot

Created comprehensive implementation plan for fixing production authentication connection issue.

**Plan Document**: specs/009-fix-prod-auth-connection/plan.md

**Key Findings from Code Analysis**:
1. Frontend (`src/lib/auth-client.ts`) already has correct logic to read `NEXT_PUBLIC_API_URL` from `process.env`
2. Backend (`backend/src/main.py`) already has CORS middleware correctly configured
3. Backend config (`backend/src/core/config.py`) already parses `cors_origins` from environment
4. Authentication is token-based (localStorage + Bearer headers), not cookie-based

**Root Causes Identified**:
1. Vercel missing `NEXT_PUBLIC_API_URL` environment variable → frontend defaults to localhost
2. Railway `CORS_ORIGINS` likely missing Vercel production domain → CORS blocks requests
3. No code changes needed - only configuration

**Implementation Strategy**:
- **Phase 0**: Confirm backend Railway URL and current production errors
- **Phase 1**: Add `NEXT_PUBLIC_API_URL` to Vercel environment variables
- **Phase 2**: Add Vercel domain to Railway `CORS_ORIGINS`
- **Phase 3**: Verify token-based auth security (no cookie changes needed)
- **Phase 4**: Comprehensive production testing (sign-up, sign-in, sign-out, mobile, cross-browser)
- **Phase 5**: Document deployment checklist and troubleshooting

**Risk**: LOW - Configuration-only changes with clear rollback paths

## Outcome

- ✅ Impact: Created actionable 5-phase implementation plan to fix critical production authentication blocker
- 🧪 Tests: Manual production validation in Phase 4 (sign-up, sign-in, sign-out, cross-browser)
- 📁 Files: Created plan.md with technical context, project structure, implementation phases, risk analysis
- 🔁 Next prompts: Run `/sp.tasks` to generate detailed task breakdown from plan, then execute implementation
- 🧠 Reflection: Plan leverages existing correct code structure - only environment configuration needed. No architectural changes required. Clear acceptance criteria and rollback plans for each phase minimize deployment risk.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan creation successful
- Graders run and results (PASS/FAIL): Constitution check PASS, all technical decisions justified
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Execute Phase 0 to confirm Railway URL and production errors before making any changes
