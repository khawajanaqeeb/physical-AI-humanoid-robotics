# Complete Implementation Plan: Phase 2 RAG Chatbot System

**Branch**: `001-rag-chatbot-mcp` | **Date**: 2025-12-10

This document contains the comprehensive implementation plan as requested, including all 10 required sections.

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUSAURUS FRONTEND                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Chat Widget  │  │ Text Selector│  │ Session Mgmt │          │
│  │ (React)      │  │ (JS Event)   │  │ (UUID)       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ POST /api/query
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ API Layer                                                 │  │
│  │  - Language Detection Middleware                          │  │
│  │  - CORS Middleware                                        │  │
│  │  - Request Validation                                     │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                              │
│  ┌────────────────▼─────────────────────────────────────────┐  │
│  │ MULTI-AGENT RAG PIPELINE                                 │  │
│  │                                                           │  │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │  │
│  │  │ Retrieval    │ → │ Answer       │ → │ Citation     │ │  │
│  │  │ Agent        │   │ Agent        │   │ Agent        │ │  │
│  │  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘ │  │
│  │         │                  │                  │          │  │
│  │         │ Vector Search    │ GPT-4 Synthesis  │ Anchor   │  │
│  │         │ (top-k)          │ (context only)   │ Linking  │  │
│  └─────────┼──────────────────┼──────────────────┼──────────┘  │
│            │                  │                  │              │
│            ▼                  ▼                  │              │
│  ┌─────────────────┐  ┌────────────────────┐    │              │
│  │ Qdrant Client   │  │ OpenAI Client      │    │              │
│  └─────────────────┘  └────────────────────┘    │              │
│            │                                     ▼              │
│            │                           ┌──────────────────┐    │
│            │                           │ Neon Postgres    │    │
│            │                           │ (Query Logging)  │    │
│            │                           └──────────────────┘    │
└────────────┼──────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QDRANT CLOUD                                  │
│  Collection: textbook_chunks                                     │
│  - Vectors: 3072 dims (text-embedding-3-large)                   │
│  - Payload: file_path, title, heading_hierarchy, anchor          │
└─────────────────────────────────────────────────────────────────┘
             ▲
             │ Upsert/Delete (Sync)
             │
┌────────────┴─────────────────────────────────────────────────────┐
│                  CONTENT SYNC PIPELINE                            │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐         │
│  │ MCP Server   │ → │ Chunking &   │ → │ Embedding    │         │
│  │ (fs tools)   │   │ Metadata     │   │ (OpenAI)     │         │
│  └──────────────┘   └──────────────┘   └──────────────┘         │
│         ▲                                                         │
│         │ Read markdown files                                    │
│  ┌──────┴──────────────────────────────────────────────────┐    │
│  │ Change Detection (MCP system tools)                      │    │
│  │ - File watcher / Timestamp comparison                    │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Architecture (FastAPI + MCP Server)

**Components**:
- **API Layer**: FastAPI endpoints with async/await, Pydantic validation
- **Middleware Stack**: CORS, language detection, structured logging
- **Agent Orchestration**: Coordinates Retrieval → Answer → Citation pipeline
- **Service Layer**: MCP client, Qdrant client, embedding service, sync orchestrator
- **Database Layer**: AsyncSQLAlchemy with Neon Postgres

**Communication Pattern**: Request → Middleware → Orchestrator → Agents → External Services

### Multi-Agent RAG Pipeline Architecture

**Agent Responsibilities**:

1. **Retrieval Agent**:
   - Embeds query using OpenAI text-embedding-3-large
   - Searches Qdrant for top-k chunks (default k=5, threshold=0.7)
   - Applies metadata filters (e.g., file_path for text selection context)
   - Returns ranked chunks with similarity scores

2. **Answer Agent**:
   - Receives query + retrieved chunks
   - Uses GPT-4 with strict system prompt: "Use ONLY provided context"
   - Synthesizes coherent natural language response
   - Prevents hallucination through context constraints

3. **Citation Agent**:
   - Matches answer claims to source chunks
   - Extracts metadata (document title, section anchor)
   - Formats citations as Docusaurus links: `/docs/page#anchor`
   - Returns list of Citation objects

**Orchestration Flow**:
```
User Query
    ↓
Retrieval Agent (async)
    ↓ [chunks with scores]
Answer Agent (async)
    ↓ [answer text]
Citation Agent (async)
    ↓ [formatted citations]
Response Assembly
```

### Embedding & Vector Storage Pipeline

**Pipeline Stages**:

1. **Content Extraction** (MCP Server):
   - Read markdown files via MCP fs tools
   - Extract heading hierarchy and text content
   - Generate Docusaurus heading anchors (lowercase, dash-separated)

2. **Chunking**:
   - Target: 500-800 tokens per chunk
   - Overlap: 20% (100-160 tokens) between adjacent chunks
   - Preserve paragraph boundaries where possible

3. **Embedding Generation** (OpenAI):
   - Model: text-embedding-3-large (3072 dimensions)
   - Batching: 100 chunks per API call
   - Retry logic: Exponential backoff (max 3 attempts)
   - Cost tracking: ~$0.13 per 1M tokens

4. **Vector Storage** (Qdrant Cloud):
   - Upsert points with chunk_id = `{file_path}:{chunk_index}`
   - Payload: metadata (title, hierarchy, anchor, etc.)
   - Indexing: HNSW for fast similarity search

### Relational Logging/Analytics Layer (Neon Postgres)

**Schema**:
- **queries**: Full query logs (text, session, chunks, timing)
- **feedback**: Thumbs up/down ratings
- **sync_jobs**: Content sync status and error logs

**Usage**:
- Real-time query logging (async inserts)
- Analytics queries (volume, latency, sentiment)
- Sync job monitoring (status, errors, metrics)

### Frontend Integration Architecture (Docusaurus + Chat Widget)

**Components**:
- **Custom Plugin**: Docusaurus plugin injecting chat widget globally
- **Floating Button**: Fixed-position button (bottom-right)
- **Chat Modal**: Overlay modal with message history and input
- **Text Selector**: Event listener for "Ask AI" button on selection
- **Session Manager**: UUID generation and sessionStorage persistence

**Integration Points**:
- Plugin loaded via `docusaurus.config.js`
- API calls to backend via fetch/axios
- Session UUID attached to all requests
- Citations rendered as anchor links

### System Communication Flow

**Query Processing**:
```
User types question in UI
    ↓
Frontend: GET/CREATE session UUID (sessionStorage)
    ↓
POST /api/query {query, session_id, selected_text?}
    ↓
Backend Middleware: Validate + detect language
    ↓
Retrieval Agent: Embed query → search Qdrant
    ↓
Answer Agent: Synthesize response from chunks
    ↓
Citation Agent: Format anchor links
    ↓
Database: Log query + response
    ↓
Response JSON: {answer, citations, sources, timing}
    ↓
Frontend: Render answer + clickable citations
    ↓
User clicks citation → navigate to `/docs/page#anchor`
```

**Content Sync**:
```
Cron trigger (every 6 hours) OR manual POST /api/sync/trigger
    ↓
MCP Server: Detect changed files (timestamp comparison)
    ↓
For each changed file:
  MCP: Extract content + metadata
  Chunking: Split with 20% overlap
  OpenAI: Generate embeddings (batch)
  Qdrant: Upsert chunks (delete old, insert new)
    ↓
Database: Log sync job (status, files processed, errors)
    ↓
Response: {sync_id, status, message}
```

---

## 2. IMPLEMENTATION PHASES (WITH ORDER)

### Phase 1: Project Initialization & Environment Setup
**Objective**: Bootstrap development environment and external service accounts

**Deliverables**:
- Repository folder structure (backend/, frontend/, specs/)
- Python 3.11 virtual environment with requirements.txt installed
- Node.js environment with Docusaurus 3.x initialized
- Qdrant Cloud collection created (textbook_chunks, 3072 dims)
- Neon Postgres database with schema (queries, feedback, sync_jobs)
- .env files configured with API keys

**Tools/Tech**: Git, Python, Node.js, Qdrant Console, Neon Console, OpenAI API

**Complexity**: Low (2-4 hours)

**Success Criteria**:
- ✅ `pip install -r backend/requirements.txt` succeeds
- ✅ `npm install` in frontend/ succeeds
- ✅ Qdrant collection queryable via Python client
- ✅ Neon database accessible, tables created
- ✅ `GET /health` returns 200 OK

---

### Phase 2: MCP-Driven Content Ingestion Pipeline
**Objective**: Extract and structure textbook content for embedding

**Deliverables**:
- `backend/app/services/mcp_client.py` (MCP wrapper)
- Chunking algorithm (500-800 tokens, 20% overlap)
- Heading anchor extraction (Docusaurus format)
- Metadata structure (file_path, title, hierarchy, anchor)

**Tools/Tech**: Context7 MCP Server, MCP Client SDK, regex

**Complexity**: Medium (6-10 hours)

**Success Criteria**:
- ✅ MCP client connects and lists markdown files
- ✅ Chunks have 500-800 tokens with 100-160 token overlap
- ✅ Anchors match Docusaurus format (e.g., "forward-kinematics")
- ✅ Metadata includes file_path, title, heading hierarchy, anchor

---

### Phase 3: Embedding Generation & Qdrant Integration
**Objective**: Generate vector embeddings and populate Qdrant

**Deliverables**:
- `backend/app/services/embeddings.py` (OpenAI batching)
- `backend/app/services/qdrant_client.py` (CRUD operations)
- Upsert logic (chunk_id as point ID)
- Delete logic (remove chunks for deleted files)

**Tools/Tech**: OpenAI API, Qdrant Python Client (async)

**Complexity**: Medium (6-8 hours)

**Success Criteria**:
- ✅ Batch embed 100 chunks per API call
- ✅ Upsert to Qdrant with correct payload
- ✅ Search returns top-k chunks with scores
- ✅ Embedding cost <$0.50 per 100 pages

---

### Phase 4: Multi-Agent RAG Pipeline
**Objective**: Implement and orchestrate three agents

**Deliverables**:
- `backend/app/agents/retrieval.py`
- `backend/app/agents/answer.py`
- `backend/app/agents/citation.py`
- Agent orchestration logic

**Tools/Tech**: OpenAI Agents SDK, GPT-4

**Complexity**: High (12-16 hours)

**Success Criteria**:
- ✅ Retrieval Agent returns top-5 chunks (score > 0.7)
- ✅ Answer Agent uses only provided context (no hallucination)
- ✅ Citation Agent formats links: `/docs/page#anchor`
- ✅ Pipeline completes in <3s p95

---

### Phase 5: FastAPI Backend Endpoints
**Objective**: Expose RESTful API with validation and middleware

**Deliverables**:
- POST /api/query (main RAG endpoint)
- POST /api/feedback (thumbs up/down)
- POST /api/sync/trigger (admin, authenticated)
- GET /api/sync/status/{sync_id}
- GET /health (dependency checks)
- Middleware: CORS, language detection, logging

**Tools/Tech**: FastAPI, Pydantic, langdetect, structlog

**Complexity**: Medium (8-12 hours)

**Success Criteria**:
- ✅ OpenAPI docs auto-generated at /docs
- ✅ Invalid requests return 422 with details
- ✅ Non-English queries return 400 with message
- ✅ CORS allows Docusaurus domain
- ✅ Health endpoint checks all dependencies

---

### Phase 6: Neon Postgres Logging & Analytics
**Objective**: Persist queries and feedback for monitoring

**Deliverables**:
- SQLAlchemy async ORM models (Query, Feedback, SyncJob)
- Connection pooling (asyncpg driver)
- Logging middleware (capture request/response)
- Analytics SQL queries (volume, latency, sentiment)

**Tools/Tech**: SQLAlchemy 2.0, asyncpg, Neon Postgres

**Complexity**: Medium (6-8 hours)

**Success Criteria**:
- ✅ All queries logged with session_id and timing
- ✅ Feedback linked to queries via foreign key
- ✅ Sync jobs tracked with status transitions
- ✅ Connection pool handles 100 concurrent queries

---

### Phase 7: Docusaurus Chat Widget Frontend
**Objective**: Build interactive chat UI integrated with textbook

**Deliverables**:
- Custom Docusaurus plugin (`frontend/src/plugins/rag-chatbot/`)
- Floating button component
- Chat modal (message list + input)
- Session UUID manager (sessionStorage)
- Text selection "Ask AI" button
- Citation link rendering
- Responsive design (mobile, tablet, desktop)

**Tools/Tech**: React 18, Docusaurus 3.x plugin API, CSS

**Complexity**: High (12-16 hours)

**Success Criteria**:
- ✅ Chat button visible on all pages
- ✅ Modal opens without navigation
- ✅ Session UUID persists for tab (cleared on close)
- ✅ Text selection triggers "Ask AI" (<500ms)
- ✅ Citations clickable and navigate correctly
- ✅ Matches Docusaurus theme

---

### Phase 8: Content Sync Automation
**Objective**: Automate content updates with change detection

**Deliverables**:
- `backend/scripts/sync_content.py` (standalone script)
- Change detection (timestamp + hash comparison)
- Incremental re-embedding (only modified files)
- Error recovery (continue on failure)
- Sync job logging to database

**Tools/Tech**: MCP system tools, asyncio, cron

**Complexity**: Medium (6-8 hours)

**Success Criteria**:
- ✅ Detects new/modified/deleted files
- ✅ Re-embeds only changed content
- ✅ Logs errors but continues
- ✅ Completes 50-page sync in <10min
- ✅ Cron runs every 6 hours in production

---

### Phase 9: Testing & Quality Assurance
**Objective**: Validate all success criteria and edge cases

**Deliverables**:
- Unit tests (agents, services, API)
- Integration tests (Qdrant, Neon, MCP)
- E2E RAG tests (100 test questions)
- Edge case tests (non-English, long queries, concurrent)
- Citation accuracy validation (90%+ target)
- Load tests (100 concurrent users)

**Tools/Tech**: pytest, pytest-asyncio, Jest, Locust

**Complexity**: High (12-16 hours)

**Success Criteria**:
- ✅ 90%+ backend code coverage
- ✅ All spec.md success criteria validated
- ✅ 100 questions, zero hallucination
- ✅ 90%+ citation accuracy
- ✅ Load test passes (100 users, <3s p95)

---

### Phase 10: Deployment & Monitoring
**Objective**: Deploy to production with observability

**Deliverables**:
- Backend deployed to Railway (containerized)
- Frontend deployed to Vercel
- Environment variables configured
- HTTPS enabled
- Structured logging (JSON)
- Error tracking (Sentry)
- Uptime monitoring (UptimeRobot)
- Cost alerts (OpenAI API)

**Tools/Tech**: Railway, Vercel, Sentry, UptimeRobot

**Complexity**: Medium (6-10 hours)

**Success Criteria**:
- ✅ Backend accessible via HTTPS
- ✅ Frontend chat widget functional
- ✅ Health endpoint returns 200
- ✅ Logs viewable in Railway
- ✅ Alerts configured for errors/costs

---

## 3. DEPENDENCY GRAPH

### Sequential Dependencies

```
Phase 1 (Init) [FOUNDATIONAL]
    ↓
Phase 2 (MCP Ingestion)
    ↓
Phase 3 (Embeddings + Qdrant)
    ↓
Phase 4 (Agents)
    ↓
Phase 5 (API Endpoints)
    ↓              ↓
Phase 6 (DB)  Phase 7 (Frontend) [PARALLEL]
    ↓              ↓
Phase 8 (Sync Automation)
    ↓
Phase 9 (Testing)
    ↓
Phase 10 (Deployment)
```

### Parallel Work Opportunities

- **Phases 6 & 7** can run in parallel after Phase 5 API is stable
- **Phase 8** can start after Phase 3 if Phase 6 logging is mocked

### Critical Path (Minimum Viable)

**Phases 1 → 2 → 3 → 4 → 5 → 9 → 10** (MVP deployment)
- Phases 6 (DB logging) and 7 (frontend) can be simplified
- Phase 8 (sync automation) can be manual initially

### Required External Tools

**Build-Time**:
- Qdrant Cloud account (Phase 3)
- Neon Postgres instance (Phase 1)
- OpenAI API key (Phase 3, 4)
- Context7 MCP Server (Phase 2)

**Runtime**:
- Qdrant Cloud uptime
- Neon Postgres autoscaling
- OpenAI API rate limits
- MCP Server process availability

---

## 4. DETAILED SUBSYSTEM PLANS

### 4.1 MCP Ingestion Subsystem

**Purpose**: Extract, chunk, and structure textbook content

**Modules**:
- `mcp_client.py`: MCP Server wrapper
- `chunking.py`: Text splitting with overlap
- `metadata_extractor.py`: Heading hierarchy + anchors

**Data Flow**:
```
Markdown Files → MCP fs_readFile → Extracted Content
→ Chunking (500-800 tokens, 20% overlap) → Chunks + Metadata
→ Anchor Extraction → Structured Chunks
```

**Integration**: Feeds embedding subsystem (Phase 3)

**Testing**:
- Unit: Chunking with various token lengths
- Unit: Anchor extraction vs. Docusaurus format
- Integration: MCP connection + file reading
- Edge: Empty files, malformed markdown, code blocks

---

### 4.2 Embedding & Chunking Subsystem

**Purpose**: Generate vector embeddings for Qdrant

**Modules**:
- `embeddings.py`: OpenAI API with batching/retry
- `qdrant_client.py`: Qdrant CRUD

**Data Flow**:
```
Chunks → Batch (100) → OpenAI Embeddings API
→ Vectors (3072 dims) → Qdrant Upsert → Indexed
```

**Integration**: Used by Retrieval Agent (Phase 4)

**Testing**:
- Unit: Batching logic
- Unit: Qdrant upsert with mocks
- Integration: Full pipeline with small dataset
- Performance: Cost + time measurement
- Edge: Rate limits, network failures

---

### 4.3 Qdrant Integration Subsystem

**Purpose**: Vector search interface for retrieval

**Modules**:
- `qdrant_client.py`: Async wrapper
- `search.py`: Search with filters/scoring

**Data Flow**:
```
Query Text → Embed → Query Vector → Search Qdrant (top-k, threshold)
→ Top-k Chunks → [Optional] Filter by file_path → Ranked Chunks
```

**Integration**: Used by Answer Agent (Phase 4)

**Testing**:
- Unit: Search with known vectors
- Integration: Real Qdrant collection
- Performance: Query latency (<50ms)
- Edge: No results, low scores, concurrent

---

### 4.4 Multi-Agent Orchestration Engine

**Purpose**: Coordinate RAG agent pipeline

**Modules**:
- `retrieval.py`, `answer.py`, `citation.py`
- `orchestrator.py`: Pipeline coordination

**Data Flow**:
```
User Query → Retrieval Agent → Answer Agent → Citation Agent
→ Final Response
```

**Integration**: Called by API endpoint (Phase 5)

**Testing**:
- Unit: Each agent independently
- Integration: Full pipeline with mocks
- E2E: Real queries against test data
- Validation: Zero-hallucination (100 questions)
- Edge: Empty context, ambiguous, out-of-scope

---

### 4.5 Text Selection Query Subsystem

**Purpose**: Prioritize chunks from selected text context

**Modules**:
- Frontend: `TextSelector.js`
- Backend: `retrieval.py` (file_path filter)

**Data Flow**:
```
Text Selection → Extract + Parse URL → file_path
→ Query Request → Retrieval Agent (filter: file_path)
→ Boosted Chunks
```

**Integration**: Feeds Retrieval Agent

**Testing**:
- Unit: Selection detection
- Unit: URL → file_path extraction
- Integration: Metadata filter in Qdrant
- UX: Button appears <500ms

---

### 4.6 Citation Resolution Subsystem

**Purpose**: Link answer claims to source chunks

**Modules**:
- `citation.py`: Citation Agent
- `anchor_formatter.py`: URL construction

**Data Flow**:
```
Answer + Chunks → Match claims to chunks
→ Extract metadata → Format URLs (/docs/page#anchor)
→ Clickable Links
```

**Integration**: Final stage in agent pipeline

**Testing**:
- Unit: Citation matching algorithm
- Unit: URL formatting (edge cases)
- Validation: 90%+ accuracy (100 answers)
- Integration: Click test in browser

---

### 4.7 Neon Analytics & Telemetry Subsystem

**Purpose**: Log queries/feedback for monitoring

**Modules**:
- `database.py`: SQLAlchemy async engine
- `models/database.py`: ORM models
- `logging_middleware.py`: Request/response capture

**Data Flow**:
```
Query → Process → Response → Log to Postgres
→ [Optional] Feedback → Update Feedback Table
```

**Integration**: Used by all API endpoints

**Testing**:
- Unit: ORM constraints
- Integration: Middleware with mock requests
- Performance: 100 concurrent writes
- Analytics: Sample queries

---

### 4.8 UI Integration Subsystem (Docusaurus Plugin)

**Purpose**: Seamless chat interface in textbook

**Modules**:
- `chatWidget.js`, `ChatModal.js`, `FloatingButton.js`
- `TextSelector.js`, `useSession.js`, `useQueryAPI.js`

**Data Flow**:
```
Page Load → Initialize/Retrieve Session UUID → Store sessionStorage
→ User Input → POST /api/query → Render Response → Citation Click → Navigate
```

**Integration**: Calls backend API

**Testing**:
- Unit: React components
- Integration: API calls with mock backend
- E2E: Full browser flow (Playwright)
- UX: Load time <2s, responsive
- Edge: Network errors, timeouts

---

## 5. CONTENT SYNC PIPELINE PLAN

### Change Detection Strategy

**Approach**: Timestamp + file hash comparison

```python
async def detect_changes():
    last_sync = await db.get_last_sync_time()
    all_files = await mcp_client.list_markdown_files()

    changed_files = []
    for file in all_files:
        if await mcp_client.get_mtime(file) > last_sync:
            if await mcp_client.get_hash(file) != await db.get_hash(file):
                changed_files.append(file)

    stored_files = await db.get_all_indexed_files()
    deleted_files = set(stored_files) - set(all_files)

    return changed_files, deleted_files
```

### Incremental Re-Embedding

**Process**:
1. For changed files:
   - Delete old chunks (by file_path filter)
   - Re-chunk with current algorithm
   - Generate embeddings
   - Upsert new chunks
   - Update file hash

2. For deleted files:
   - Query Qdrant for chunks (file_path filter)
   - Delete all matching points
   - Remove from database index

### Error Handling

**Strategy**: Continue on failure, log errors, retry transient failures

```python
async def sync_file(file_path, sync_job):
    try:
        chunks = await mcp_client.extract_chunks(file_path)
        embeddings = await embed_chunks(chunks)
        await qdrant_client.upsert(chunks, embeddings)
        sync_job.files_processed += 1
    except Exception as e:
        sync_job.files_failed += 1
        sync_job.error_log.append({"file_path": file_path, "error": str(e)})
        logger.error(f"Failed: {file_path}: {e}")
        # Continue (do not raise)
```

### Embedding Refresh Strategy

**Selected**: Incremental only (change-based)
- Full refresh: Only on major version upgrade
- Incremental: Default for production
- Hybrid (monthly full refresh): Consider post-MVP

### MCP System Scheduling

**Cron Job** (production):
```bash
# Every 6 hours
0 */6 * * * /app/venv/bin/python /app/backend/scripts/sync_content.py >> /var/log/sync.log 2>&1
```

**Development**: Manual trigger
```bash
python backend/scripts/sync_content.py --dry-run
```

### Cost Optimization

- Only embed modified files
- Batch 100 chunks per API call
- Cache embeddings for unchanged content
- Alert if sync cost exceeds $1

---

## 6. TESTING PLAN

### 6.1 Unit Tests

**Coverage**: 90%+ backend, 80%+ frontend

**Backend Examples**:
```python
def test_chunk_with_overlap():
    text = "..." * 1000  # 1000 tokens
    chunks = chunk_text(text, chunk_size=500, overlap=0.2)
    assert len(chunks) == 2
    assert overlap(chunks[0], chunks[1]) >= 100

def test_heading_to_anchor():
    assert heading_to_anchor("## Forward Kinematics") == "forward-kinematics"
```

**Frontend Examples**:
```javascript
test('renders chat modal when open', () => {
  render(<ChatModal isOpen={true} />);
  expect(screen.getByRole('dialog')).toBeInTheDocument();
});
```

### 6.2 Integration Tests

**Environments**: Separate test Qdrant collection + Neon database

```python
@pytest.mark.asyncio
async def test_full_ingestion_pipeline():
    chunks = await mcp_client.extract_chunks("tests/fixtures/sample.md")
    embeddings = await embed_chunks([c.content_text for c in chunks])
    await qdrant_client.upsert(chunks, embeddings, collection="test")
    results = await qdrant_client.search("test query", collection="test")
    assert len(results) > 0
```

### 6.3 End-to-End RAG Tests

**Dataset**: 100 curated questions with ground truth

```python
@pytest.mark.asyncio
async def test_accurate_answer_with_citations():
    query = "What is the Denavit-Hartenberg convention?"
    response = await client.post("/api/query", json={"query": query, "session_id": str(uuid4())})
    assert response.status_code == 200
    assert "Denavit-Hartenberg" in response.json()["answer"]
    assert any("denavit-hartenberg" in c["anchor"] for c in response.json()["citations"])
```

**Hallucination Detection**: LLM-as-judge + manual review

### 6.4 Edge Case Tests

```python
def test_reject_non_english():
    response = client.post("/api/query", json={"query": "¿Qué es?", "session_id": str(uuid4())})
    assert response.status_code == 400
    assert "English queries only" in response.json()["error"]

@pytest.mark.asyncio
async def test_100_concurrent_queries():
    tasks = [client.post("/api/query", json={"query": f"q{i}", "session_id": str(uuid4())}) for i in range(100)]
    responses = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in responses)
```

### 6.5 Load Tests (Locust)

**Scenario**: 100 concurrent users

```python
class ChatUser(HttpUser):
    wait_time = between(5, 15)

    @task
    def ask_question(self):
        self.client.post("/api/query", json={"query": "What is kinematics?", "session_id": self.session_id})

    def on_start(self):
        self.session_id = str(uuid4())
```

**Run**: `locust -f tests/load/locustfile.py --users 100 --spawn-rate 10 --run-time 10m`

**Success**: p95 < 3s, error rate < 1%

### 6.6 Citation Accuracy Testing

**Manual Review**:
1. Generate 100 answers
2. Verify each citation:
   - Link resolves (200 OK)
   - Anchor exists on page
   - Linked section contains cited info
3. Calculate: (correct / total) × 100

**Target**: 90%+

---

## 7. DEPLOYMENT PLAN

### 7.1 Backend (Railway)

**Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY scripts/ ./scripts/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Variables** (Railway):
```
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
DATABASE_URL=postgresql://...
FRONTEND_URL=https://your-docs.vercel.app
LOG_LEVEL=INFO
```

**Deploy**: `railway init && railway up`

### 7.2 Qdrant Cloud Setup

1. Create cluster (us-east-1, Free tier)
2. Create collection via script:
```python
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
client.create_collection(
    collection_name="textbook_chunks",
    vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
)
```
3. Enable daily snapshots (7-day retention)

### 7.3 Neon Postgres Setup

1. Create database: `rag_chatbot`
2. Run migrations: `python scripts/init_database_production.py`
3. Enable auto-backups (24-hour retention)

### 7.4 Docusaurus (Vercel)

1. Configure plugin in `docusaurus.config.js`:
```javascript
module.exports = { plugins: ['./src/plugins/rag-chatbot'] };
```
2. Set env: `REACT_APP_API_URL=https://your-app.railway.app`
3. Deploy: `npm run build && vercel --prod`

### 7.5 Secrets Management

**Backend** (Railway): OpenAI key, Qdrant key, DB URL, Admin API key

**Frontend** (Vercel): API URL (not secret, but env-specific)

**Security**: Never commit to Git, rotate quarterly

### 7.6 Observability

**1. Logging** (structlog, JSON format)

**2. Error Tracking** (Sentry)
```python
sentry_sdk.init(dsn="...", environment="production", traces_sample_rate=0.1)
```

**3. Uptime Monitoring** (UptimeRobot): Monitor `/health` every 5 min

**4. Cost Monitoring**: OpenAI spending limit ($50/month), alerts on $10/day spike

**5. Dashboards**: Railway (logs, resources), Sentry (errors), Neon (queries)

### 7.7 Deployment Checklist

**Pre**:
- ✅ Tests passing
- ✅ Secrets configured
- ✅ Qdrant/Neon ready
- ✅ Health check works
- ✅ CORS configured

**Deploy**:
- ✅ Railway + Vercel deployed
- ✅ Backend/frontend verified
- ✅ Test query successful

**Post**:
- ✅ Run initial sync
- ✅ Monitor logs (24hr)
- ✅ Configure alerts
- ✅ Schedule cron

---

## 8. RISK PLAN & MITIGATION

### Critical Risks

**1. OpenAI API Rate Limits**
- **Impact**: High (blocks queries)
- **Mitigation**: Exponential backoff, caching, batch embeddings, monitor headers
- **Rollback**: Serve cached answers during outage

**2. Qdrant Cloud Downtime**
- **Impact**: High (no retrieval)
- **Mitigation**: Circuit breaker, status monitoring, daily snapshots
- **Rollback**: Restore from snapshot

**3. Embedding Cost Overrun**
- **Impact**: Medium (budget exceeded)
- **Mitigation**: Spending limit ($50/month), change detection, cost alerts
- **Rollback**: Pause automated sync, manual only

**4. Hallucinated Answers**
- **Impact**: Critical (misinformation)
- **Mitigation**: Strict prompt, 100-question validation, feedback loop, logging
- **Rollback**: Disable chatbot, add disclaimer

**5. Citation Link Breakage**
- **Impact**: Medium (poor UX)
- **Mitigation**: Test after restructure, automated link checker, 404 monitoring
- **Rollback**: Regenerate embeddings after migration

### Technical Bottlenecks

**1. Vector Search Latency** (target: p95 < 100ms)
- **Mitigation**: HNSW indexing, reduce k if needed, monitor collection size
- **Contingency**: Upgrade Qdrant tier

**2. Database Connection Pool Exhaustion** (target: 100 concurrent users)
- **Mitigation**: Neon autoscaling, SQLAlchemy pooling (size=20), monitor connections
- **Contingency**: Increase pool or upgrade tier

**3. GPT-4 Latency** (target: p95 < 3s total)
- **Mitigation**: GPT-4 Turbo, limit context to top-5, max_tokens=500
- **Contingency**: Switch to GPT-3.5 Turbo

### Mitigation Strategies

**Circuit Breaker**:
```python
@circuit(failure_threshold=3, recovery_timeout=60)
async def call_qdrant(query):
    return await qdrant_client.search(query)
```

**Graceful Degradation**: Return generic errors, continue processing, log locally

**Rate Limiting**:
```python
@limiter.limit("10/minute")
async def process_query(request):
    ...
```

### Rollback Plan

**Scenario**: Critical bug in production

1. **Immediate**: Rollback to previous Railway build, display maintenance banner
2. **Investigation**: Review Sentry + Railway logs, reproduce in staging
3. **Fix**: Hotfix on branch, test, deploy, monitor 24hr
4. **Post-Mortem**: Document root cause, add regression test, update checklist

### Recovery & Logging

**Data Recovery**:
- Qdrant: Restore from daily snapshot (max 24hr loss)
- Neon: Restore from backup (24hr retention)
- Code: Git revert

**Logging Levels**:
- ERROR: Immediate attention
- WARN: Degraded performance
- INFO: Successful operations
- DEBUG: Detailed traces (disabled in prod)

**Retention**: Railway (7d), Sentry (30d), Database (90d)

**Alerting**:
- Critical: PagerDuty/Slack (API down, DB unreachable)
- Warning: Email (cost spike, slow queries)
- Info: Dashboard (daily sync summary)

---

## 9. DELIVERY MILESTONES

**M1: Foundation Ready** (End of Phase 3)
- ✅ Environment setup
- ✅ MCP extracting/chunking
- ✅ Embeddings in Qdrant
- ✅ Sample queries retrieving chunks
- **Validation**: 10 manual test queries

**M2: Multi-Agent Pipeline Functional** (End of Phase 4)
- ✅ Agents implemented
- ✅ E2E pipeline working
- ✅ Citations formatted
- **Validation**: 20 test queries with accurate answers

**M3: Backend API Stable** (End of Phase 5)
- ✅ REST API deployed
- ✅ Validation + error handling
- ✅ Language detection
- ✅ Health checks
- **Validation**: Postman collection 100% success

**M4: Database Integration Complete** (End of Phase 6)
- ✅ Queries/feedback logged
- ✅ Analytics queries functional
- ✅ Sync jobs tracked
- **Validation**: Query 24hr analytics

**M5: Chat UI Integrated** (End of Phase 7)
- ✅ Plugin installed
- ✅ Floating button on all pages
- ✅ Session UUID managed
- ✅ Text selection functional
- **Validation**: Test 3 browsers (Chrome, Firefox, Safari)

**M6: Full System End-to-End** (End of Phase 8)
- ✅ Automated sync running
- ✅ All components integrated
- ✅ User can ask → receive cited answer
- ✅ Citations navigate correctly
- **Validation**: 10 users test for 1hr

**M7: Testing & Hardening Complete** (End of Phase 9)
- ✅ 90%+ coverage (backend)
- ✅ 100 questions validated (zero hallucination)
- ✅ Load test: 100 concurrent users
- ✅ Citation accuracy: 90%+
- **Validation**: All spec.md success criteria met

**M8: Production Deployment** (End of Phase 10)
- ✅ Railway + Vercel deployed
- ✅ Monitoring/alerting configured
- ✅ Initial sync complete
- ✅ Stable 72 hours
- **Validation**: Health check 200, zero critical errors

---

## 10. FINAL SUMMARY

This comprehensive plan provides an engineering-grade roadmap for the Phase 2 RAG Chatbot System, with:

**Architecture Highlights**:
- Multi-agent RAG pipeline (Retrieval → Answer → Citation)
- MCP-driven content ingestion with Docusaurus anchor extraction
- Qdrant Cloud for vector storage (3072-dim embeddings)
- Neon Postgres for analytics and telemetry
- Docusaurus chat widget with session-per-tab tracking

**Key Technical Decisions**:
1. OpenAI text-embedding-3-large for embeddings (cost-effective, high accuracy)
2. GPT-4 for Answer Agent (prevents hallucination via strict prompting)
3. FastAPI backend (native async, excellent performance)
4. Incremental sync with change detection (cost optimization)
5. sessionStorage UUID for privacy-preserving session tracking

**Risk Mitigation**:
- Circuit breakers for external services
- Exponential backoff for rate limits
- Zero-hallucination validation (100 test questions)
- Comprehensive monitoring and alerting

**Success Metrics** (from spec.md):
- ✅ Query response < 3s p95
- ✅ Zero hallucination (100 test questions)
- ✅ Citation accuracy > 90%
- ✅ 100 concurrent users supported
- ✅ Embedding cost < $0.50 per 100 pages

**Estimated Effort**: 60-90 hours (Phases 1-10)

**Critical Path**: Phases 1 → 2 → 3 → 4 → 5 → 9 → 10

**Next Step**: Run `/sp.tasks` to generate actionable implementation tasks

**Plan Status**: ✅ Ready for task generation

---

**Generated Artifacts**:
- `research.md` (Phase 0: Technology decisions)
- `data-model.md` (Phase 1: Entity schemas)
- `contracts/openapi.yaml` (Phase 1: API specification)
- `quickstart.md` (Phase 1: Developer guide)

**Branch**: `001-rag-chatbot-mcp`
**Date**: 2025-12-10
