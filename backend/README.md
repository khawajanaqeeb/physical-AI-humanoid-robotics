# Gemini RAG Chatbot Backend

Backend API for a Retrieval-Augmented Generation (RAG) chatbot powered by Google Gemini AI.

## Overview

This backend implements a complete RAG pipeline using:
- **Google Gemini embedding-001** (768 dimensions) for semantic search
- **Google Gemini Pro** for response generation
- **Qdrant Cloud** for vector storage
- **Neon Postgres** for metadata storage
- **FastAPI** for the REST API

## Features

- Context-grounded responses to prevent hallucination
- Hierarchical content chunking with overlap
- Dual storage (Qdrant for vectors, Postgres for metadata)
- Rate limiting with slowapi
- Batch processing with exponential backoff
- Comprehensive error handling and logging
- Health check endpoints

## Prerequisites

- Python 3.11+
- Google Cloud account with Gemini API access
- Qdrant Cloud account
- Neon Postgres database
- Git

## Installation

### 1. Clone the repository

```bash
cd backend
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the backend directory:

```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=gemini_embeddings

# Neon Postgres
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# API Configuration
API_PORT=8000
LOG_LEVEL=INFO
JSON_LOGS=false
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

## Database Setup

### 1. Run migrations

```bash
# Ensure your DATABASE_URL is set in .env
python scripts/run_migrations.py
```

This will create the `chunks` table for storing metadata.

### 2. Initialize Qdrant collection

```bash
python scripts/init_gemini_qdrant.py
```

This creates the Qdrant collection with 768-dimensional vectors for Gemini embeddings.

**Expected output:**
```
🚀 Initializing Qdrant for Gemini embeddings...
============================================================

✅ Qdrant collection initialized successfully!

Configuration:
  Collection name: gemini_embeddings
  Vector dimensions: 768 (Gemini embedding-001)
  Distance metric: COSINE
  Current points: 0
  Payload indexes: file_path, chapter
============================================================
```

## Content Ingestion

### Prepare your Docusaurus content

Your markdown files should be in a Docusaurus-compatible structure:

```
docs/
├── chapter-01/
│   ├── intro.md
│   └── section-1.md
├── chapter-02/
│   └── intro.md
└── ...
```

### Ingest content

```bash
# Ingest entire directory
python scripts/ingest_book.py \
  --docs-path /path/to/docs \
  --base-url https://book.example.com

# Ingest single file
python scripts/ingest_book.py \
  --docs-path /path/to/docs \
  --file docs/chapter-01/intro.md

# Force re-index (delete and re-create all chunks)
python scripts/ingest_book.py \
  --docs-path /path/to/docs \
  --force
```

**Expected output:**
```
🚀 Starting book ingestion for Gemini RAG...
============================================================

✅ Ingestion completed!

Statistics:
  Files processed: 42
  Files skipped: 0
  Total chunks: 387
  Errors: 0
============================================================
```

## Running the Server

### Development mode

```bash
python -m uvicorn src.main:app --reload --port 8000
```

Or:

```bash
python src/main.py
```

### Production mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Root

```bash
GET /
```

Returns API information and available endpoints.

### Health Check

```bash
GET /health
```

Returns health status of all services (Qdrant, Postgres, Gemini API).

### Query (Gemini RAG)

```bash
POST /api/v1/query
Content-Type: application/json

{
  "question": "What is the difference between forward and inverse kinematics?",
  "session_id": "optional-uuid-here",
  "max_results": 3
}
```

**Response:**

```json
{
  "answer": "Forward kinematics calculates the position...",
  "sources": [
    {
      "chapter": "Chapter 3: Kinematics",
      "section": "3.1 Forward Kinematics",
      "source_url": "https://book.example.com/chapter-03/forward-kinematics",
      "relevance_score": 0.89
    }
  ],
  "confidence": 0.85,
  "response_time_ms": 1243
}
```

## Testing

### Manual testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is a robot?",
    "max_results": 3
  }'
```

### Testing with Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query",
    json={
        "question": "What is inverse kinematics?",
        "max_results": 5
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])}")
print(f"Confidence: {result['confidence']}")
```

### Run automated tests

```bash
pytest tests/ -v
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── gemini_query.py    # Main query endpoint
│   │   │   ├── health.py          # Health check
│   │   │   └── query.py           # Legacy endpoint
│   │   └── gemini_schemas.py      # Pydantic models
│   ├── clients/
│   │   ├── qdrant_client.py       # Qdrant operations
│   │   └── openai_client.py       # Legacy (unused)
│   ├── config/
│   │   ├── settings.py            # Environment config
│   │   └── logging.py             # Structured logging
│   ├── services/
│   │   ├── embedding.py           # Gemini embeddings
│   │   ├── chunking.py            # Content chunking
│   │   ├── retrieval.py           # Vector search
│   │   ├── generation.py          # Response generation
│   │   └── gemini_rag_service.py  # RAG orchestration
│   ├── database.py                # Postgres connection
│   └── main.py                    # FastAPI app
├── scripts/
│   ├── init_gemini_qdrant.py      # Qdrant setup
│   ├── ingest_book.py             # Content ingestion
│   └── run_migrations.py          # Database migrations
├── migrations/
│   └── 004_create_chunks_table.sql
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Architecture

### RAG Pipeline

1. **Query Reception**: User submits question via POST /api/v1/query
2. **Query Embedding**: Question is embedded using Gemini embedding-001 (768-dim)
3. **Vector Search**: Qdrant retrieves top-k similar chunks using cosine similarity
4. **Context Assembly**: Retrieved chunks are formatted with metadata
5. **Response Generation**: Gemini Pro generates answer using retrieved context
6. **Citation Extraction**: Sources are extracted and ranked
7. **Response Return**: Answer with sources and confidence score returned to user

### Data Flow

```
User Question
    ↓
[Embedding Service] → Gemini embedding-001 (768-dim vector)
    ↓
[Retrieval Service] → Qdrant search (top-k chunks)
    ↓
[Postgres] ← Metadata lookup
    ↓
[Generation Service] → Gemini Pro (context + question)
    ↓
Response with Sources
```

## Configuration

### Chunking Parameters

- **Chunk size**: 400-800 words
- **Overlap**: 100 words
- **Strategy**: Hierarchical (preserves headings)

### Embedding Parameters

- **Model**: `models/embedding-001`
- **Dimensions**: 768
- **Task type**: `retrieval_document` (indexing), `retrieval_query` (search)
- **Batch size**: 10 (configurable)
- **Delay between batches**: 1.0s

### Retrieval Parameters

- **Top-k**: 3-10 (default: 5)
- **Score threshold**: 0.7 (cosine similarity)
- **Distance metric**: COSINE

### Generation Parameters

- **Model**: `gemini-pro`
- **Temperature**: 0.7
- **Max output tokens**: 2048
- **Context grounding**: Strict (uses only provided chunks)

## Rate Limiting

Default rate limits:
- **Global**: 100 requests/minute
- **Per endpoint**: Configurable via `@limiter.limit()` decorator

Configure in `.env`:
```env
RATE_LIMIT_PER_MINUTE=100
```

## Logging

Structured logging with `structlog`:

```python
logger.info("query_processed",
    session_id=session_id,
    response_time_ms=1243,
    confidence=0.85,
    sources_count=3
)
```

Set log level in `.env`:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
JSON_LOGS=true  # true for production, false for development
```

## Troubleshooting

### Qdrant connection errors

```
Error: Could not connect to Qdrant
```

**Solution:**
- Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Check Qdrant Cloud cluster is running
- Test connection: `python -c "from clients.qdrant_client import check_qdrant_connection; import asyncio; print(asyncio.run(check_qdrant_connection()))"`

### Database connection errors

```
Error: Could not connect to database
```

**Solution:**
- Verify `DATABASE_URL` format: `postgresql+asyncpg://user:password@host/database`
- Ensure Neon database is accessible
- Run migrations: `python scripts/run_migrations.py`

### Gemini API errors

```
Error: 429 Resource exhausted
```

**Solution:**
- Check API quota in Google Cloud Console
- Reduce batch size in embedding service
- Increase delay between batches

### Empty search results

```
No relevant chunks found for query
```

**Solution:**
- Verify content has been ingested: Check Qdrant collection point count
- Lower `score_threshold` (default: 0.7)
- Increase `top_k` parameter
- Re-ingest content with `--force` flag

### File ingestion fails

```
Error: File ingestion failed
```

**Solution:**
- Check file encoding is UTF-8
- Verify file path matches `docs/**/*.md` pattern
- Check frontmatter syntax (YAML between `---` markers)
- Review logs for specific error details

## Performance Optimization

### Batch processing

Adjust batch size for embedding generation:

```python
# In services/embedding.py
embeddings = await embed_batch(
    texts=chunk_texts,
    batch_size=20,  # Increase for faster processing
    delay_between_batches=0.5  # Reduce delay
)
```

### Caching

Consider adding Redis for caching:
- Embedding results
- Search results for common queries
- Generated responses

### Database indexing

Ensure indexes are created:

```sql
CREATE INDEX idx_chunks_file_path ON chunks(file_path);
CREATE INDEX idx_chunks_qdrant_point_id ON chunks(qdrant_point_id);
CREATE INDEX idx_chunks_chapter ON chunks(chapter);
```

## Migration from OpenAI

If migrating from an OpenAI-based RAG system:

1. **Update dependencies**: Remove `openai`, add `google-generativeai`
2. **Re-create Qdrant collection**: 768-dim instead of 3072-dim
3. **Re-ingest content**: New embeddings required
4. **Update API clients**: Replace OpenAI API calls with Gemini
5. **Test thoroughly**: Different models may produce different results

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [Repository URL]
- Documentation: [Docs URL]
- Email: [Support Email]
