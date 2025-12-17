# Tasks: RAG Chatbot Integration for Deployed Docusaurus Textbook (Cohere + Qdrant)

**Input**: Design documents from `/specs/003-cohere-qdrant-rag/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in specification - test tasks omitted per template guidelines.

**Organization**: Tasks are grouped by user story (US1: Query Content [P1-MVP], US2: Content Discovery [P2], US3: Content Synchronization [P3]) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Web app structure (from plan.md):
- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/plugins/rag-chatbot/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic backend structure

- [ ] T001 Create backend directory structure per plan.md (backend/src/{api,services,models,core,utils})
- [ ] T002 Create requirements.txt with FastAPI 0.104+, cohere 5.0+, qdrant-client 1.7+, BeautifulSoup4 4.12+, requests 2.31+, tenacity 8.2+, slowapi 0.1.9+, python-dotenv 1.0+
- [ ] T003 Create requirements-dev.txt with pytest 7.4+, pytest-cov, pytest-mock
- [ ] T004 [P] Create backend/.env.example with COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, CORS_ORIGINS, API_KEY placeholders
- [ ] T005 [P] Create backend/.gitignore including .env, __pycache__, .pytest_cache
- [ ] T006 [P] Create all __init__.py files for Python package structure in backend/src/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create backend/src/core/config.py with environment variable loading using python-dotenv and pydantic Settings validation
- [ ] T008 [P] Create backend/src/core/logging_config.py with JSON structured logging setup
- [ ] T009 [P] Create backend/src/core/exceptions.py with custom exception classes (CohereAPIError, QdrantConnectionError, IngestionError, ValidationError)
- [ ] T010 [P] Create backend/src/utils/retry.py with tenacity retry decorators for Cohere and Qdrant operations
- [ ] T011 Create backend/src/api/main.py as FastAPI app entry point with CORS middleware configuration for Vercel frontend
- [ ] T012 Create backend/src/services/cohere_service.py implementing CohereService class with embed() and generate() methods using tenacity retry
- [ ] T013 Create backend/src/services/qdrant_service.py implementing QdrantService class with create_collection(), upsert_vectors(), and search() methods using tenacity retry
- [ ] T014 Implement Qdrant collection initialization in backend/src/services/qdrant_service.py (1024-dim vectors, COSINE distance, on_disk_payload=True)
- [ ] T015 [P] Create backend/src/models/chunk.py implementing DocumentChunk dataclass per data-model.md
- [ ] T016 [P] Create backend/src/models/query_session.py implementing QuerySession dataclass per data-model.md
- [ ] T017 [P] Create backend/src/models/ingestion_job.py implementing IngestionJob and ErrorRecord dataclasses per data-model.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Query Textbook Content (Priority: P1) 🎯 MVP

**Goal**: Enable students to ask questions and receive accurate, grounded answers with source citations from textbook content

**Independent Test**: Submit a question via POST /api/v1/query, verify response contains answer text + source citations with URLs, click source URL to confirm it navigates to textbook page

### Implementation for User Story 1

**Ingestion Pipeline (FR-001 to FR-008)**:
- [ ] T018 [P] [US1] Create backend/src/utils/text_processing.py with text cleaning functions (remove navigation, footers, normalize whitespace)
- [ ] T019 [US1] Create backend/src/services/chunking_service.py implementing recursive semantic chunking (500-800 chars, 100-char overlap, preserve heading context)
- [ ] T020 [US1] Create backend/src/services/ingestion_service.py with fetch_sitemap() method to parse sitemap.xml using xml.etree.ElementTree
- [ ] T021 [US1] Implement crawl_page() method in backend/src/services/ingestion_service.py using requests + BeautifulSoup to extract content from <article> or <main>
- [ ] T022 [US1] Implement ingest_textbook() method in backend/src/services/ingestion_service.py orchestrating: fetch sitemap → crawl pages → chunk → embed with Cohere → upsert to Qdrant
- [ ] T023 [US1] Add error handling in backend/src/services/ingestion_service.py for HTTP errors, parse failures, embedding failures (log ErrorRecord, continue processing)

**RAG Pipeline (FR-009 to FR-016)**:
- [ ] T024 [US1] Create backend/src/services/rag_service.py implementing RAGService class
- [ ] T025 [US1] Implement query_textbook() method in backend/src/services/rag_service.py: embed query with Cohere → search Qdrant (top-5, threshold=0.7) → retrieve chunks
- [ ] T026 [US1] Implement generate_answer() method in backend/src/services/rag_service.py using Cohere command-r with documents parameter, citation_quality="accurate", temperature=0.3
- [ ] T027 [US1] Implement extract_citations() method in backend/src/services/rag_service.py to parse Cohere citations into SourceCitation objects
- [ ] T028 [US1] Add "information not found in textbook" handling in backend/src/services/rag_service.py when retrieval score < threshold or no results

**API Layer (FR-017, FR-020 to FR-023)**:
- [ ] T029 [P] [US1] Create backend/src/api/schemas/request.py with QueryRequest Pydantic model (query: str 1-2000 chars, max_results: int 1-10 default 5)
- [ ] T030 [P] [US1] Create backend/src/api/schemas/response.py with QueryResponse, SourceCitation Pydantic models per contracts/openapi.yaml
- [ ] T031 [US1] Create backend/src/api/routes/query.py implementing POST /api/v1/query endpoint calling RAGService.query_textbook()
- [ ] T032 [US1] Add SlowAPI rate limiting (10 req/min per IP) to query endpoint in backend/src/api/middleware/rate_limit.py
- [ ] T033 [US1] Add structured logging for query operations in backend/src/api/routes/query.py (log session_id, response_time_ms, chunks_retrieved)
- [ ] T034 [US1] Register query route in backend/src/api/main.py with proper error handling middleware

**Verification**:
- [ ] T035 [US1] Run backend server (uvicorn src.api.main:app --reload), confirm startup with no errors
- [ ] T036 [US1] Verify FastAPI auto-docs at http://localhost:8000/docs show POST /api/v1/query endpoint
- [ ] T037 [US1] Test query endpoint with sample question, verify JSON response matches QueryResponse schema
- [ ] T038 [US1] Verify source citations include valid textbook URLs and relevance scores
- [ ] T039 [US1] Test "information not found" response for out-of-scope query

**Checkpoint**: At this point, User Story 1 should be fully functional - students can query the chatbot and receive grounded answers with citations

---

## Phase 4: User Story 2 - Content Discovery & Navigation (Priority: P2)

**Goal**: Enable users to navigate to specific textbook sections from chatbot responses and see enhanced citation metadata

**Independent Test**: Receive a chatbot answer with multiple source citations, verify each citation includes page_title and chunk_text preview, click citation URL to confirm navigation to exact textbook page

### Implementation for User Story 2

**Enhanced Citations (builds on US1)**:
- [ ] T040 [P] [US2] Update backend/src/api/schemas/response.py SourceCitation model to ensure page_title and chunk_text (max 300 chars) are always populated
- [ ] T041 [US2] Update backend/src/services/rag_service.py extract_citations() to include chunk_text excerpts (truncate with "..." if >300 chars)
- [ ] T042 [US2] Update backend/src/services/rag_service.py to tag which parts of answer came from which sources (use Cohere citation metadata)

**Frontend Integration Preparation**:
- [ ] T043 [P] [US2] Review frontend/plugins/rag-chatbot/chatWidget.js current implementation
- [ ] T044 [US2] Update frontend/plugins/rag-chatbot/apiClient.js to call POST /api/v1/query with proper error handling
- [ ] T045 [US2] Update frontend/plugins/rag-chatbot/chatWidget.js to render SourceCitation objects as clickable links with page_title as link text
- [ ] T046 [US2] Add citation preview UI in frontend/plugins/rag-chatbot/chatWidget.js showing chunk_text on hover or expand
- [ ] T047 [US2] Add relevance_score display as percentage in frontend/plugins/rag-chatbot/chatWidget.js for user transparency

**Verification**:
- [ ] T048 [US2] Test query with multi-section answer, verify response includes multiple distinct source citations
- [ ] T049 [US2] Verify each citation includes non-empty page_title and chunk_text fields
- [ ] T050 [US2] Click source URLs from frontend to confirm navigation to correct textbook pages
- [ ] T051 [US2] Verify CORS allows requests from deployed Vercel frontend (https://physical-ai-humanoid-robotics-e3c7.vercel.app/)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can query and navigate to sources

---

## Phase 5: User Story 3 - Real-Time Content Synchronization (Priority: P3)

**Goal**: Enable administrators to trigger content re-ingestion via protected API endpoint to reflect textbook updates

**Independent Test**: Add a new page to textbook sitemap, trigger POST /api/v1/ingest with API key, verify new content becomes queryable and old queries still work

### Implementation for User Story 3

**Protected Ingestion Endpoint (FR-018, FR-019)**:
- [ ] T052 [P] [US3] Create backend/src/api/middleware/auth.py with API key validation decorator checking X-API-Key header against config.API_KEY
- [ ] T053 [P] [US3] Create backend/src/api/schemas/request.py IngestRequest model (force_refresh: bool default False)
- [ ] T054 [P] [US3] Create backend/src/api/schemas/response.py IngestResponse model per contracts/openapi.yaml
- [ ] T055 [US3] Create backend/src/api/routes/ingest.py implementing POST /api/v1/ingest endpoint protected by API key auth
- [ ] T056 [US3] Implement ingestion job orchestration in backend/src/api/routes/ingest.py: create IngestionJob → call IngestionService → update job status → return IngestResponse
- [ ] T057 [US3] Add force_refresh logic in backend/src/services/ingestion_service.py to re-process all pages when force_refresh=True
- [ ] T058 [US3] Add incremental update logic in backend/src/services/ingestion_service.py to skip unchanged pages when force_refresh=False (compare ingestion_timestamp)
- [ ] T059 [US3] Register ingest route in backend/src/api/main.py with auth middleware

**Verification**:
- [ ] T060 [US3] Test POST /api/v1/ingest without API key, verify 401 Unauthorized response
- [ ] T061 [US3] Test POST /api/v1/ingest with valid API key and force_refresh=False, verify ingestion job completes successfully
- [ ] T062 [US3] Verify IngestResponse includes job_id, status, pages_processed, chunks_created counts
- [ ] T063 [US3] Test force_refresh=True reprocesses all pages even if already ingested
- [ ] T064 [US3] After re-ingestion, query for newly added content and verify it's retrievable
- [ ] T065 [US3] Verify queries for old content still work after re-ingestion (no data loss)

**Checkpoint**: All user stories should now be independently functional - query, navigate sources, and admin can re-sync content

---

## Phase 6: Health Check & Observability

**Purpose**: System monitoring and operational visibility (FR-027, FR-028)

- [ ] T066 [P] Create backend/src/api/routes/health.py implementing GET /api/v1/health endpoint
- [ ] T067 [P] Implement health checks in backend/src/api/routes/health.py: ping Cohere API, ping Qdrant, return HealthResponse per contracts/openapi.yaml
- [ ] T068 Register health route in backend/src/api/main.py (no rate limiting or auth)
- [ ] T069 [P] Add request timeout configuration in backend/src/core/config.py (default: 30s for queries, 600s for ingestion)
- [ ] T070 Implement request timeouts in backend/src/api/main.py middleware to prevent hanging connections

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T071 [P] Create backend/README.md with setup instructions from quickstart.md
- [ ] T072 [P] Create backend/.env.example documentation explaining each environment variable with examples
- [ ] T073 [P] Add input validation edge cases in backend/src/api/schemas/request.py (query too long >2000 chars, max_results out of range)
- [ ] T074 Add comprehensive error responses in backend/src/api/main.py global exception handler matching ErrorResponse schema
- [ ] T075 [P] Add HTTP status code validation: 400 for bad requests, 401 for auth failures, 429 for rate limits, 500 for server errors, 503 for service unavailable
- [ ] T076 Performance optimization: Add caching for repeated queries in backend/src/services/rag_service.py (optional, measure first)
- [ ] T077 [P] Security: Add input sanitization in backend/src/utils/text_processing.py to prevent injection attacks
- [ ] T078 Validate quickstart.md instructions by following them end-to-end on clean environment
- [ ] T079 Run through all edge cases from spec.md and verify system handles them gracefully
- [ ] T080 Prepare deployment checklist: requirements.txt finalized, .env.example complete, CORS configured, API keys secured

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational (Phase 2) completion
  - User Story 1 (US1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (US2): Can start after Foundational - Extends US1 but independently testable
  - User Story 3 (US3): Can start after Foundational - Uses US1 ingestion code but independently testable
- **Health Check (Phase 6)**: Can start after Foundational - No dependencies on user stories
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1-MVP)**: Foundational complete → Can implement independently → Delivers core chatbot query functionality
- **User Story 2 (P2)**: Foundational complete → Extends US1 citations → Delivers enhanced navigation
- **User Story 3 (P3)**: Foundational complete → Reuses US1 ingestion → Delivers admin re-sync capability

### Within Each User Story

- Ingestion Pipeline before RAG Pipeline (US1: T018-T023 before T024-T028)
- RAG Pipeline before API Layer (US1: T024-T028 before T029-T034)
- API schemas before routes (US1: T029-T030 before T031)
- Backend implementation before Frontend integration (US2: T040-T042 before T043-T047)

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002-T006 can all run in parallel (different files)

**Phase 2 (Foundational)**:
- T008, T009, T010 can run in parallel (different core utilities)
- T015, T016, T017 can run in parallel (different model files)

**Phase 3 (User Story 1)**:
- T018, T029, T030 can start in parallel (different concerns)
- T024-T028 (RAG service methods) can be developed in parallel after T023 completes

**Phase 4 (User Story 2)**:
- T040, T043 can run in parallel
- T044-T047 (frontend updates) can run in parallel

**Phase 5 (User Story 3)**:
- T052, T053, T054 can run in parallel (different files)

**Phase 6 (Health)**:
- T066, T067, T069 can run in parallel

**Phase 7 (Polish)**:
- T071, T072, T073, T075, T077 can all run in parallel

---

## Parallel Example: User Story 1

```bash
# Start these together after Foundational phase:
Task T018: "Create text_processing.py utilities"
Task T029: "Create QueryRequest schema"
Task T030: "Create QueryResponse schema"

# After T018 completes, start chunking:
Task T019: "Create chunking_service.py"

# After ingestion pipeline (T018-T023) completes, start RAG:
Task T024: "Create rag_service.py"
Task T025: "Implement query_textbook()"
Task T026: "Implement generate_answer()"
Task T027: "Implement extract_citations()"
Task T028: "Add not-found handling"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T017) - CRITICAL
3. Complete Phase 3: User Story 1 (T018-T039)
4. **STOP and VALIDATE**: Test US1 independently with sample queries
5. Run initial ingestion (T022)
6. Deploy/demo MVP

**MVP Scope**: After T039, you have a functional RAG chatbot that can:
- Ingest textbook content from sitemap
- Answer user questions with grounded responses
- Provide source citations
- Handle queries via /api/v1/query endpoint

### Incremental Delivery

1. Setup + Foundational (T001-T017) → Foundation ready
2. Add User Story 1 (T018-T039) → Test independently → Deploy MVP ✅
3. Add User Story 2 (T040-T051) → Test independently → Deploy enhanced citations
4. Add User Story 3 (T052-T065) → Test independently → Deploy admin re-sync
5. Add Health & Polish (T066-T080) → Production-ready

Each phase adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

1. **Developer A**: User Story 1 (T018-T039) - Core chatbot
2. **Developer B**: User Story 2 (T040-T051) - Enhanced citations (starts after T039)
3. **Developer C**: Health Check (T066-T070) - Monitoring
4. **All together**: Polish (T071-T080) after all stories complete

---

## Verification Checklist

### After User Story 1 (MVP)
- [ ] Backend starts without errors
- [ ] POST /api/v1/query accepts questions and returns answers
- [ ] Responses include source citations with valid URLs
- [ ] Answers are grounded in textbook content (no hallucinations)
- [ ] Rate limiting enforces 10 req/min per IP
- [ ] CORS allows Vercel frontend requests

### After User Story 2
- [ ] Citations include page_title and chunk_text previews
- [ ] Frontend renders citations as clickable links
- [ ] Clicking citation navigates to correct textbook page
- [ ] US1 functionality still works

### After User Story 3
- [ ] POST /api/v1/ingest requires API key
- [ ] Ingestion job processes all sitemap pages
- [ ] Re-ingestion updates content without breaking existing queries
- [ ] US1 and US2 functionality still work

### Production Ready (After Phase 7)
- [ ] All edge cases from spec.md handled gracefully
- [ ] Quickstart.md instructions verified end-to-end
- [ ] Environment variables documented in .env.example
- [ ] Error responses match OpenAPI schema
- [ ] Logs capture all critical operations
- [ ] Security: Input sanitization, API key protection, CORS configured
- [ ] Performance: Query <3s at p95, ingestion <10min for 500 pages

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** (US1, US2, US3) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group for manual Git control
- Stop at any checkpoint to validate story independently before proceeding
- **MVP = User Story 1 only** - delivers core value, can deploy and demo
- Avoid vague tasks, same-file conflicts, cross-story dependencies that break independence

---

## Summary

**Total Tasks**: 80 tasks across 7 phases
**MVP Tasks**: 39 tasks (T001-T039) - User Story 1 only
**User Story Breakdown**:
- US1 (P1-MVP): 22 implementation tasks (T018-T039)
- US2 (P2): 12 implementation tasks (T040-T051)
- US3 (P3): 14 implementation tasks (T052-T065)

**Parallel Opportunities**: 25 tasks marked [P] can run in parallel within their phase
**Independent Stories**: Each user story (US1, US2, US3) can be tested and deployed independently
**Suggested MVP Scope**: Complete through T039 (User Story 1) for first deployment
