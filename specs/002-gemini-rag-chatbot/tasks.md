# Tasks: Gemini-Powered RAG Chatbot for Docusaurus Book

**Input**: Design documents from `/specs/002-gemini-rag-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the specification - tests are OPTIONAL and not included in this task list.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US0=Ingestion, US1=Q&A, US2=Discovery, US3=Multi-turn)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `frontend/src/`
- All paths follow plan.md project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure (backend/src/{models,services,api/endpoints,db}, backend/tests, backend/scripts)
- [ ] T002 Create frontend directory structure (frontend/src/{components,services,types}, frontend/tests)
- [ ] T003 Initialize Python virtual environment and install dependencies in backend/requirements.txt
- [ ] T004 [P] Create backend/.env.example with required environment variables (GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL)
- [ ] T005 [P] Initialize npm project in frontend/ with package.json dependencies (react, typescript, axios)
- [ ] T006 [P] Create .gitignore for Python and Node.js in repository root
- [ ] T007 [P] Create .dockerignore for backend/ (if Docker deployment planned)
- [ ] T008 [P] Create backend/README.md with setup instructions
- [ ] T009 [P] Create frontend/README.md with integration guide