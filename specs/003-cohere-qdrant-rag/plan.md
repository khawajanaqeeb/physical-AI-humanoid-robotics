# Implementation Plan: RAG Chatbot Integration for Deployed Docusaurus Textbook (Cohere + Qdrant)

**Branch**: `003-cohere-qdrant-rag` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-cohere-qdrant-rag/spec.md`

## Summary

Build a production-ready RAG chatbot that answers user questions strictly based on textbook content from the deployed Docusaurus site (https://physical-ai-humanoid-robotics-e3c7.vercel.app/). The system will:
1. Ingest textbook content via sitemap.xml crawling
2. Generate embeddings using Cohere's embed-english-v3.0 model
3. Store vectors in Qdrant Cloud with rich metadata
4. Accept user queries via FastAPI endpoints
5. Retrieve relevant chunks and generate grounded answers using Cohere's command-r model
6. Return responses with source citations to the Docusaurus frontend

**Technical Approach**: FastAPI backend with separate ingestion and retrieval pipelines, using Cohere for embeddings/generation and Qdrant Cloud for vector storage. Content extraction via BeautifulSoup with recursive semantic chunking. Simple API key authentication for protected endpoints.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, cohere 5.0+, qdrant-client 1.7+, BeautifulSoup4 4.12+, requests 2.31+, tenacity 8.2+, slowapi 0.1.9+
**Storage**: Qdrant Cloud (vector database), no relational database
**Testing**: pytest 7.4+ with unittest.mock for external service mocking
**Target Platform**: Cloud platform with Python 3.11+ support (Railway/Render/Cloud Run/Lambda - to be determined during implementation)
**Project Type**: Web application (backend API only, frontend integration via CORS)
**Performance Goals**:
  - Query response: <3 seconds at p95
  - Concurrent queries: 100+ without degradation
  - Ingestion throughput: 500 pages in <10 minutes
**Constraints**:
  - Windows development environment (no Bash commands)
  - No automatic Git operations
  - CORS must allow Vercel frontend (https://physical-ai-humanoid-robotics-e3c7.vercel.app/)
  - All secrets via .env file
  - Cohere only (no OpenAI/Gemini)
**Scale/Scope**:
  - Initial corpus: ~100-500 textbook pages
  - Estimated chunks: 10,000-50,000
  - Expected query volume: 1,000 queries/day during development
  - Rate limit: 10 queries/minute per IP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Alignment with Core Principles

✅ **I. Fully Spec-Driven Workflow**
- Specification created and validated before planning
- All requirements traceable to spec.md
- No implementation details in specification

✅ **II. Technical Accuracy, Clarity, and Educational Focus**
- RAG system designed to provide accurate, cited answers from textbook content
- Guardrails against hallucination (strict grounding in retrieved chunks)
- Source citations enable verification and learning

✅ **III. Modular Documentation**
- Clear separation: ingestion pipeline, retrieval pipeline, API layer
- Reusable components (embedding service, chunking logic, Qdrant client wrapper)
- Well-organized project structure

✅ **IV. Toolchain Fidelity**
- Spec-Kit Plus used for specification
- Claude Code for planning and implementation assistance
- Integration with existing Docusaurus deployment
- Vercel hosting preserved (frontend unchanged)

### Project Standards Compliance

✅ **Chapter Structure & Count**: N/A (backend infrastructure, not textbook chapter)

✅ **Content Formatting & Code Integrity**: All code must be production-ready, tested, and follow Python best practices (PEP 8, type hints)

✅ **Specification & Generation**: This plan follows spec-driven workflow with approved specification

✅ **Accessibility & Deployment**: API responses must be clear and include user-friendly error messages. Deployment platform TBD but must support Python 3.11+

**Gate Status**: ✅ PASSED - No constitutional violations

## Project Structure

### Documentation (this feature)

```text
specs/003-cohere-qdrant-rag/
├── spec.md              # Feature specification (✅ created)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (✅ created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   └── schemas.json     # Request/response JSON schemas
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (✅ created)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── query.py         # POST /api/v1/query endpoint
│   │   │   ├── ingest.py        # POST /api/v1/ingest endpoint
│   │   │   └── health.py        # GET /api/v1/health endpoint
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── cors.py          # CORS configuration
│   │   │   ├── rate_limit.py    # Rate limiting with SlowAPI
│   │   │   └── auth.py          # API key authentication
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── request.py       # Pydantic request models
│   │       └── response.py      # Pydantic response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cohere_service.py    # Cohere API wrapper (embed + generate)
│   │   ├── qdrant_service.py    # Qdrant client wrapper (upsert + search)
│   │   ├── ingestion_service.py # Sitemap crawling & content extraction
│   │   ├── chunking_service.py  # Text chunking logic
│   │   └── rag_service.py       # RAG orchestration (retrieve + generate)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chunk.py             # DocumentChunk domain model
│   │   ├── query_session.py     # QuerySession domain model
│   │   └── ingestion_job.py     # IngestionJob domain model
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Environment variable loading & validation
│   │   ├── logging_config.py    # Structured logging setup
│   │   └── exceptions.py        # Custom exception classes
│   └── utils/
│       ├── __init__.py
│       ├── retry.py             # Tenacity retry decorators
│       └── text_processing.py   # Text cleaning utilities
├── tests/
│   ├── unit/
│   │   ├── test_chunking_service.py
│   │   ├── test_text_processing.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_query_flow.py
│   │   ├── test_ingestion_flow.py
│   │   └── test_api_endpoints.py
│   ├── contract/
│   │   ├── test_cohere_api.py
│   │   ├── test_qdrant_api.py
│   │   └── test_sitemap_accessibility.py
│   └── conftest.py              # Pytest fixtures
├── .env.example                 # Example environment variables
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies (pytest, etc.)
└── README.md                    # Backend setup and usage instructions

frontend/
├── plugins/
│   └── rag-chatbot/             # Existing Docusaurus chat widget integration
│       ├── chatWidget.js        # Chat UI component (to be updated for new API)
│       └── apiClient.js         # API client for backend communication
└── docusaurus.config.js         # Docusaurus configuration (CORS origin)
```

**Structure Decision**: Web application architecture with backend API and minimal frontend integration. Backend follows clean architecture principles with clear separation of concerns:
- **API layer**: FastAPI routes, middleware, request/response schemas
- **Service layer**: Business logic for ingestion, retrieval, RAG orchestration
- **Core layer**: Configuration, logging, shared utilities
- **Models layer**: Domain entities matching spec.md Key Entities

Frontend modifications are minimal (update existing chat widget to call new backend API).

## Complexity Tracking

No constitutional violations - table not needed.

---

## Implementation Phases

### Phase 0: Research & Architecture ✅ COMPLETED

**Output**: [research.md](./research.md)

**Completed Decisions**:
- Cohere embed-english-v3.0 for embeddings (1024 dimensions)
- Cohere command-r for RAG generation with citation support
- Qdrant Cloud with single collection architecture, COSINE distance
- BeautifulSoup for HTML parsing, recursive semantic chunking (500-800 chars)
- FastAPI with SlowAPI rate limiting, simple API key auth
- Tenacity for retry logic with exponential backoff
- Pytest three-tier testing (unit, integration, contract)
- Structured JSON logging for observability

---

### Phase 1: Data Models & Contracts 🔄 IN PROGRESS

**Prerequisites**: research.md completed ✅

**Outputs**:
1. `data-model.md` - Domain entity specifications
2. `contracts/openapi.yaml` - API contract specification
3. `contracts/schemas.json` - Request/response JSON schemas
4. `quickstart.md` - Developer onboarding guide

**Tasks**:

#### Task 1.1: Create Data Model Specification
Create `data-model.md` defining domain entities from spec.md:

**DocumentChunk**:
- `chunk_id`: str (UUID hex)
- `content_text`: str (500-1000 characters)
- `embedding_vector`: List[float] (1024 dimensions)
- `page_url`: str (source URL)
- `page_title`: str (page title)
- `section_heading`: str (heading context, nullable)
- `chunk_index`: int (position in page)
- `character_count`: int (validation)
- `ingestion_timestamp`: str (ISO 8601)

**QuerySession**:
- `session_id`: str (UUID)
- `query_text`: str (user input)
- `embedding_vector`: List[float] (1024 dimensions)
- `retrieved_chunks`: List[DocumentChunk] (top-K results)
- `generated_response`: str (Cohere generation)
- `source_citations`: List[SourceCitation]
- `timestamp`: str (ISO 8601)
- `response_time_ms`: int (performance tracking)
- `retrieval_score_threshold`: float (quality metric)

**IngestionJob**:
- `job_id`: str (UUID)
- `start_time`: str (ISO 8601)
- `end_time`: str (ISO 8601, nullable)
- `pages_processed`: int
- `chunks_created`: int
- `chunks_updated`: int
- `errors_encountered`: List[ErrorRecord]
- `status`: Enum["pending", "running", "completed", "failed"]

**SourceCitation**:
- `page_url`: str
- `page_title`: str
- `chunk_text`: str (excerpt)
- `relevance_score`: float

#### Task 1.2: Create API Contracts
Create `contracts/openapi.yaml` with OpenAPI 3.0 specification:

**Endpoints**:

1. `POST /api/v1/query` (Public, Rate Limited)
   - Request: `{ "query": str, "max_results": int? }`
   - Response: `{ "answer": str, "sources": SourceCitation[], "metadata": {...} }`
   - Errors: 400 (invalid input), 429 (rate limit), 500 (server error), 503 (service unavailable)

2. `POST /api/v1/ingest` (Protected, API Key Required)
   - Request: `{ "force_refresh": bool? }`
   - Response: `{ "job_id": str, "status": str, "pages_processed": int, "chunks_created": int }`
   - Errors: 401 (unauthorized), 500 (server error)

3. `GET /api/v1/health` (Public, No Rate Limit)
   - Response: `{ "status": "healthy|degraded|unhealthy", "services": {...}, "timestamp": str }`

**JSON Schemas**: Extract request/response schemas to `contracts/schemas.json` for validation and testing.

#### Task 1.3: Create Quickstart Guide
Create `quickstart.md` with:
- Prerequisites (Python 3.11+, accounts: Cohere, Qdrant Cloud)
- Environment setup (.env configuration)
- Local development workflow (install deps, run server, run tests)
- First ingestion run
- First query test
- Troubleshooting common issues

#### Task 1.4: Update Agent Context
Run `.specify/scripts/bash/update-agent-context.sh claude` to update `.claude/` with:
- Python 3.11+ (already present from branch 002)
- FastAPI, Cohere, Qdrant Client, BeautifulSoup4
- Testing: pytest

---

### Phase 2: Implementation Planning (NOT DONE BY /sp.plan)

**Note**: This phase is handled by the `/sp.tasks` command, which generates `tasks.md`.

The tasks.md file will break down implementation into concrete, testable tasks:
1. Project initialization & dependencies
2. Core configuration & logging
3. Cohere service implementation
4. Qdrant service implementation
5. Content ingestion pipeline
6. RAG retrieval & generation
7. FastAPI endpoints & middleware
8. Frontend integration updates
9. Testing suite
10. Deployment preparation

Each task will include:
- Description
- Acceptance criteria
- Dependencies
- Estimated complexity
- Test cases

---

## Implementation Sequence

The recommended order for implementation (to be formalized in tasks.md):

### Stage 1: Foundation (MVP Prerequisites)
1. Project structure setup (backend/ directories, __init__.py files)
2. Environment configuration loading & validation (core/config.py)
3. Structured logging setup (core/logging_config.py)
4. Custom exception classes (core/exceptions.py)

### Stage 2: External Service Integration
5. Cohere service wrapper (services/cohere_service.py)
   - embed() method for batch embedding
   - generate() method for RAG generation
   - Retry logic with tenacity
6. Qdrant service wrapper (services/qdrant_service.py)
   - Collection creation/validation
   - Upsert vectors with metadata
   - Search with filtering

### Stage 3: Content Ingestion Pipeline
7. Text processing utilities (utils/text_processing.py)
8. Chunking service (services/chunking_service.py)
   - Recursive semantic chunking
   - Overlap handling
9. Ingestion service (services/ingestion_service.py)
   - Sitemap fetching & parsing
   - Page crawling with BeautifulSoup
   - Content extraction & cleaning
10. Domain models (models/*.py)

### Stage 4: RAG Query Pipeline
11. RAG orchestration service (services/rag_service.py)
    - Embed query
    - Search Qdrant
    - Assemble context
    - Generate with Cohere
    - Format response with citations

### Stage 5: API Layer
12. Pydantic schemas (api/schemas/*.py)
13. Health check endpoint (api/routes/health.py)
14. Query endpoint (api/routes/query.py)
15. Ingest endpoint (api/routes/ingest.py)
16. Middleware (cors, rate limiting, auth)
17. FastAPI app initialization (api/main.py)

### Stage 6: Testing
18. Unit tests (tests/unit/)
19. Integration tests with mocked services (tests/integration/)
20. Contract tests with real services (tests/contract/)

### Stage 7: Frontend Integration
21. Update chatWidget.js to call new backend API
22. Update apiClient.js with new endpoint structure
23. CORS verification between Vercel frontend and deployed backend

### Stage 8: Deployment
24. Requirements.txt finalization
25. README.md with deployment instructions
26. .env.example documentation
27. Platform-specific deployment (Railway/Render/Cloud Run/Lambda)

---

## Deployment Strategy

**Pre-Deployment Checklist**:
- [ ] All tests passing (unit, integration, contract)
- [ ] Environment variables documented in .env.example
- [ ] Cohere API key configured with sufficient quota
- [ ] Qdrant Cloud collection created and accessible
- [ ] CORS origins configured for Vercel frontend
- [ ] Rate limiting tested and configured
- [ ] Error handling validated for all endpoints
- [ ] Logging capturing all critical events

**Deployment Options** (choose one during implementation):

1. **Railway** (Recommended for simplicity)
   - Pros: Simple deployment, automatic HTTPS, good free tier, Python support
   - Cons: Cold starts on free tier
   - Steps: Connect GitHub repo, configure environment variables, deploy

2. **Render**
   - Pros: Similar to Railway, generous free tier
   - Cons: Slower cold starts than Railway
   - Steps: Connect GitHub repo, configure environment variables, deploy

3. **Google Cloud Run**
   - Pros: Scales to zero, pay-per-use, fast cold starts
   - Cons: Requires containerization (Docker), GCP account setup
   - Steps: Create Dockerfile, build image, push to GCR, deploy

4. **AWS Lambda + API Gateway**
   - Pros: True serverless, scales automatically, pay-per-request
   - Cons: Cold start optimization needed, more complex setup
   - Steps: Package with dependencies, create Lambda function, configure API Gateway

**Post-Deployment Verification**:
1. Test health endpoint: `GET https://<deployed-url>/api/v1/health`
2. Run initial ingestion: `POST https://<deployed-url>/api/v1/ingest` with API key
3. Test query endpoint: `POST https://<deployed-url>/api/v1/query` with sample question
4. Verify CORS from Vercel frontend
5. Monitor logs for errors
6. Validate response times meet SLA (<3s p95)

---

## Risk Mitigation

| Risk | Mitigation Strategy | Contingency Plan |
|------|---------------------|------------------|
| Cohere rate limits exceeded | Implement request queuing, monitor usage dashboard | Add caching layer for repeated queries, upgrade API tier |
| Qdrant connectivity issues | Retry logic with exponential backoff, health checks | Implement circuit breaker, maintain read-only mode |
| Poor chunk quality affects retrieval | Iterative testing with sample queries, adjustable parameters | Refine chunking strategy, increase overlap, adjust chunk size |
| Slow ingestion (>10min for 500 pages) | Parallel processing with rate limit respect | Run ingestion during low-traffic periods, implement incremental updates |
| CORS issues between frontend/backend | Early integration testing, proper configuration | Proxy requests through Vercel serverless functions |
| Deployment platform limitations | Test on multiple platforms early | Have backup platform configured (e.g., Railway + Render) |

---

## Success Metrics

Aligned with spec.md Success Criteria:

- **SC-001**: Query response time <3s at p95 → Monitor with structured logs (response_time_ms field)
- **SC-002**: 95%+ citation accuracy → Manual review of sample queries during testing
- **SC-003**: 85%+ answer success rate → Build test set from textbook Q&A, measure accuracy
- **SC-004**: 2-click navigation to sources → Verify source URLs in responses are valid
- **SC-005**: 100+ concurrent queries → Load testing with locust or similar tool
- **SC-006**: Ingestion <10min for 500 pages → Time ingestion job, log duration
- **SC-007**: 99% uptime over 30 days → Monitor with uptime service (UptimeRobot, Better Uptime)
- **SC-008**: Zero hallucinations → Manual review, strict grounding validation in RAG service

---

## Next Steps

1. ✅ Phase 0 complete: research.md created
2. 🔄 Phase 1 in progress: Create data-model.md, contracts/, quickstart.md
3. ⏳ Phase 1 final step: Run update-agent-context.sh
4. ⏳ Phase 2: Run `/sp.tasks` to generate implementation task breakdown

**Ready for**: Data model specification and API contract creation
