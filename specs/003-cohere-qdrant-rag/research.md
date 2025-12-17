# Phase 0: Research & Technical Decisions
**Feature**: RAG Chatbot Integration for Deployed Docusaurus Textbook (Cohere + Qdrant)
**Date**: 2025-12-16

## Executive Summary

This research document resolves technical unknowns and establishes the architectural foundation for implementing a production-ready RAG chatbot system using Cohere for embeddings/generation and Qdrant Cloud for vector storage.

## Research Areas

### 1. Cohere API Integration Strategy

**Decision**: Use Cohere Python SDK v5+ with separate clients for embedding and generation

**Rationale**:
- Official Python SDK provides high-level abstraction over REST API
- Supports both synchronous and asynchronous operations
- Built-in retry logic and error handling
- Type-safe interface with proper IDE support

**Key Technical Findings**:
- **Embedding Model**: `embed-english-v3.0` (1024 dimensions)
  - Optimized for semantic search use cases
  - Input type: `EmbedInputType.SEARCH_DOCUMENT` for ingestion, `EmbedInputType.SEARCH_QUERY` for queries
  - Max batch size: 96 texts per API call
  - Supports truncation strategies (START/END/NONE)
  - Output dimension: 1024 (default for v3.0)

- **Generation Model**: `command` or `command-r`
  - `command`: Stable, production-ready model
  - `command-r`: Retrieval-optimized variant with better citation support
  - Temperature: 0.3 (default for factual responses)
  - Citation quality: "accurate" mode for proper source attribution
  - Max tokens: No hard limit specified (let model decide completion)

**Implementation Approach**:
```python
# Initialization pattern
from cohere import Client

cohere_client = Client(api_key=os.getenv("COHERE_API_KEY"))

# Embedding pattern (batch processing)
response = cohere_client.embed(
    texts=[chunk1, chunk2, ...],  # Up to 96 chunks
    model="embed-english-v3.0",
    input_type="search_document",
    embedding_types=["float"]
)

# Generation pattern with RAG
response = cohere_client.chat(
    model="command-r",
    message=user_query,
    documents=[
        {"text": chunk.text, "id": chunk.id, "title": chunk.page_title}
        for chunk in retrieved_chunks
    ],
    citation_quality="accurate",
    temperature=0.3
)
```

**Alternatives Considered**:
- Direct REST API calls: Rejected due to lack of built-in retry logic and type safety
- OpenAI API: Explicitly excluded by requirements
- Gemini API: Explicitly excluded by requirements

---

### 2. Qdrant Cloud Integration & Collection Strategy

**Decision**: Use Qdrant Python Client with persistent gRPC connection and single collection architecture

**Rationale**:
- Official Python client supports both REST and gRPC (gRPC preferred for performance)
- Synchronous client sufficient for current scale (async can be added later if needed)
- Single collection simplifies management and reduces complexity
- Collection metadata filtering provides sufficient flexibility for multi-page organization

**Key Technical Findings**:
- **Collection Configuration**:
  - Vector size: 1024 (matches Cohere embed-english-v3.0)
  - Distance metric: Cosine similarity (standard for semantic search)
  - On-disk payload: Enable for better memory efficiency
  - Indexing: HNSW (Hierarchical Navigable Small World) - default, optimal for accuracy/speed tradeoff

- **Metadata Schema**:
  ```python
  payload = {
      "page_url": str,           # Full URL to source page
      "page_title": str,         # Page title for display
      "section_heading": str,    # Section/heading context
      "chunk_text": str,         # Full chunk text (for retrieval)
      "chunk_index": int,        # Sequential position in page
      "character_count": int,    # Length validation
      "ingestion_timestamp": str # ISO format timestamp
  }
  ```

- **Search Configuration**:
  - Default top-K: 5 results
  - Score threshold: 0.7 (similarity threshold to filter low-quality matches)
  - No pre-filtering by default (filter by page_url if specific page queries needed)

**Implementation Approach**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Initialize client
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=True
)

# Create collection (one-time setup)
qdrant_client.create_collection(
    collection_name=os.getenv("QDRANT_COLLECTION_NAME"),
    vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    on_disk_payload=True
)

# Upsert vectors (batch upload)
qdrant_client.upsert(
    collection_name=collection_name,
    points=[
        PointStruct(
            id=uuid.uuid4().hex,
            vector=embedding,
            payload=metadata
        )
        for embedding, metadata in chunks
    ]
)

# Search vectors
results = qdrant_client.search(
    collection_name=collection_name,
    query_vector=query_embedding,
    limit=5,
    score_threshold=0.7
)
```

**Alternatives Considered**:
- Multiple collections (one per page): Rejected due to management overhead and Qdrant collection limits
- Pinecone: Rejected as Qdrant Cloud specified in requirements
- Local Qdrant instance: Rejected as Qdrant Cloud specified in requirements

---

### 3. Content Extraction & Chunking Strategy

**Decision**: Use BeautifulSoup for HTML parsing with recursive text chunking preserving semantic boundaries

**Rationale**:
- BeautifulSoup is battle-tested for HTML parsing and Docusaurus-generated content
- Recursive chunking maintains semantic coherence better than fixed-size chunking
- Section-aware chunking preserves document structure

**Key Technical Findings**:
- **Optimal Chunk Size**: 500-800 characters with 100-character overlap
  - Balances context preservation with retrieval precision
  - Stays well within Cohere's embedding token limits (~2000 tokens)
  - Overlap ensures boundary concepts aren't lost

- **Extraction Strategy**:
  1. Fetch sitemap.xml and parse URLs
  2. For each URL, fetch HTML content
  3. Extract main content (typically within `<article>` or `.markdown` class in Docusaurus)
  4. Remove navigation, footers, and non-content elements
  5. Extract text while preserving structure (headings, paragraphs)
  6. Apply recursive chunking with semantic boundaries

- **Chunking Algorithm**:
  ```
  1. Start with full document text
  2. Split by major headings (h1, h2, h3)
  3. For sections > 800 chars:
     a. Split by paragraphs
     b. Combine small paragraphs until ~500-800 chars
     c. Add 100-char overlap from previous chunk
  4. Preserve heading context in each chunk's metadata
  ```

**Implementation Approach**:
```python
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Fetch sitemap
response = requests.get(sitemap_url)
root = ET.fromstring(response.content)
urls = [url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        for url in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url")]

# Extract content from each page
for url in urls:
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    # Docusaurus content is typically in article tag or main content div
    article = soup.find("article") or soup.find("main")

    # Extract title
    title = soup.find("h1").get_text() if soup.find("h1") else "Untitled"

    # Process sections with heading context
    chunks = recursive_chunk(article, target_size=700, overlap=100)
```

**Alternatives Considered**:
- LangChain document loaders: Rejected to minimize dependencies and maintain control
- Fixed-size character chunking: Rejected due to loss of semantic boundaries
- Sentence-based chunking: Rejected as too granular for textbook content

---

### 4. API Design & Rate Limiting

**Decision**: FastAPI with SlowAPI for rate limiting and simple API key authentication

**Rationale**:
- FastAPI provides automatic OpenAPI documentation and validation
- SlowAPI integrates seamlessly with FastAPI for rate limiting
- Simple API key auth sufficient for MVP (no user authentication needed)

**Key Technical Findings**:
- **Endpoint Structure**:
  ```
  POST /api/v1/query
    - Public endpoint
    - Rate limit: 10 requests/minute per IP
    - Input: { "query": str, "max_results": int (optional) }
    - Output: { "answer": str, "sources": [...], "metadata": {...} }

  POST /api/v1/ingest
    - Protected endpoint (requires API_KEY header)
    - No rate limit (authenticated admin use)
    - Input: { "force_refresh": bool (optional) }
    - Output: { "status": str, "pages_processed": int, "chunks_created": int }

  GET /api/v1/health
    - Public endpoint
    - No rate limit
    - Output: { "status": "healthy", "services": {...} }
  ```

- **CORS Configuration**:
  ```python
  from fastapi.middleware.cors import CORSMiddleware

  app.add_middleware(
      CORSMiddleware,
      allow_origins=[os.getenv("CORS_ORIGINS")],  # Vercel frontend URL
      allow_credentials=True,
      allow_methods=["GET", "POST"],
      allow_headers=["*"],
  )
  ```

- **Rate Limiting Strategy**:
  ```python
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address

  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter

  @app.post("/api/v1/query")
  @limiter.limit("10/minute")
  async def query_endpoint(...):
      ...
  ```

**Alternatives Considered**:
- Flask: Rejected in favor of FastAPI's modern async support and auto-documentation
- Django: Rejected as too heavyweight for API-only service
- OAuth2: Rejected as unnecessary for current scope (no user authentication)

---

### 5. Error Handling & Retry Strategy

**Decision**: Exponential backoff with tenacity library for transient failures

**Rationale**:
- Tenacity provides declarative retry logic with multiple backoff strategies
- Graceful degradation for external service failures
- Comprehensive error logging for debugging

**Key Technical Findings**:
- **Retry Configuration**:
  - Cohere API calls: Max 3 retries with exponential backoff (2s, 4s, 8s)
  - Qdrant operations: Max 3 retries with exponential backoff (1s, 2s, 4s)
  - HTTP fetches (sitemap/pages): Max 2 retries with 5s timeout

- **Error Categories**:
  1. **Transient errors** (retry):
     - Network timeouts
     - Rate limit errors (429)
     - Service unavailable (503)

  2. **Permanent errors** (fail fast):
     - Authentication failures (401/403)
     - Invalid input (400/422)
     - Not found (404)

  3. **Partial failures** (log and continue):
     - Single page extraction failures during ingestion
     - Individual chunk embedding failures

**Implementation Approach**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests.exceptions

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.Timeout,
                                   requests.exceptions.ConnectionError))
)
def call_cohere_api(...):
    ...

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(QdrantException)
)
def query_qdrant(...):
    ...
```

**Alternatives Considered**:
- Manual retry loops: Rejected due to code duplication and maintainability
- No retries: Rejected as inappropriate for production system with external dependencies

---

### 6. Logging & Observability Strategy

**Decision**: Structured logging with Python's logging module and JSON formatter

**Rationale**:
- Standard library solution (no additional dependencies)
- JSON format enables easy parsing and integration with log aggregators
- Structured logs facilitate debugging and monitoring

**Key Technical Findings**:
- **Log Levels**:
  - DEBUG: Request/response payloads (sanitized), intermediate processing steps
  - INFO: API calls, ingestion progress, query metrics
  - WARNING: Retry attempts, degraded performance
  - ERROR: Failures requiring investigation
  - CRITICAL: Service-level failures

- **Required Log Fields**:
  ```python
  {
      "timestamp": ISO-8601,
      "level": str,
      "service": "rag-chatbot",
      "event": str,
      "request_id": uuid,
      "user_ip": str (hashed for privacy),
      "duration_ms": int,
      "error": str (if applicable),
      "context": {...}
  }
  ```

**Implementation Approach**:
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": "rag-chatbot",
            "event": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        if record.exc_info:
            log_data["error"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

logger = logging.getLogger("rag_chatbot")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Alternatives Considered**:
- Third-party logging libraries (structlog, loguru): Rejected to minimize dependencies
- Plain text logs: Rejected due to parsing difficulty

---

### 7. Testing Strategy

**Decision**: Three-tier testing approach with pytest

**Rationale**:
- Pytest is the Python standard for testing
- Clear separation of concerns (unit, integration, contract)
- Mocking external services prevents test flakiness

**Key Technical Findings**:
- **Unit Tests** (fast, isolated):
  - Chunking algorithm correctness
  - Payload construction logic
  - Response formatting
  - Error handling branches

- **Integration Tests** (moderate speed, external services mocked):
  - End-to-end query flow with mocked Cohere/Qdrant
  - Ingestion pipeline with sample HTML
  - API endpoint behavior with test client

- **Contract Tests** (slow, real external services):
  - Cohere API integration (rate-limited)
  - Qdrant Cloud connectivity
  - Sitemap accessibility

**Implementation Approach**:
```python
# Unit test example
def test_chunk_text_respects_boundaries():
    text = "Header 1\n\nParagraph 1. Paragraph 2.\n\nHeader 2\n\nParagraph 3."
    chunks = chunk_text(text, target_size=50, overlap=10)
    assert all(len(chunk) <= 60 for chunk in chunks)  # target + overlap
    assert any("Header 1" in chunk for chunk in chunks)

# Integration test with mocking
@pytest.fixture
def mock_cohere(monkeypatch):
    mock_client = Mock()
    mock_client.embed.return_value = Mock(embeddings=[[0.1] * 1024])
    monkeypatch.setattr("app.services.cohere_client", mock_client)
    return mock_client

def test_query_endpoint(client, mock_cohere, mock_qdrant):
    response = client.post("/api/v1/query", json={"query": "test"})
    assert response.status_code == 200
    assert "answer" in response.json()
```

**Alternatives Considered**:
- No testing: Rejected as inappropriate for production system
- Only end-to-end tests: Rejected due to slowness and flakiness

---

## Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Language | Python | 3.11+ | Required by specification, modern async support |
| Web Framework | FastAPI | 0.104+ | Async support, auto-documentation, validation |
| Embeddings | Cohere embed-english-v3.0 | v3.0 | 1024-dim, optimized for semantic search |
| Generation | Cohere command-r | Latest | RAG-optimized with citation support |
| Vector DB | Qdrant Cloud | Latest | Managed service, HNSW indexing |
| HTTP Client | requests | 2.31+ | Standard library for sitemap/page fetching |
| HTML Parser | BeautifulSoup4 | 4.12+ | Robust Docusaurus content extraction |
| Sitemap Parser | xml.etree.ElementTree | Stdlib | Built-in XML parsing |
| Rate Limiting | SlowAPI | 0.1.9+ | FastAPI-native rate limiting |
| Retry Logic | tenacity | 8.2+ | Declarative retry with exponential backoff |
| Testing | pytest | 7.4+ | Industry-standard Python testing |
| Environment | python-dotenv | 1.0+ | .env file loading |

---

## Deployment Considerations

**Platform**: To be determined during implementation (requirements specify Python 3.11+ support needed)

**Recommended Options**:
1. **Railway/Render**: Simple deployment, automatic HTTPS, good free tier
2. **AWS Lambda + API Gateway**: Serverless, scales to zero, may need cold start optimization
3. **Google Cloud Run**: Containerized, scales to zero, good Python support
4. **Self-hosted VPS**: Full control, requires manual setup and maintenance

**Decision Deferred**: Deployment platform will be chosen during implementation phase based on:
- Cost constraints
- Expected traffic patterns
- Operational complexity preferences
- Integration requirements with Vercel frontend

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cohere rate limits exceeded | Medium | High | Implement retry with backoff, monitor usage, add request queuing if needed |
| Qdrant Cloud connectivity issues | Low | High | Retry logic, circuit breaker pattern, health checks |
| Sitemap parsing failures | Low | Medium | Robust error handling, manual URL fallback |
| Poor chunk quality affecting retrieval | Medium | High | Iterative testing with sample queries, adjustable chunk parameters |
| Frontend CORS issues | Low | Low | Early integration testing, proper CORS configuration |
| Slow ingestion (>10min for 500 pages) | Medium | Medium | Batch processing, parallel requests (respect rate limits) |

---

## Next Steps

This research document resolves all technical unknowns. Proceed to Phase 1:
1. Create data model specification (data-model.md)
2. Define API contracts (contracts/)
3. Write quickstart guide (quickstart.md)
4. Update agent context with selected technologies
