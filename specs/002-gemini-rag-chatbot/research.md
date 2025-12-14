# Research Document: Gemini RAG Chatbot Implementation

**Feature**: 002-gemini-rag-chatbot
**Date**: 2025-12-14
**Purpose**: Resolve technical unknowns and document best practices for RAG chatbot implementation

---

## 1. Gemini Embedding API Integration

### Decision: Use `google-generativeai` Python SDK with `models/embedding-001`

**Rationale**:
- Official Google SDK provides native support for `gemini-embedding-001` model
- Returns 768-dimensional embeddings suitable for semantic search
- Handles authentication, rate limiting, and retries internally
- Well-documented with production-ready error handling

**Model Specification**:
- Model name: `models/embedding-001`
- Dimension: 768
- Input limit: ~2048 tokens per request
- Batch embedding support: Yes (process multiple texts in single API call)
- Task type parameter: `retrieval_document` for indexing, `retrieval_query` for user questions

**Alternatives Considered**:
1. **OpenAI embeddings**: Explicitly excluded per spec requirements
2. **Custom embedding models**: Rejected due to complexity and maintenance burden
3. **Gemini text models for embeddings**: Not recommended; dedicated embedding models optimized for retrieval

**Implementation Pattern**:
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# For document chunks during ingestion
result = genai.embed_content(
    model="models/embedding-001",
    content="chunk text here",
    task_type="retrieval_document"
)
embedding_vector = result['embedding']  # 768-dim list

# For user queries
result = genai.embed_content(
    model="models/embedding-001",
    content="user question here",
    task_type="retrieval_query"
)
query_vector = result['embedding']
```

**Rate Limits & Best Practices**:
- Free tier: 60 requests/minute
- Implement exponential backoff for rate limit errors
- Batch embeddings during ingestion (group chunks into single request where possible)
- Cache embeddings; re-generate only for new/modified content

---

## 2. Chunking Strategy for Docusaurus Markdown Content

### Decision: Hierarchical chunking with metadata preservation

**Rationale**:
- Docusaurus books have clear hierarchy (chapters → sections → paragraphs)
- Preserving document structure improves retrieval accuracy
- Metadata (chapter, section headings) provides critical context

**Chunking Parameters**:
- Target chunk size: 512-1024 tokens (~400-800 words)
- Overlap: 128 tokens (20-25% overlap to preserve context across boundaries)
- Split on: Paragraph boundaries, code blocks, headings
- Preserve: Frontmatter metadata, heading hierarchy, code block integrity

**Implementation Approach**:
1. Parse Markdown/MDX files using `markdown-it` or `mdast`
2. Extract frontmatter (title, sidebar position, tags)
3. Split on heading boundaries (H1, H2, H3) to maintain semantic sections
4. If section exceeds max chunk size, split on paragraph boundaries with overlap
5. Never split code blocks mid-block; treat as atomic units
6. Attach metadata to each chunk: file path, heading path, source URL

**Alternatives Considered**:
1. **Fixed-size chunking (e.g., 500 tokens)**: Rejected; breaks semantic coherence
2. **Sentence-based chunking**: Too granular; loses document context
3. **Full-document indexing**: Exceeds token limits; poor retrieval precision

**Metadata Schema Per Chunk**:
```json
{
  "chunk_text": "actual content here...",
  "file_path": "docs/chapter-01/section-03.md",
  "chapter": "Chapter 1: Introduction",
  "section": "1.3 Core Concepts",
  "heading_path": ["Introduction", "Core Concepts"],
  "source_url": "https://book-url.com/chapter-01/section-03",
  "chunk_index": 2,
  "total_chunks": 5
}
```

---

## 3. Qdrant Cloud Configuration

### Decision: Use Qdrant Cloud Free Tier with optimized collection settings

**Rationale**:
- Free tier provides 1GB storage (~500K vectors at 768 dimensions)
- Managed service eliminates infrastructure overhead
- Native Python client with async support for FastAPI integration
- Cosine similarity optimized for semantic search

**Collection Configuration**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

client.create_collection(
    collection_name="docusaurus_book_chunks",
    vectors_config=VectorParams(
        size=768,  # Gemini embedding dimension
        distance=Distance.COSINE  # Optimal for semantic similarity
    )
)
```

**Indexing Pattern**:
- Use UUIDs or content-based hashing for point IDs
- Store full metadata as payload (chapter, section, URL, chunk_index)
- Enable payload indexing on frequently filtered fields (e.g., chapter)
- Batch upsert during ingestion (100-500 points per batch)

**Search Pattern**:
```python
search_results = client.search(
    collection_name="docusaurus_book_chunks",
    query_vector=query_embedding,
    limit=5,  # Top-k retrieval (3-5 recommended)
    with_payload=True,  # Include metadata
    score_threshold=0.7  # Minimum similarity score
)
```

**Re-indexing Strategy**:
- Detect modified files via timestamp or hash comparison
- Delete old points for changed files
- Upsert new embeddings for modified content
- Keep ingestion idempotent: same input → same index state

**Alternatives Considered**:
1. **Self-hosted Qdrant**: Rejected; adds deployment complexity
2. **Pinecone**: Viable but Qdrant preferred for open-source compatibility
3. **FAISS (local vector search)**: Rejected; lacks managed scaling and persistence

---

## 4. Neon Serverless Postgres Usage

### Decision: Use Neon for chunk metadata and session tracking

**Rationale**:
- Free tier: 0.5GB storage, sufficient for metadata (~10-50KB per book)
- Serverless auto-scaling reduces operational overhead
- Native Postgres compatibility with `asyncpg` for FastAPI
- Separation of concerns: Qdrant stores vectors, Postgres stores metadata

**Schema Design**:

**Table: `chunks`**
```sql
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_text TEXT NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    chapter VARCHAR(256),
    section VARCHAR(256),
    heading_path TEXT[],  -- Array of headings
    source_url VARCHAR(512),
    chunk_index INT,
    total_chunks INT,
    qdrant_point_id UUID NOT NULL,  -- Reference to Qdrant vector
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_file_path ON chunks(file_path);
CREATE INDEX idx_qdrant_point_id ON chunks(qdrant_point_id);
```

**Table: `query_logs` (optional, for monitoring)**
```sql
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    response_text TEXT,
    chunks_retrieved INT,
    response_time_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Connection Pattern**:
```python
from asyncpg import create_pool

pool = await create_pool(
    dsn=os.getenv("DATABASE_URL"),
    min_size=2,
    max_size=10
)
```

**Alternatives Considered**:
1. **Storing all metadata in Qdrant payload**: Viable but less flexible for complex queries
2. **SQLite**: Rejected; doesn't scale for serverless deployments
3. **No metadata storage**: Rejected; loses traceability and re-indexing capability

---

## 5. FastAPI Best Practices for RAG Backend

### Decision: Async FastAPI with structured error handling and observability

**Rationale**:
- Async I/O critical for external API calls (Gemini, Qdrant, Postgres)
- Pydantic models enforce contract validation
- Built-in OpenAPI docs for frontend integration
- Middleware for CORS, rate limiting, and logging

**API Structure**:

**POST /query**
```python
from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    max_results: int = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    confidence: float
    response_time_ms: int

class SourceCitation(BaseModel):
    chapter: str
    section: str
    source_url: str
    relevance_score: float
```

**GET /health**
```python
class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    qdrant_connected: bool
    postgres_connected: bool
    gemini_api_available: bool
```

**Error Handling**:
- 400: Invalid request (malformed query, missing fields)
- 429: Rate limit exceeded
- 500: Internal server error (Gemini API down, Qdrant unreachable)
- 503: Service degraded (one dependency unavailable)

**Middleware Stack**:
1. CORS: Restrict to Docusaurus domain (whitelist approach)
2. Rate limiting: 100 requests/min per IP (using `slowapi`)
3. Logging: Structured JSON logs with request ID tracing
4. Request timeout: 10s max per request

**Alternatives Considered**:
1. **Flask**: Rejected; lacks native async support
2. **Django**: Rejected; too heavy for simple API
3. **Raw ASGI (Starlette)**: Viable but FastAPI adds valuable abstractions

---

## 6. React Component Integration with Docusaurus

### Decision: Standalone React component as Docusaurus custom plugin

**Rationale**:
- Docusaurus supports custom React components via Swizzling or plugins
- Encapsulate chatbot as self-contained widget
- No modifications to existing book pages or content
- Can be injected globally or per-page via theme customization

**Integration Approach**:

**Option 1: Custom Docusaurus Plugin (Recommended)**
- Create `docusaurus-plugin-rag-chat` package
- Inject `<ChatWidget />` into Docusaurus theme layout
- Configure via `docusaurus.config.js`:
```javascript
module.exports = {
  plugins: [
    [
      './plugins/rag-chat',
      {
        apiUrl: 'https://backend-url.com',
        position: 'bottom-right',  // Floating chat button
        primaryColor: '#007bff'
      }
    ]
  ]
};
```

**Option 2: Swizzle Theme Component**
- Swizzle `DocItem/Layout` or `Root` component
- Inject `<ChatWidget />` directly into theme JSX
- Simpler but less portable

**Component Architecture**:
```
<ChatWidget>
  └─ <ChatButton> (toggle visibility)
  └─ <ChatPanel>
      ├─ <MessageList>
      │   └─ <MessageBubble> (user/assistant)
      ├─ <InputBox>
      └─ <SourceCitations>
```

**State Management**:
- Local component state for conversation history (useState)
- Optional: React Context for global session persistence
- No Redux (overkill for simple chat interface)

**API Client**:
```typescript
async function sendQuery(question: string): Promise<QueryResponse> {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, max_results: 3 })
  });
  if (!response.ok) throw new Error('Query failed');
  return response.json();
}
```

**Alternatives Considered**:
1. **Embedded iframe**: Rejected; worse UX and harder to style
2. **Separate SPA**: Rejected; requires separate deployment and breaks integration
3. **Vanilla JS widget**: Viable but React preferred for Docusaurus compatibility

---

## 7. Deployment Strategy

### Decision: Separate deployments for backend (cloud platform) and frontend (embedded in Docusaurus on GitHub Pages)

**Backend Deployment**:
- **Platform**: Render.com, Railway.app, or Fly.io (all offer free tiers)
- **Docker container**: Package FastAPI app with dependencies
- **Environment variables**: `GEMINI_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `DATABASE_URL`
- **Health checks**: `/health` endpoint for uptime monitoring
- **HTTPS**: Required (all platforms provide automatic TLS)

**Frontend Deployment**:
- Embed chatbot component into Docusaurus build
- Deploy to GitHub Pages alongside book
- Configure `apiUrl` to point to backend deployment
- Enable CORS on backend for GitHub Pages domain

**Configuration Management**:
- Backend: `.env` file (local) + platform env vars (production)
- Frontend: Build-time env vars in `docusaurus.config.js`
- Security: Never commit API keys; use `.env.example` template

**Alternatives Considered**:
1. **Monolithic deployment**: Rejected; couples frontend and backend unnecessarily
2. **Serverless functions (AWS Lambda)**: Viable but adds cold start latency
3. **Self-hosted VPS**: Rejected; excessive operational overhead

---

## 8. Response Generation LLM

### Decision: Use Google Gemini Pro for response generation (inferred from embedding choice)

**Rationale**:
- Consistent Google AI ecosystem (embeddings + generation)
- Gemini Pro available via same `google-generativeai` SDK
- Free tier: 60 requests/minute
- Strong instruction-following for RAG prompts

**Prompt Template**:
```
You are a helpful assistant answering questions about a technical book.

Context from the book:
{retrieved_chunks}

User question: {user_question}

Instructions:
1. Answer the question using ONLY information from the provided context
2. Cite specific chapters and sections in your answer
3. If the context doesn't contain enough information, say "I don't have enough information in the book to answer this question fully"
4. Do not make up or infer information not present in the context

Answer:
```

**Alternatives Considered**:
1. **OpenAI GPT-4**: Excluded to maintain Gemini-only constraint
2. **Claude**: Viable but requires separate API integration
3. **Open-source LLMs (Llama, Mistral)**: Rejected; adds hosting complexity

---

## Summary of Key Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Embeddings | Gemini `embedding-001` (768-dim) | Spec requirement; optimized for retrieval |
| Vector DB | Qdrant Cloud (Free Tier) | Managed service, cosine similarity, 1GB free |
| Metadata DB | Neon Serverless Postgres | Lightweight, free tier, separation of concerns |
| Backend | FastAPI (Python 3.11+, async) | Native async, Pydantic validation, OpenAPI docs |
| Frontend | React component in Docusaurus | Native integration, no book content changes |
| Chunking | Hierarchical (512-1024 tokens, 128 overlap) | Preserves structure, semantic coherence |
| Deployment | Backend: Render/Railway, Frontend: GitHub Pages | Free tiers, separate concerns, HTTPS by default |
| Response LLM | Gemini Pro | Consistent ecosystem, free tier, strong RAG prompts |

---

## Open Questions & Risks

1. **Gemini API rate limits during high traffic**: Mitigation via aggressive client-side rate limiting and caching
2. **Free-tier quota exhaustion**: Monitor usage; implement graceful degradation; document upgrade paths
3. **Chunking quality for code-heavy sections**: Test with real book content; adjust strategy if needed
4. **CORS configuration for GitHub Pages**: Ensure backend whitelist includes correct domain (user.github.io)

---

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts, quickstart.md) with all technical unknowns resolved.
