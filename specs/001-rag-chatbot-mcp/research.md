# Research: Phase 2 RAG Chatbot System

**Feature**: 001-rag-chatbot-mcp
**Date**: 2025-12-10
**Phase**: 0 - Technology Research & Decision Log

## Overview

This research document resolves all technical unknowns and design decisions for the integrated RAG chatbot system. It consolidates technology choices, best practices, and architectural patterns for the full stack.

---

## 1. MCP Server Integration Strategy

### Decision: Use Context7 MCP Server with async client wrapper

**Rationale**:
- Context7 MCP Server provides file system tools for markdown extraction
- Supports async operations required by FastAPI backend
- Native support for metadata extraction and structured content processing
- Established MCP protocol for tool invocation

**Alternatives Considered**:
1. **Custom file parser**: Rejected due to reinvention of tested functionality
2. **Direct file I/O in FastAPI**: Rejected due to lack of change detection and structured metadata

**Implementation Pattern**:
```python
# MCP client wrapper for async operations
from mcp import Client, StdioServerParameters
from mcp.types import Tool

class MCPContentExtractor:
    async def read_markdown_files(self, path: str) -> List[Dict]:
        # Use fs_readFile tool for content extraction
        # Extract heading hierarchy and anchors
        # Return structured chunks with metadata
```

**Best Practices**:
- Maintain persistent MCP connection with connection pooling
- Implement exponential backoff for MCP tool failures
- Cache file modification timestamps to avoid redundant reads
- Use MCP system tools for sync scheduling (cron-like patterns)

---

## 2. Multi-Agent RAG Architecture

### Decision: OpenAI Agents SDK with 3-agent orchestration pattern

**Rationale**:
- OpenAI Agents SDK (previously ChatKit) provides structured agent creation and orchestration
- Separation of concerns: Retrieval → Answer → Citation
- Each agent has clear responsibility and testable interface
- Built-in support for context management and tool use

**Architecture**:

```
User Query → Retrieval Agent (Qdrant) → Answer Agent (GPT-4) → Citation Agent → Response
                    ↓                           ↓                      ↓
               Top-k chunks              Synthesized answer      Linked citations
```

**Agent Responsibilities**:

1. **Retrieval Agent**:
   - Input: User query string + optional selected text context
   - Tool: Qdrant vector search (cosine similarity)
   - Output: Top-k chunks (k=5 default) with similarity scores > 0.7
   - Handles: Text selection prioritization, query embedding

2. **Answer Agent**:
   - Input: User query + retrieved chunks
   - Model: GPT-4 (for accuracy and reasoning)
   - System prompt: "Use ONLY provided context. Do not add external information."
   - Output: Coherent natural language response
   - Handles: Context synthesis, hallucination prevention

3. **Citation Agent**:
   - Input: Answer text + source chunks + metadata
   - Logic: Match answer claims to source chunks
   - Output: Citations with format `[Source: {title}#{anchor}]`
   - Handles: Anchor link generation, citation formatting

**Alternatives Considered**:
1. **Single agent with tool calling**: Rejected due to complexity and hallucination risk
2. **LangChain**: Rejected due to overhead and spec requirement for OpenAI SDK

**Implementation Pattern**:
```python
from openai import OpenAI
from openai.agents import Agent

# Retrieval Agent
retrieval_agent = Agent(
    name="retrieval",
    instructions="Search vector database for relevant chunks",
    tools=[qdrant_search_tool]
)

# Answer Agent
answer_agent = Agent(
    name="answer",
    instructions="Synthesize answer from context only. No external info.",
    model="gpt-4"
)

# Citation Agent
citation_agent = Agent(
    name="citation",
    instructions="Link answer claims to source chunks with anchors"
)
```

**Best Practices**:
- Keep agent prompts minimal and role-focused
- Pass metadata through agent chain without modification
- Implement timeout per agent (5s retrieval, 10s answer, 3s citation)
- Log agent inputs/outputs for debugging and analytics

---

## 3. Embedding Strategy

### Decision: OpenAI text-embedding-3-large with batching

**Rationale**:
- Higher dimensional embeddings (3072) improve retrieval accuracy
- Cost-effective at $0.13 per 1M tokens
- Native async support in OpenAI Python SDK
- Proven performance for technical content

**Chunk Configuration**:
- **Size**: 500-800 tokens per chunk
- **Overlap**: 20% (100-160 tokens) to preserve context at boundaries
- **Metadata**: file_path, document_title, heading_hierarchy, section_anchor, chunk_index

**Batching Strategy**:
- Batch size: 100 chunks per API call (max 8192 tokens per request)
- Parallel batching: 3 concurrent API calls
- Cost estimate: 50-page textbook (~100k tokens) = ~$0.013

**Alternatives Considered**:
1. **text-embedding-ada-002**: Rejected due to lower accuracy
2. **Open-source models (e.g., sentence-transformers)**: Rejected due to deployment complexity

**Implementation Pattern**:
```python
from openai import AsyncOpenAI

async def embed_chunks(chunks: List[str]) -> List[List[float]]:
    client = AsyncOpenAI()
    response = await client.embeddings.create(
        model="text-embedding-3-large",
        input=chunks
    )
    return [e.embedding for e in response.data]
```

**Best Practices**:
- Retry with exponential backoff (max 3 attempts)
- Cache embeddings to avoid re-processing unchanged chunks
- Monitor token usage and set cost alerts
- Validate embedding dimensions match Qdrant collection (3072)

---

## 4. Vector Database: Qdrant Cloud

### Decision: Qdrant Cloud with async Python client

**Rationale**:
- Managed service eliminates infrastructure overhead
- Native async operations for FastAPI integration
- Excellent performance for similarity search (<50ms p95)
- Metadata filtering for chunk prioritization

**Collection Configuration**:
```python
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

collection_config = VectorParams(
    size=3072,  # text-embedding-3-large dimensions
    distance=Distance.COSINE
)
```

**Search Strategy**:
- Default: Top-5 chunks with score > 0.7
- Text selection queries: Boost chunks from same page (metadata filter)
- Query parameters: limit=5, score_threshold=0.7

**Upsert Logic**:
- Use file_path + chunk_index as point ID
- Update existing points on content change
- Delete points when files removed

**Alternatives Considered**:
1. **Pinecone**: Rejected due to higher cost
2. **Self-hosted Qdrant**: Rejected due to operational overhead
3. **Weaviate**: Rejected due to less mature async Python support

**Best Practices**:
- Implement connection pooling (max 10 concurrent connections)
- Use payload indexing for metadata filtering
- Monitor query latency and collection size
- Enable snapshotting for disaster recovery

---

## 5. Relational Database: Neon Postgres

### Decision: Neon Postgres serverless with async SQLAlchemy

**Rationale**:
- Serverless autoscaling matches variable query load
- Native PostgreSQL compatibility for complex analytics
- Built-in connection pooling (max 100 connections)
- Free tier sufficient for initial deployment

**Schema Design**:

```sql
-- Queries table
CREATE TABLE queries (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    user_session_id UUID NOT NULL,
    retrieved_chunk_ids TEXT[],
    answer_text TEXT,
    citations JSONB,
    similarity_scores FLOAT[],
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Feedback table
CREATE TABLE feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID REFERENCES queries(query_id),
    feedback_type VARCHAR(20) CHECK (feedback_type IN ('positive', 'negative')),
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Sync jobs table
CREATE TABLE sync_jobs (
    sync_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    status VARCHAR(20) CHECK (status IN ('running', 'completed', 'failed')),
    files_processed INT DEFAULT 0,
    files_failed INT DEFAULT 0,
    error_log JSONB,
    CONSTRAINT valid_status CHECK (
        (status = 'running' AND end_time IS NULL) OR
        (status IN ('completed', 'failed') AND end_time IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_queries_session ON queries(user_session_id);
CREATE INDEX idx_queries_timestamp ON queries(timestamp);
CREATE INDEX idx_feedback_query ON feedback(query_id);
CREATE INDEX idx_sync_jobs_status ON sync_jobs(status);
```

**Alternatives Considered**:
1. **SQLite**: Rejected due to lack of remote access for analytics
2. **MongoDB**: Rejected due to spec requirement for relational schema

**Best Practices**:
- Use async SQLAlchemy with asyncpg driver
- Implement connection pooling (min=5, max=20)
- Enable query logging for slow queries (>500ms)
- Set up automated backups (daily snapshots)

---

## 6. Backend Framework: FastAPI

### Decision: FastAPI with async/await throughout

**Rationale**:
- Native async support for I/O-bound operations
- Automatic OpenAPI documentation
- Built-in request validation with Pydantic
- Excellent performance (comparable to Node.js/Go)

**API Structure**:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="RAG Chatbot API")

class QueryRequest(BaseModel):
    query: str
    session_id: str
    selected_text: str | None = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Dict[str, str]]
    sources: List[str]

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    # Orchestrate multi-agent RAG pipeline
    pass
```

**Middleware Stack**:
1. CORS (allow Docusaurus domain)
2. Request logging
3. Error handling (structured JSON responses)
4. Language detection (reject non-English)

**Alternatives Considered**:
1. **Flask**: Rejected due to lack of native async
2. **Django**: Rejected due to overhead for simple API

**Best Practices**:
- Use dependency injection for DB/MCP clients
- Implement circuit breakers for external services
- Set request timeout (30s max)
- Enable compression for large responses

---

## 7. Frontend Integration: Docusaurus

### Decision: Custom React plugin with sessionStorage

**Rationale**:
- Docusaurus 3.x supports custom plugins
- React enables rich chat UI
- sessionStorage for browser-tab-scoped sessions
- No authentication required (session UUID only)

**Implementation Approach**:

```javascript
// plugins/rag-chatbot/index.js
module.exports = function (context, options) {
  return {
    name: 'rag-chatbot',

    getClientModules() {
      return ['./chatWidget'];
    },
  };
};

// chatWidget.js
import React from 'react';

export function ChatWidget() {
  const [sessionId, setSessionId] = React.useState(() => {
    let id = sessionStorage.getItem('chat_session_id');
    if (!id) {
      id = crypto.randomUUID();
      sessionStorage.setItem('chat_session_id', id);
    }
    return id;
  });

  // Render floating button + modal
}
```

**Text Selection Integration**:
```javascript
document.addEventListener('mouseup', () => {
  const selectedText = window.getSelection().toString();
  if (selectedText.length > 10) {
    showAskAIButton(selectedText);
  }
});
```

**Best Practices**:
- Lazy-load chat UI (code splitting)
- Debounce text selection (300ms)
- Cache chat history in memory (not persisted)
- Match Docusaurus theme colors dynamically

---

## 8. Citation Format: Docusaurus Heading Anchors

### Decision: Use auto-generated heading IDs with hash links

**Rationale**:
- Docusaurus auto-generates heading anchors from markdown headings
- Format: `/docs/page-name#heading-id` (e.g., `/docs/robotics#kinematics`)
- No manual anchor management required
- Deep links work across builds

**Anchor Extraction**:
```python
# During MCP ingestion
import re

def extract_heading_anchor(heading_text: str) -> str:
    # Docusaurus converts: "## Forward Kinematics" → "forward-kinematics"
    return re.sub(r'[^a-z0-9]+', '-', heading_text.lower()).strip('-')
```

**Citation Rendering**:
```markdown
The forward kinematics equation... [Source: Robotics Fundamentals#forward-kinematics]
```

Rendered as:
```html
<a href="/docs/robotics#forward-kinematics">Source: Robotics Fundamentals#forward-kinematics</a>
```

**Best Practices**:
- Validate anchors during ingestion (check heading exists)
- Store full URL in metadata (not just anchor)
- Test citation links in deployment environment
- Handle edge cases (special characters, duplicate headings)

---

## 9. Session Management: Browser sessionStorage

### Decision: UUID in sessionStorage, expires on tab close

**Rationale**:
- No server-side session storage required
- Privacy-preserving (no cookies or tracking)
- Automatic cleanup on tab close
- Aligns with "session-per-tab" requirement

**Implementation**:
```javascript
// Generate session ID on first chat interaction
function getOrCreateSessionId() {
  let sessionId = sessionStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    sessionStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
}
```

**Session Scope**:
- Each browser tab = unique session
- No cross-tab synchronization
- No persistence beyond tab lifetime
- Server logs session_id for analytics only

**Best Practices**:
- Do not use session_id for authorization
- Include session_id in all API requests for telemetry
- Monitor session duration distribution
- Clear chat history on tab close (no localStorage)

---

## 10. Language Detection & Guardrails

### Decision: FastAPI middleware with langdetect library

**Rationale**:
- langdetect provides fast, accurate language detection
- Reject non-English queries at API layer
- Clear error message to user
- Prevents wasted embedding/agent costs

**Implementation**:
```python
from langdetect import detect, LangDetectException

async def validate_language(query: str):
    try:
        lang = detect(query)
        if lang != 'en':
            raise HTTPException(
                status_code=400,
                detail="This chatbot supports English queries only. Please rephrase your question in English."
            )
    except LangDetectException:
        # Ambiguous or too short - allow through
        pass
```

**Scope Guardrails**:
- Detect off-topic queries (e.g., "weather in Paris")
- Use keyword matching + semantic similarity to textbook content
- Respond with: "This question is outside the scope of the textbook. Please ask about [topic areas]."

**Best Practices**:
- Log rejected queries for improvement
- Set detection threshold (80% confidence)
- Handle code snippets gracefully (ignore)
- Provide helpful scope boundary message

---

## 11. Content Sync Pipeline

### Decision: MCP-driven change detection with scheduled sync

**Rationale**:
- MCP system tools provide file watching capabilities
- Incremental updates reduce embedding cost
- Configurable schedule (default: 6 hours)
- Graceful error handling ensures continuity

**Sync Workflow**:

1. **Change Detection**: MCP file watcher monitors markdown directory
2. **File Diff**: Compare current files with last sync timestamp
3. **Chunk Extraction**: MCP reads modified files
4. **Embedding**: Batch embed new/changed chunks
5. **Qdrant Update**: Upsert new points, delete removed chunks
6. **Database Log**: Record sync job in Neon Postgres

**Implementation Pattern**:
```python
async def sync_content():
    sync_job = create_sync_job()

    try:
        modified_files = await mcp_client.detect_changes()

        for file_path in modified_files:
            chunks = await mcp_client.extract_chunks(file_path)
            embeddings = await embed_chunks(chunks)
            await qdrant_client.upsert(chunks, embeddings)
            sync_job.files_processed += 1

        sync_job.status = 'completed'
    except Exception as e:
        sync_job.status = 'failed'
        sync_job.error_log = str(e)
    finally:
        await save_sync_job(sync_job)
```

**Best Practices**:
- Run sync during low-traffic periods
- Implement partial failure recovery (continue on error)
- Monitor embedding cost per sync
- Alert on consecutive sync failures (3+)

---

## 12. Deployment Strategy

### Decision: Railway (backend) + Qdrant Cloud + Neon + Vercel/Netlify (frontend)

**Rationale**:
- Railway provides simple Python deployment with async support
- Managed services (Qdrant, Neon) eliminate infrastructure work
- Vercel/Netlify native Docusaurus support
- All platforms have free tiers for MVP

**Backend Deployment (Railway)**:
- Runtime: Python 3.11
- Workers: 2 (for async handling)
- Memory: 512MB (sufficient for FastAPI + clients)
- Environment variables: OpenAI API key, Qdrant URL, Neon connection string

**Frontend Deployment (Vercel)**:
- Build command: `npm run build`
- Output directory: `build/`
- Environment variable: `REACT_APP_API_URL` (backend URL)

**Alternatives Considered**:
1. **Fly.io**: Rejected due to complex config
2. **Render**: Viable alternative to Railway
3. **GitHub Pages**: Rejected for backend (static only)

**Best Practices**:
- Enable HTTPS (automatic on all platforms)
- Set up health check endpoint (`/health`)
- Configure CORS for frontend domain
- Monitor uptime (use UptimeRobot or similar)

---

## 13. Observability & Monitoring

### Decision: Structured logging + Neon analytics + Sentry for errors

**Rationale**:
- Structured logs (JSON) enable querying
- Neon database captures query analytics
- Sentry provides error tracking and alerting
- All integrate easily with FastAPI

**Logging Strategy**:
```python
import structlog

logger = structlog.get_logger()

logger.info("query_processed",
    query_id=query_id,
    session_id=session_id,
    retrieval_time_ms=retrieval_time,
    answer_time_ms=answer_time,
    num_citations=len(citations)
)
```

**Key Metrics**:
- Query latency (p50, p95, p99)
- Retrieval accuracy (top-k hit rate)
- Embedding cost per sync
- Error rate by type
- Session duration distribution

**Best Practices**:
- Log all external API calls (OpenAI, Qdrant)
- Set up alerts for latency spikes (>5s)
- Monitor Qdrant collection size growth
- Track feedback sentiment over time

---

## Summary

All technical unknowns resolved. Key decisions documented with rationale. Ready to proceed to Phase 1 (data model and API contracts).

**Next Steps**:
1. Generate `data-model.md` with entity schemas
2. Create API contracts in `/contracts/` directory
3. Update agent context with technology stack
4. Fill complete implementation plan template
