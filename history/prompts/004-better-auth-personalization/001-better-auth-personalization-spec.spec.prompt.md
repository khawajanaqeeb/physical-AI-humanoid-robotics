---
id: 001
title: Better Auth Personalization Spec
stage: spec
date: 2025-12-20
surface: agent
model: claude-sonnet-4-5
feature: 004-better-auth-personalization
branch: main
user: khawaja naqeeb
command: /sp.specify
labels: ["authentication", "personalization", "better-auth", "rag", "user-profiles"]
links:
  spec: specs/004-better-auth-personalization/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-better-auth-personalization/spec.md
  - specs/004-better-auth-personalization/checklists/requirements.md
tests:
  - Specification quality validation against completeness checklist
  - Technology-agnostic success criteria verification
  - Functional requirements testability review
---

## Prompt

You are a senior full-stack engineer and AI systems architect.

PROJECT OVERVIEW
This repository hosts an educational project titled "Physical AI & Humanoid Robotics".
It includes:
- A Docusaurus-based textbook deployed on Vercel
- A Retrieval-Augmented Generation (RAG) chatbot
- A FastAPI backend
- Qdrant for vector search
- Cohere for embeddings / generation

Repository:
https://github.com/khawajanaqeeb/physical-AI-humanoid-robotics

IMPORTANT:
- The default and active branch of this repository is `main`
- All changes must be committed and pushed to the `main` branch
- Do NOT create or push to any other branch

Live Docusaurus book URL (READ-ONLY CONTEXT ONLY):
https://physical-ai-humanoid-robotics-e3c7.vercel.app

⚠️ CONSTRAINT:
- The Docusaurus site is provided for contextual understanding only
- Do NOT modify Docusaurus content, configuration, or layout
- Do NOT scrape or crawl the site

--------------------------------------------------
CURRENT TECH STACK (ALREADY IMPLEMENTED & STABLE)
--------------------------------------------------
Backend:
- FastAPI (Python)

AI / RAG:
- OpenAI Agents / ChatKit SDK
- Qdrant (vector database)
- Cohere (embeddings / LLM)

Frontend:
- Docusaurus (Vercel deployment)
- Existing chatbot UI already connected to backend

Configuration:
- All existing API keys and service URLs are already present in `.env`
- Existing keys include (DO NOT TOUCH):
  - COHERE_API_KEY
  - QDRANT_URL
  - QDRANT_API_KEY
  - CORS_ORIGINS

CORS is already configured as:
CORS_ORIGINS=https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000

--------------------------------------------------
OBJECTIVE (BONUS FEATURE IMPLEMENTATION)
--------------------------------------------------
Implement user authentication and personalization WITHOUT breaking existing functionality.

Participants can earn bonus points by:
1. Implementing Signup and Signin using Better Auth
2. Collecting user background information at signup
3. Personalizing RAG chatbot responses based on user background

--------------------------------------------------
AUTHENTICATION REQUIREMENTS
--------------------------------------------------
Auth framework:
- Use Better Auth (https://www.better-auth.com/)
- Better Auth is a library, NOT a hosted SaaS
- No Better Auth account or API key is required

Database:
- PostgreSQL hosted on Neon
- Used ONLY for:
  - Auth users
  - Sessions
  - User profiles

New environment variables to add (ONLY THESE):
- DATABASE_URL
- BETTER_AUTH_SECRET

Rules:
- Read secrets from `.env`
- Update `.env.example` with placeholders
- NEVER commit real secrets
- Do NOT modify existing env keys

--------------------------------------------------
SIGNUP FLOW REQUIREMENTS
--------------------------------------------------
During Signup, collect and persist the following:
- Software experience level (Beginner / Intermediate / Advanced)
- Hardware / Robotics experience (None / Basic / Advanced)
- Optional interests (AI, Robotics, APIs, ML, etc.)

Data handling:
- Store this information in PostgreSQL
- Link it to the authenticated user
- Use clean, normalized schema design
- Migrations must be safe and reversible

--------------------------------------------------
PERSONALIZATION REQUIREMENTS (CRITICAL)
--------------------------------------------------
Existing RAG logic MUST remain intact.

Enhancement:
- When a logged-in user sends a chatbot query:
  1. Authenticate the session
  2. Fetch the user's profile from PostgreSQL
  3. Inject profile context into the RAG system prompt

Examples:
- Beginner users → simple explanations, fewer technical terms
- Advanced users → technical depth, formulas, robotics examples

Constraints:
- Do NOT re-embed documents
- Do NOT modify Qdrant schema
- Do NOT change Cohere usage
- Personalization must be additive only

--------------------------------------------------
BACKEND ARCHITECTURE EXPECTATIONS
--------------------------------------------------
Extend the existing FastAPI backend (NO new backend URL).

Recommended folder additions:
- auth/
  - better_auth.py
  - routes.py
- users/
  - models.py
  - services.py
  - routes.py

Principles:
- Clear separation of concerns
- Auth logic isolated from RAG logic
- Defensive error handling
- Production-grade code quality

--------------------------------------------------
GIT & VERSION CONTROL REQUIREMENTS
--------------------------------------------------
You MUST:
- Work directly on the `main` branch
- Create new files and folders as needed
- Modify existing files ONLY if required
- Commit with clear, professional commit messages
- Push all changes to:
  https://github.com/khawajanaqeeb/physical-AI-humanoid-robotics

Example commit messages:
- feat(auth): integrate Better Auth with FastAPI
- feat(profile): add user background schema
- feat(rag): personalize responses using user profile

--------------------------------------------------
NON-NEGOTIABLE CONSTRAINTS
--------------------------------------------------
- DO NOT break existing RAG functionality
- DO NOT refactor unrelated code
- DO NOT remove existing endpoints

## Response snapshot

Created comprehensive feature specification for Better Auth authentication and personalized RAG chatbot feature as `specs/004-better-auth-personalization/spec.md`.

**Key Deliverables**:

1. **Feature Specification** (specs/004-better-auth-personalization/spec.md):
   - 4 prioritized user stories (P1-P3) covering complete user journey
   - 27 testable functional requirements (FR-001 to FR-027)
   - 12 measurable, technology-agnostic success criteria
   - 4 key entities defined (User, UserProfile, Session, ChatbotQuery)
   - 8 edge cases identified for robust implementation
   - Zero [NEEDS CLARIFICATION] markers - all requirements clearly specified

2. **Quality Checklist** (specs/004-better-auth-personalization/checklists/requirements.md):
   - All validation items PASSED
   - Confirmed no implementation details in spec
   - Verified all requirements are testable and unambiguous
   - Validated success criteria are measurable and technology-agnostic
   - Ready for `/sp.plan` phase

**User Story Priorities**:
- **P1** (Critical): Account creation and signin - foundational capabilities
- **P2** (High Value): Personalized chatbot interactions - core value proposition
- **P3** (Enhancement): Profile management - quality of life improvement

**Scope Boundaries**:
- IN SCOPE: Better Auth integration, user profiles (experience levels + interests), prompt-based personalization
- OUT OF SCOPE: Password reset, email verification, OAuth providers, profile picture uploads
- CONSTRAINTS: Zero changes to Qdrant schema, Cohere usage, or existing RAG retrieval logic

**Next Steps**:
Ready to proceed with `/sp.clarify` (if needed) or `/sp.plan` to design implementation architecture.

## Outcome

- ✅ Impact: Complete, validated specification ready for architectural planning. Establishes clear requirements for authentication and personalization without breaking existing RAG functionality.
- 🧪 Tests: Specification quality validation completed - all checklist items passed. 27 functional requirements verified as testable and unambiguous. 12 success criteria confirmed as measurable and technology-agnostic.
- 📁 Files: Created 2 files - specs/004-better-auth-personalization/spec.md (comprehensive feature specification) and specs/004-better-auth-personalization/checklists/requirements.md (validation checklist with PASSED status)
- 🔁 Next prompts: `/sp.plan` to design Better Auth integration architecture, database schema, and personalization prompt injection strategy. Optional: `/sp.clarify` if additional requirements discovery needed.
- 🧠 Reflection: Specification successfully maintains technology-agnostic language while providing concrete, testable requirements. Prioritized user stories enable incremental delivery (P1 auth first, then P2 personalization). Edge cases proactively identify potential failure scenarios.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification creation completed without clarification requests, all requirements derived from detailed user input
- Graders run and results (PASS/FAIL): PASS - All specification quality checklist items validated. Zero implementation details, all requirements testable, success criteria measurable and technology-agnostic
- Prompt variant (if applicable): Standard /sp.specify workflow with comprehensive user input containing explicit constraints and requirements
- Next experiment (smallest change to try): Consider adding acceptance criteria for profile validation edge cases (e.g., contradictory experience levels) to strengthen FR-027
