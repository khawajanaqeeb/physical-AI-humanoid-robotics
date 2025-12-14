# Implementation Plan: Gemini-Powered RAG Chatbot for Docusaurus Book

**Branch**: `002-gemini-rag-chatbot` | **Date**: 2025-12-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-gemini-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate a Retrieval-Augmented Generation (RAG) chatbot into an existing Docusaurus book that answers reader questions using the book's content as the primary knowledge source. The system will use Google Gemini embeddings exclusively (`gemini-embedding-001`, 768 dimensions), Qdrant Cloud for vector storage, Neon Serverless Postgres for metadata, and FastAPI for the backend service. The chatbot interface will be embedded into the Docusaurus site without modifying existing book content.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- Backend: FastAPI, google-generativeai, qdrant-client, psycopg2-binary/asyncpg, pydantic
- Frontend: React 18+ (Docusaurus compatible), TypeScript
- Infrastructure: Qdrant Cloud (Free Tier), Neon Serverless Postgres (Free Tier)

**Storage**:
- Qdrant Cloud: Vector embeddings (768-dim) with cosine similarity indexing
- Neon Serverless Postgres: Chunk metadata (chapter, section, URLs, timestamps)
- No modifications to existing Docusaurus book content files

**Testing**:
- Backend: pytest with pytest-asyncio
- Frontend: Jest + React Testing Library
- Integration: End-to-end tests for query pipeline
- Contract: OpenAPI schema validation

**Target Platform**:
- Backend: Linux server/container (Python 3.11+)
- Frontend: Modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- Deployment: Backend on cloud platform with public endpoint, Frontend embedded in Docusaurus (GitHub Pages)

**Project Type**: Web application (backend API + frontend component)

**Performance Goals**:
- Query response time: <3s (p90)
- Ingestion throughput: 50,000-word book in <10 minutes
- Concurrent users: 100 simultaneous queries without degradation
- Embedding generation: Batch processing with rate limit compliance

**Constraints**:
- Free-tier limits: Qdrant Cloud and Neon Postgres capacity
- Gemini API rate limits for embedding generation
- No OpenAI dependencies (Gemini embeddings exclusively)
- Zero modifications to existing book content
- CORS restricted to Docusaurus domain only

**Scale/Scope**:
- Expected usage: ~1,000 queries/day
- Book size: Up to 100,000 words (typical technical book)
- Vector collection: ~200-500 chunks per 50,000 words
- Conversation sessions: Stateless or short-term (5-10 exchanges)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Fully Spec-Driven Workflow
- ✅ **PASS**: Feature specification exists at `specs/002-gemini-rag-chatbot/spec.md` with clear requirements, user stories, and acceptance criteria

### II. Technical Accuracy, Clarity, and Educational Focus
- ✅ **PASS**: This is a supporting feature for the textbook (chatbot for Q&A), not textbook content itself. Technical accuracy applies to implementation code and documentation
- ⚠️ **ATTENTION**: All generated documentation (research.md, data-model.md, quickstart.md) must maintain grade 8-12 clarity where applicable to align with textbook audience

### III. Modular Documentation
- ✅ **PASS**: Implementation follows Docusaurus best practices; chatbot embeds as a component without modifying existing book structure
- ✅ **PASS**: Backend and frontend are clearly separated for maintainability

### IV. Toolchain Fidelity
- ✅ **PASS**: Using Spec-Kit Plus for this specification and planning workflow
- ✅ **PASS**: Claude Code is being used for content generation and planning
- ✅ **PASS**: Docusaurus is the target platform for chatbot embedding
- ⚠️ **ATTENTION**: Backend FastAPI deployment and Qdrant/Neon services are outside the standard textbook toolchain but necessary for RAG functionality

### Project Standards & Constraints
- ✅ **PASS**: This feature does not modify existing textbook chapters or content (zero modifications constraint met)
- ✅ **PASS**: All code must be correct, runnable, and verifiable per standards
- ✅ **PASS**: Markdown/MDX formatting will be followed for all documentation artifacts
- ✅ **PASS**: Final chatbot integration will be deployed alongside GitHub Pages deployment

**Gate Status**: ✅ APPROVED to proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
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
│   ├── models/
│   │   ├── chunk.py           # ContentChunk entity
│   │   ├── query.py           # Query request/response models
│   │   └── session.py         # ConversationSession entity
│   ├── services/
│   │   ├── embedding.py       # Gemini embedding generation
│   │   ├── ingestion.py       # Content chunking and indexing
│   │   ├── retrieval.py       # Vector search via Qdrant
│   │   └── generation.py      # Response generation with sources
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── query.py       # POST /query endpoint
│   │   │   └── health.py      # GET /health endpoint
│   │   └── middleware.py      # CORS, rate limiting, logging
│   ├── db/
│   │   ├── qdrant_client.py   # Qdrant connection and ops
│   │   └── postgres_client.py # Neon Postgres connection
│   ├── config.py              # Environment config
│   └── main.py                # FastAPI app entry point
├── scripts/
│   └── ingest_book.py         # Ingestion script for Docusaurus content
├── tests/
│   ├── unit/
│   │   ├── test_embedding.py
│   │   ├── test_chunking.py
│   │   └── test_retrieval.py
│   ├── integration/
│   │   └── test_query_pipeline.py
│   └── contract/
│       └── test_openapi_spec.py
├── requirements.txt
├── .env.example
└── README.md

frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.tsx      # Main chat component
│   │   ├── MessageList.tsx     # Conversation display
│   │   ├── InputBox.tsx        # Query input field
│   │   └── SourceCitation.tsx  # Display book references
│   ├── services/
│   │   └── api.ts              # Backend API client
│   ├── types/
│   │   └── chat.ts             # TypeScript interfaces
│   └── index.tsx               # Entry point for Docusaurus plugin
├── tests/
│   ├── ChatWidget.test.tsx
│   └── api.test.ts
├── package.json
├── tsconfig.json
└── README.md
```

**Structure Decision**: Selected **Web application** structure with separate `backend/` and `frontend/` directories. This aligns with the requirement for a FastAPI backend service and a React-based chatbot component embedded in Docusaurus. The backend handles all RAG operations (embedding, retrieval, generation), while the frontend provides the user interface integrated into the existing Docusaurus book.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All architectural decisions align with constitution principles.

---

## Phase 0 & Phase 1 Execution Summary

### Phase 0: Research (Completed)

**Artifacts Generated**:
- `research.md`: Comprehensive technical research resolving all unknowns

**Key Decisions Documented**:
1. Gemini `embedding-001` for 768-dim embeddings
2. Hierarchical chunking strategy (512-1024 tokens, 128 overlap)
3. Qdrant Cloud for vector storage with cosine similarity
4. Neon Serverless Postgres for metadata
5. FastAPI async backend with structured error handling
6. React component as Docusaurus custom plugin
7. Separate deployments (backend: Render/Railway, frontend: GitHub Pages)
8. Gemini Pro for response generation

### Phase 1: Design & Contracts (Completed)

**Artifacts Generated**:
- `data-model.md`: Complete entity definitions with validation rules
- `contracts/api.openapi.yaml`: OpenAPI 3.0 specification for backend API
- `contracts/schemas.json`: JSON Schema definitions for all data models
- `quickstart.md`: Developer onboarding guide with setup instructions

**Key Design Outputs**:
1. **Entities**: ContentChunk, Query, RetrievedContext, Response, ConversationSession
2. **API Endpoints**: POST /query, GET /health
3. **Database Schema**: `chunks` table (Postgres) + Qdrant collection
4. **Validation Rules**: Input sanitization, rate limiting, error codes
5. **Project Structure**: Backend (`backend/src/`) and Frontend (`frontend/src/`)

### Post-Design Constitution Check

**Re-evaluation after Phase 1 design artifacts:**

### I. Fully Spec-Driven Workflow
- ✅ **PASS**: All design artifacts (data-model, contracts, quickstart) directly derive from spec.md

### II. Technical Accuracy, Clarity, and Educational Focus
- ✅ **PASS**: All documentation is technically accurate and clear
- ✅ **PASS**: Quickstart.md targets developers with grade 8-12 clarity where applicable

### III. Modular Documentation
- ✅ **PASS**: Clear separation of concerns: research, data model, contracts, quickstart
- ✅ **PASS**: Backend and frontend are independently deployable

### IV. Toolchain Fidelity
- ✅ **PASS**: All artifacts follow Spec-Kit Plus conventions
- ✅ **PASS**: Design supports Docusaurus integration without content modifications

### Project Standards & Constraints
- ✅ **PASS**: Zero modifications to existing book content (chatbot is additive)
- ✅ **PASS**: All code will be verifiable and runnable per standards
- ✅ **PASS**: Deployment strategy aligns with GitHub Pages for frontend

**Final Gate Status**: ✅ APPROVED to proceed to Phase 2 (/sp.tasks command)

---

## Next Steps

**Command**: Run `/sp.tasks` to generate dependency-ordered, testable implementation tasks based on this plan.

**Execution**: After task generation, use `/sp.implement` to execute the implementation workflow with continuous validation.

**ADR Consideration**: Significant architectural decisions documented in research.md may warrant ADRs:
- Gemini-only embedding strategy (vs. multi-provider approach)
- Qdrant Cloud selection (vs. self-hosted or alternatives)
- Stateless session management (vs. persistent conversation storage)

To document these decisions, run: `/sp.adr <decision-title>` after task generation.
