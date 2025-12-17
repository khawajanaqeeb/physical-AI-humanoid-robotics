# Data Model Specification
**Feature**: RAG Chatbot Integration for Deployed Docusaurus Textbook (Cohere + Qdrant)
**Date**: 2025-12-16
**Status**: Phase 1 Output

## Overview

This document defines the domain entities and their relationships for the RAG chatbot system. All entities are derived from the Key Entities section of [spec.md](./spec.md).

## Domain Entities

### DocumentChunk

Represents a semantically coherent segment of textbook content with its embedding and metadata.

**Purpose**: Core unit of retrieval in the RAG system. Each chunk contains a portion of textbook content that can be independently embedded, stored, and retrieved.

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `chunk_id` | str | Yes | UUID hex format, unique | Unique identifier for the chunk |
| `content_text` | str | Yes | 500-1000 characters | Full text content of the chunk |
| `embedding_vector` | List[float] | Yes | Exactly 1024 dimensions | Cohere embed-english-v3.0 embedding |
| `page_url` | str | Yes | Valid URL | Source page URL from textbook |
| `page_title` | str | Yes | Non-empty string | Human-readable page title |
| `section_heading` | str | No | Nullable | Heading/section context for chunk |
| `chunk_index` | int | Yes | >= 0 | Sequential position within page |
| `character_count` | int | Yes | > 0 | Length of content_text |
| `ingestion_timestamp` | str | Yes | ISO 8601 format | When chunk was created/updated |

**Validation Rules**:
- `character_count` must equal `len(content_text)`
- `embedding_vector` must have exactly 1024 elements
- `chunk_index` must be unique within a page_url
- `page_url` must be from textbook domain (https://physical-ai-humanoid-robotics-e3c7.vercel.app/)

**Storage**:
- Stored in Qdrant Cloud as a Point with:
  - `id`: chunk_id
  - `vector`: embedding_vector
  - `payload`: All other fields as metadata

**Example**:
```python
{
    "chunk_id": "a1b2c3d4e5f6",
    "content_text": "Humanoid robotics combines mechanical engineering with artificial intelligence to create robots that mimic human form and behavior. These systems require sophisticated control algorithms...",
    "embedding_vector": [0.123, -0.456, 0.789, ...],  # 1024 floats
    "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/intro",
    "page_title": "Introduction to Humanoid Robotics",
    "section_heading": "Overview",
    "chunk_index": 0,
    "character_count": 157,
    "ingestion_timestamp": "2025-12-16T10:30:00Z"
}
```

---

### QuerySession

Represents a complete user interaction from query to response, including retrieval and generation.

**Purpose**: Track query processing for observability, debugging, and performance monitoring.

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `session_id` | str | Yes | UUID format | Unique identifier for query session |
| `query_text` | str | Yes | Non-empty, max 2000 chars | User's original question |
| `embedding_vector` | List[float] | Yes | Exactly 1024 dimensions | Embedded query for retrieval |
| `retrieved_chunks` | List[DocumentChunk] | Yes | Length = top-K (default 5) | Chunks retrieved from Qdrant |
| `generated_response` | str | Yes | Non-empty | Cohere-generated answer |
| `source_citations` | List[SourceCitation] | Yes | At least 1 citation | Sources used in response |
| `timestamp` | str | Yes | ISO 8601 format | When query was received |
| `response_time_ms` | int | Yes | > 0 | Total processing time |
| `retrieval_score_threshold` | float | Yes | 0.0 - 1.0 | Min similarity score used |
| `error` | str | No | Nullable | Error message if query failed |

**Validation Rules**:
- `query_text` length must be <= 2000 characters
- `retrieved_chunks` length must match configured top-K value
- `source_citations` must reference chunks from `retrieved_chunks`
- `response_time_ms` should be < 3000ms for 95% of queries (SLA)
- If `error` is present, `generated_response` may be empty

**Lifecycle**:
1. Create session with query_text and timestamp
2. Generate embedding_vector via Cohere
3. Retrieve chunks from Qdrant (populate retrieved_chunks)
4. Generate response via Cohere RAG (populate generated_response, source_citations)
5. Calculate response_time_ms
6. Log session for monitoring

**Example**:
```python
{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query_text": "What are the main components of a humanoid robot?",
    "embedding_vector": [0.234, -0.567, 0.890, ...],  # 1024 floats
    "retrieved_chunks": [
        # List of DocumentChunk objects
    ],
    "generated_response": "Based on the textbook, the main components of a humanoid robot include...",
    "source_citations": [
        {
            "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/components",
            "page_title": "Robot Components",
            "chunk_text": "The primary components include actuators, sensors, control systems...",
            "relevance_score": 0.89
        }
    ],
    "timestamp": "2025-12-16T15:45:30Z",
    "response_time_ms": 1850,
    "retrieval_score_threshold": 0.7,
    "error": null
}
```

---

### IngestionJob

Represents a content synchronization operation that crawls the textbook and updates the vector database.

**Purpose**: Track ingestion runs for monitoring, debugging, and incremental updates.

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `job_id` | str | Yes | UUID format | Unique identifier for ingestion job |
| `start_time` | str | Yes | ISO 8601 format | When job started |
| `end_time` | str | No | ISO 8601 format, nullable | When job completed/failed |
| `pages_processed` | int | Yes | >= 0 | Count of pages successfully processed |
| `chunks_created` | int | Yes | >= 0 | Count of new chunks added to Qdrant |
| `chunks_updated` | int | Yes | >= 0 | Count of existing chunks updated |
| `errors_encountered` | List[ErrorRecord] | Yes | Can be empty list | Errors during processing |
| `status` | Enum | Yes | See below | Current job status |

**Status Enum**:
- `pending`: Job created but not started
- `running`: Job currently processing
- `completed`: Job finished successfully
- `failed`: Job terminated due to errors

**Validation Rules**:
- `end_time` must be after `start_time` (if present)
- `status` must be `completed` or `failed` when `end_time` is set
- Total chunks (`chunks_created` + `chunks_updated`) should correlate with `pages_processed`
- Ingestion should complete within 10 minutes for 500 pages (performance SLA)

**State Transitions**:
```
pending → running → completed
                 → failed
```

**Example**:
```python
{
    "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "start_time": "2025-12-16T08:00:00Z",
    "end_time": "2025-12-16T08:07:30Z",
    "pages_processed": 150,
    "chunks_created": 1250,
    "chunks_updated": 0,
    "errors_encountered": [
        {
            "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/broken-page",
            "error_type": "HTTPError",
            "error_message": "404 Not Found",
            "timestamp": "2025-12-16T08:02:15Z"
        }
    ],
    "status": "completed"
}
```

---

### SourceCitation

Represents a source reference in a generated response, linking the answer to textbook content.

**Purpose**: Provide transparency and verification for generated answers.

**Attributes**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `page_url` | str | Yes | Valid URL | Link to source textbook page |
| `page_title` | str | Yes | Non-empty string | Human-readable page title |
| `chunk_text` | str | Yes | Non-empty, max 300 chars | Excerpt from retrieved chunk |
| `relevance_score` | float | Yes | 0.0 - 1.0 | Qdrant similarity score |

**Validation Rules**:
- `chunk_text` should be truncated with "..." if exceeds 300 characters
- `relevance_score` must be >= `retrieval_score_threshold` from QuerySession
- `page_url` must correspond to a chunk in `retrieved_chunks`

**Display Format**:
- Frontend should render citations as clickable links
- Show page_title as link text
- Display relevance_score as percentage for user transparency
- Show chunk_text as preview on hover/expand

**Example**:
```python
{
    "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/sensors",
    "page_title": "Sensor Systems in Humanoid Robots",
    "chunk_text": "Force-torque sensors measure the forces and torques at robot joints, enabling compliant motion control. These sensors are critical for safe human-robot interaction...",
    "relevance_score": 0.85
}
```

---

### ErrorRecord

Sub-entity for tracking errors during ingestion jobs.

**Purpose**: Detailed error tracking for debugging and quality assurance.

**Attributes**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `page_url` | str | Yes | URL where error occurred |
| `error_type` | str | Yes | Exception class name or HTTP error code |
| `error_message` | str | Yes | Detailed error description |
| `timestamp` | str | Yes | ISO 8601 format, when error occurred |

**Common Error Types**:
- `HTTPError`: Failed to fetch page (4xx, 5xx)
- `ParseError`: Failed to extract content from HTML
- `EmbeddingError`: Cohere API failure during embedding generation
- `QdrantError`: Vector database operation failure
- `ValidationError`: Chunk validation failed

**Example**:
```python
{
    "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/malformed",
    "error_type": "ParseError",
    "error_message": "Unable to extract main content from HTML: No <article> or <main> tag found",
    "timestamp": "2025-12-16T08:03:45Z"
}
```

---

## Entity Relationships

```
QuerySession
├─ retrieved_chunks: List[DocumentChunk]
└─ source_citations: List[SourceCitation]
       └─ References DocumentChunk via page_url

IngestionJob
└─ errors_encountered: List[ErrorRecord]

DocumentChunk (stored in Qdrant)
└─ Retrieved by QuerySession
└─ Created/Updated by IngestionJob
```

**Cardinalities**:
- 1 QuerySession → 5 DocumentChunks (default top-K)
- 1 QuerySession → 1-5 SourceCitations (subset of retrieved chunks)
- 1 IngestionJob → 0-N ErrorRecords
- 1 IngestionJob → 0-N DocumentChunks (created/updated)

---

## Implementation Notes

### Python Type Hints

Use Python dataclasses or Pydantic models for type safety:

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class DocumentChunk:
    chunk_id: str
    content_text: str
    embedding_vector: List[float]
    page_url: str
    page_title: str
    section_heading: Optional[str]
    chunk_index: int
    character_count: int
    ingestion_timestamp: str

    def __post_init__(self):
        assert len(self.embedding_vector) == 1024
        assert self.character_count == len(self.content_text)
```

### Qdrant Payload Mapping

```python
def chunk_to_qdrant_point(chunk: DocumentChunk) -> PointStruct:
    return PointStruct(
        id=chunk.chunk_id,
        vector=chunk.embedding_vector,
        payload={
            "content_text": chunk.content_text,
            "page_url": chunk.page_url,
            "page_title": chunk.page_title,
            "section_heading": chunk.section_heading,
            "chunk_index": chunk.chunk_index,
            "character_count": chunk.character_count,
            "ingestion_timestamp": chunk.ingestion_timestamp
        }
    )
```

### Logging Integration

All entity operations should be logged with structured logging:

```python
logger.info(
    "Query session completed",
    extra={
        "session_id": session.session_id,
        "response_time_ms": session.response_time_ms,
        "retrieval_score_threshold": session.retrieval_score_threshold,
        "chunks_retrieved": len(session.retrieved_chunks)
    }
)
```

---

## Data Flow

### Ingestion Flow
```
1. Create IngestionJob (status=pending)
2. Update status to running
3. For each page in sitemap:
   a. Fetch and parse HTML
   b. Chunk content → List[DocumentChunk]
   c. Generate embeddings via Cohere
   d. Upsert to Qdrant
   e. Increment pages_processed, chunks_created
   f. On error: append to errors_encountered
4. Update end_time and status (completed/failed)
5. Log IngestionJob summary
```

### Query Flow
```
1. Create QuerySession with query_text, timestamp
2. Generate embedding_vector via Cohere
3. Search Qdrant → List[DocumentChunk]
4. Populate retrieved_chunks
5. Generate response via Cohere RAG
6. Extract SourceCitations from Cohere's citation metadata
7. Populate generated_response, source_citations
8. Calculate response_time_ms
9. Log QuerySession
10. Return response to API client
```

---

## Validation Checklist

Before implementation:
- [ ] All entities have complete attribute definitions
- [ ] All constraints are clear and testable
- [ ] Relationships between entities are explicit
- [ ] Example data is realistic and valid
- [ ] Validation rules cover edge cases
- [ ] Qdrant mapping strategy is defined
- [ ] Logging integration points identified
- [ ] Data flows match spec.md functional requirements
