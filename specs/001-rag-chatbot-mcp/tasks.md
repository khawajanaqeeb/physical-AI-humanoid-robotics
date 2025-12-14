# Tasks: RAG Chatbot System

**Input**: Design documents from `/specs/001-rag-chatbot-mcp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Not explicitly requested in spec - focusing on implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

Based on research.md and quickstart.md structure:
- Backend: `backend/` (FastAPI application)
- Frontend: `frontend/` (Docusaurus with custom plugin)
- Migrations: `backend/migrations/`
- Scripts: `backend/scripts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure (backend/src/, backend/tests/, backend/migrations/, backend/scripts/)
- [X] T002 Create frontend directory structure (frontend/src/, frontend/plugins/)
- [X] T003 [P] Initialize Python project with requirements.txt (FastAPI, qdrant-client, asyncpg, SQLAlchemy, openai, langdetect, structlog, pydantic, python-dotenv)
- [X] T004 [P] Initialize Node.js project with package.json for Docusaurus 3.x
- [X] T005 [P] Create .env.example file in backend/ with all required environment variables
- [X] T006 [P] Create .gitignore for Python and Node.js projects
- [X] T007 [P] Setup logging configuration in backend/src/config/logging.py using structlog

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create database connection manager in backend/src/database.py with async SQLAlchemy and connection pooling
- [X] T009 Create Qdrant client wrapper in backend/src/clients/qdrant_client.py with async operations and connection pooling
- [X] T010 Create OpenAI client wrapper in backend/src/clients/openai_client.py for embeddings and chat completions
- [X] T011 Create MCP client wrapper in backend/src/clients/mcp_client.py for file system operations and content extraction
- [X] T012 Create database migration 001_create_queries_table.sql in backend/migrations/
- [X] T013 Create database migration 002_create_feedback_table.sql in backend/migrations/
- [X] T014 Create database migration 003_create_sync_jobs_table.sql in backend/migrations/
- [X] T015 Create database initialization script backend/scripts/init_database.py to run migrations
- [X] T016 Create Qdrant collection initialization script backend/scripts/init_qdrant.py with collection config (3072 dimensions, COSINE distance)
- [X] T017 [P] Create Pydantic models for all entities in backend/src/models/__init__.py (Citation, Query, Feedback, SyncJob, TextbookChunkMetadata)
- [X] T018 [P] Create API request/response models in backend/src/api/schemas.py (QueryRequest, QueryResponse, FeedbackRequest, etc.)
- [X] T019 Create FastAPI application setup in backend/src/main.py with CORS middleware and error handling
- [X] T020 Create language detection middleware in backend/src/middleware/language_validator.py using langdetect
- [X] T021 Create environment configuration loader in backend/src/config/settings.py using pydantic-settings
- [X] T022 [P] Create utility for text chunking in backend/src/utils/chunker.py (500-800 tokens, 20% overlap)
- [X] T023 [P] Create utility for heading anchor extraction in backend/src/utils/docusaurus_anchors.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 4 - Multi-Agent RAG Pipeline (Priority: P1) 🎯 MVP Foundation

**Goal**: Implement the core RAG pipeline with Retrieval, Answer, and Citation agents

**Independent Test**: Submit query via API, verify retrieval → answer → citations flow with proper timing

**Why P1**: This is the foundation for all other user stories - must be implemented first

### Implementation for User Story 4

- [X] T024 [P] [US4] Create Retrieval Agent in backend/src/agents/retrieval_agent.py with Qdrant search logic (top-k=5, threshold=0.7)
- [X] T025 [P] [US4] Create Answer Agent in backend/src/agents/answer_agent.py with GPT-4 integration and hallucination prevention prompts
- [X] T026 [P] [US4] Create Citation Agent in backend/src/agents/citation_agent.py with claim-to-source matching and URL generation
- [X] T027 [US4] Create RAG orchestrator in backend/src/services/rag_service.py that coordinates all three agents
- [X] T028 [US4] Implement query endpoint POST /api/query in backend/src/api/routes/query.py with async orchestration
- [X] T029 [US4] Add request validation and error handling for query endpoint
- [X] T030 [US4] Add query logging to Neon database in backend/src/repositories/query_repository.py
- [X] T031 [US4] Add timing instrumentation for each agent (retrieval_time_ms, answer_time_ms, citation_time_ms)
- [X] T032 [US4] Add out-of-scope query detection in backend/src/middleware/language_validator.py
- [X] T033 [US4] Implement health check endpoint GET /health in backend/src/api/routes/health.py

**Checkpoint**: Core RAG pipeline functional - can process queries and return answers with citations

---

## Phase 4: User Story 1 - Interactive Textbook Query (Priority: P1) 🎯 MVP UI

**Goal**: Deploy chat widget that allows students to ask questions and receive answers with citations

**Independent Test**: Click floating chat button, ask question, verify accurate answer with working citation links

**Depends on**: User Story 4 (RAG pipeline must be complete)

### Implementation for User Story 1

- [X] T034 [P] [US1] Create Docusaurus plugin structure in frontend/plugins/rag-chatbot/index.js
- [X] T035 [P] [US1] Create ChatWidget React component in frontend/plugins/rag-chatbot/ChatWidget.jsx with floating button
- [X] T036 [P] [US1] Create ChatModal React component in frontend/plugins/rag-chatbot/ChatModal.jsx with message list and input
- [X] T037 [US1] Implement session management in frontend/plugins/rag-chatbot/hooks/useSession.js (sessionStorage UUID generation)
- [X] T038 [US1] Implement API client in frontend/plugins/rag-chatbot/api/client.js for query submission
- [X] T039 [US1] Add chat message state management in frontend/plugins/rag-chatbot/hooks/useChatMessages.js
- [X] T040 [US1] Create Citation component in frontend/plugins/rag-chatbot/components/Citation.jsx with clickable links
- [X] T041 [US1] Add loading state and error handling in ChatModal component
- [X] T042 [US1] Style chat widget to match Docusaurus theme in frontend/plugins/rag-chatbot/styles.css
- [X] T043 [US1] Make chat widget responsive for desktop, tablet, and mobile
- [X] T044 [US1] Configure plugin in frontend/docusaurus.config.js to load on all pages
- [X] T045 [US1] Test citation link navigation to exact textbook sections

**Checkpoint**: Students can open chat, ask questions, and get answers with working citations

---

## Phase 5: User Story 2 - Text Selection Query (Priority: P2)

**Goal**: Allow readers to select text and see "Ask AI" button for contextual queries

**Independent Test**: Select text, verify button appears, click, confirm chat opens with selected text pre-populated

**Depends on**: User Story 1 (chat widget must exist)

### Implementation for User Story 2

- [ ] T046 [US2] Add text selection detection in frontend/plugins/rag-chatbot/hooks/useTextSelection.js with debounce (300ms)
- [ ] T047 [US2] Create AskAIButton component in frontend/plugins/rag-chatbot/components/AskAIButton.jsx that appears on selection
- [ ] T048 [US2] Add position calculation logic for button placement near selected text
- [ ] T049 [US2] Implement context passing from text selection to ChatModal
- [ ] T050 [US2] Update ChatModal to pre-populate input with selected text
- [ ] T051 [US2] Update query endpoint handler to prioritize chunks from same page when selected_text is provided
- [ ] T052 [US2] Add metadata filtering in Retrieval Agent for text selection context
- [ ] T053 [US2] Test text selection across different page layouts and screen sizes
- [ ] T054 [US2] Add minimum selection length validation (10+ characters)

**Checkpoint**: Text selection opens chat with context, answers prioritize related information

---

## Phase 6: User Story 3 - Automatic Content Synchronization (Priority: P3)

**Goal**: MCP server detects changes, extracts content, generates embeddings, updates vector database

**Independent Test**: Add/modify markdown file, trigger sync, verify content extracted and indexed in Qdrant

**Depends on**: User Story 4 (RAG pipeline uses indexed content)

### Implementation for User Story 3

- [ ] T055 [US3] Create content extraction service in backend/src/services/content_extractor.py using MCP client
- [ ] T056 [US3] Implement markdown file detection in backend/src/services/file_watcher.py with timestamp comparison
- [ ] T057 [US3] Create embedding service in backend/src/services/embedding_service.py with batch processing (100 chunks per request)
- [ ] T058 [US3] Implement chunk upsert logic in backend/src/repositories/qdrant_repository.py
- [ ] T059 [US3] Implement chunk deletion logic for removed files in backend/src/repositories/qdrant_repository.py
- [ ] T060 [US3] Create sync orchestrator in backend/src/services/sync_service.py coordinating extraction, embedding, and storage
- [ ] T061 [US3] Add sync job tracking to database in backend/src/repositories/sync_repository.py
- [ ] T062 [US3] Implement sync trigger endpoint POST /api/sync/trigger in backend/src/api/routes/sync.py with API key auth
- [ ] T063 [US3] Implement sync status endpoint GET /api/sync/status/{sync_id} in backend/src/api/routes/sync.py
- [ ] T064 [US3] Create initial sync script backend/scripts/sync_content.py with --initial flag
- [ ] T065 [US3] Add error handling for partial failures (continue on error, log failures)
- [ ] T066 [US3] Add exponential backoff for OpenAI API rate limits
- [ ] T067 [US3] Add change detection caching to avoid redundant embeddings
- [ ] T068 [US3] Document scheduled sync setup in README (cron example for 6-hour intervals)

**Checkpoint**: Content changes automatically sync to vector database with graceful error handling

---

## Phase 7: User Story 5 - Query Analytics and Feedback (Priority: P3)

**Goal**: System logs queries and feedback to database for monitoring and improvement

**Independent Test**: Submit queries and feedback, verify stored in database, run analytics queries

**Depends on**: User Story 1 (users can provide feedback on answers)

### Implementation for User Story 5

- [ ] T069 [P] [US5] Implement feedback submission endpoint POST /api/feedback in backend/src/api/routes/feedback.py
- [ ] T070 [P] [US5] Create feedback repository in backend/src/repositories/feedback_repository.py with database insert
- [ ] T071 [US5] Add thumbs-up/thumbs-down buttons to ChatMessage component in frontend/plugins/rag-chatbot/components/ChatMessage.jsx
- [ ] T072 [US5] Implement feedback submission in frontend API client
- [ ] T073 [US5] Add feedback confirmation UI (e.g., "Thanks for your feedback!")
- [ ] T074 [US5] Prevent duplicate feedback submissions (one per query, disabled after submission)
- [ ] T075 [US5] Create analytics query scripts in backend/scripts/analytics/ (query_volume.sql, feedback_sentiment.sql, latency_stats.sql)
- [ ] T076 [US5] Add structured logging for all query operations with query_id, session_id, and timing
- [ ] T077 [US5] Document analytics queries in quickstart.md

**Checkpoint**: All queries and feedback logged, analytics available for monitoring

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T078 [P] Add comprehensive error messages and user-friendly error display in chat UI
- [ ] T079 [P] Add request timeout configuration (30s max for queries)
- [ ] T080 [P] Implement circuit breakers for external services (OpenAI, Qdrant, MCP) using tenacity library
- [ ] T081 [P] Add response compression in FastAPI for large answers
- [ ] T082 [P] Add cost tracking and alerts for OpenAI API usage
- [ ] T083 [P] Setup Sentry for error tracking and alerting in backend
- [ ] T084 [P] Add API rate limiting middleware to prevent abuse
- [ ] T085 [P] Optimize Qdrant payload indexes for frequently filtered fields
- [ ] T086 [P] Add lazy loading for chat widget (code splitting)
- [ ] T087 [P] Add accessibility features (ARIA labels, keyboard navigation) to chat UI
- [ ] T088 [P] Create deployment documentation for Railway (backend) and Vercel (frontend)
- [ ] T089 [P] Create README.md with setup instructions, architecture diagram, and quickstart reference
- [ ] T090 [P] Add environment variable validation on startup
- [ ] T091 Run complete quickstart.md validation workflow
- [ ] T092 Conduct end-to-end testing of all user stories
- [ ] T093 Performance testing: verify <3s response time for 95% of queries
- [ ] T094 Load testing: verify system handles 100 concurrent users

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 4 (Phase 3)**: Depends on Foundational - MUST complete first (foundation for all features)
- **User Story 1 (Phase 4)**: Depends on US4 (needs RAG pipeline)
- **User Story 2 (Phase 5)**: Depends on US1 (needs chat widget)
- **User Story 3 (Phase 6)**: Depends on US4 (needs RAG pipeline to use indexed content)
- **User Story 5 (Phase 7)**: Depends on US1 (needs chat interface for feedback)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Setup (Phase 1)
    ↓
Foundational (Phase 2) ← CRITICAL BLOCKER
    ↓
User Story 4 (P1) - RAG Pipeline ← MVP Foundation (MUST BE FIRST)
    ↓
    ├─→ User Story 1 (P1) - Chat Widget ← MVP UI (needs US4)
    │       ↓
    │       ├─→ User Story 2 (P2) - Text Selection (needs US1)
    │       └─→ User Story 5 (P3) - Analytics (needs US1)
    │
    └─→ User Story 3 (P3) - Content Sync (needs US4)
```

### Recommended Implementation Order

1. **MVP First (US4 + US1)**:
   - Phase 1: Setup
   - Phase 2: Foundational (CRITICAL)
   - Phase 3: US4 - RAG Pipeline (core functionality)
   - Phase 4: US1 - Chat Widget (user interface)
   - **STOP and VALIDATE**: Test end-to-end query flow, deploy/demo

2. **Incremental Enhancement**:
   - Phase 5: US2 - Text Selection (enhancement)
   - Phase 6: US3 - Content Sync (operational automation)
   - Phase 7: US5 - Analytics (monitoring)

3. **Polish & Deploy**:
   - Phase 8: Cross-cutting improvements
   - Production deployment

### Parallel Opportunities

#### Within Foundational Phase (after Setup complete):
```bash
# Database & clients can be built in parallel:
Task T008: Database connection manager
Task T009: Qdrant client wrapper
Task T010: OpenAI client wrapper
Task T011: MCP client wrapper

# Migrations can run in parallel:
Task T012: Create queries table migration
Task T013: Create feedback table migration
Task T014: Create sync jobs table migration

# Models and utilities can be built in parallel:
Task T017: Pydantic entity models
Task T018: API request/response models
Task T022: Text chunking utility
Task T023: Heading anchor extraction utility
```

#### Within User Story 4 (RAG Pipeline):
```bash
# All three agents can be developed in parallel:
Task T024: Retrieval Agent
Task T025: Answer Agent
Task T026: Citation Agent
```

#### Within User Story 1 (Chat Widget):
```bash
# UI components can be built in parallel:
Task T034: Plugin structure
Task T035: ChatWidget component
Task T036: ChatModal component
```

#### Within Polish Phase:
```bash
# All polish tasks marked [P] can run in parallel
Task T078-T090: Independent improvements
```

### Within Each User Story

- Models before services
- Services before API endpoints
- Core implementation before integration
- Story complete before moving to next priority

---

## Implementation Strategy

### MVP First (User Stories 4 + 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: US4 - RAG Pipeline (core functionality)
4. Complete Phase 4: US1 - Chat Widget (user interface)
5. **STOP and VALIDATE**: Test end-to-end query flow
6. Deploy/demo if ready

**MVP Deliverable**: Students can ask questions in chat and receive accurate answers with working citations

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US4 (RAG Pipeline) → Core functionality works
3. Add US1 (Chat Widget) → Test independently → Deploy/Demo (MVP!)
4. Add US2 (Text Selection) → Test independently → Deploy/Demo
5. Add US3 (Content Sync) → Test independently → Deploy/Demo
6. Add US5 (Analytics) → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done, US4 MUST complete first (it's the foundation)
3. After US4 is complete:
   - Developer A: US1 (Chat Widget)
   - Developer B: US3 (Content Sync)
4. After US1 is complete:
   - Developer C: US2 (Text Selection)
   - Developer D: US5 (Analytics)

---

## Success Metrics (from spec.md)

After implementation, verify:

- **SC-001**: Answer with citations in under 3 seconds for 95% of queries
- **SC-002**: Zero hallucinated information (validate with test questions)
- **SC-003**: 90% of citations link correctly to exact textbook sections
- **SC-004**: Handles 100 concurrent users without degradation
- **SC-005**: 50-page textbook sync completes in under 10 minutes
- **SC-007**: Chat loads and becomes interactive in under 2 seconds
- **SC-008**: Correctly identifies and rejects out-of-scope queries with 95% accuracy
- **SC-009**: Text selection "Ask AI" activates within 500ms
- **SC-010**: Embedding generation cost under $0.50 per 100 pages

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- User Story 4 MUST be implemented before all other stories (it's the RAG foundation)
- User Story 1 depends on User Story 4 (needs RAG pipeline for chat to work)
- Each user story should be independently testable after implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are not included as they were not explicitly requested in spec.md
