# Data Model: Phase 2 RAG Chatbot System

**Feature**: 001-rag-chatbot-mcp
**Date**: 2025-12-10
**Phase**: 1 - Data Model Design

## Overview

This document defines all entities, schemas, and relationships for the RAG chatbot system across vector storage (Qdrant), relational database (Neon Postgres), and API request/response models.

---

## 1. Vector Database Entities (Qdrant)

### TextbookChunk

**Purpose**: Represents a semantically meaningful chunk of textbook content with embedding and metadata.

**Storage**: Qdrant Cloud collection `textbook_chunks`

**Schema**:

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TextbookChunkMetadata(BaseModel):
    """Metadata stored as Qdrant payload"""
    chunk_id: str  # Format: {file_path}:{chunk_index}
    file_path: str  # e.g., "docs/chapter-01/intro.md"
    document_title: str  # e.g., "Introduction to Robotics"
    heading_hierarchy: List[str]  # e.g., ["Chapter 1", "Section 1.2", "Kinematics"]
    section_anchor: str  # Docusaurus heading ID, e.g., "forward-kinematics"
    chunk_index: int  # 0-indexed position in document
    overlap_tokens: int  # Number of overlapping tokens (100-160)
    content_text: str  # Raw chunk text (500-800 tokens)
    created_at: datetime
    updated_at: datetime

class TextbookChunkPoint(BaseModel):
    """Complete Qdrant point structure"""
    id: str  # chunk_id
    vector: List[float]  # 3072 dimensions (text-embedding-3-large)
    payload: TextbookChunkMetadata
```

**Qdrant Collection Config**:

```python
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

collection_config = {
    "vectors": VectorParams(
        size=3072,
        distance=Distance.COSINE
    ),
    "payload_schema": {
        "file_path": PayloadSchemaType.KEYWORD,
        "document_title": PayloadSchemaType.TEXT,
        "section_anchor": PayloadSchemaType.KEYWORD,
        "chunk_index": PayloadSchemaType.INTEGER
    }
}
```

**Indexes**:
- file_path (for page-scoped filtering)
- section_anchor (for citation resolution)

**Constraints**:
- chunk_id must be unique
- vector dimensions must be 3072
- overlap_tokens must be 100-160
- content_text must be 500-800 tokens

**State Transitions**:
- Created: On initial document ingestion
- Updated: When source document content changes
- Deleted: When source document is removed

---

## 2. Relational Database Entities (Neon Postgres)

### Query

**Purpose**: Stores user queries with retrieval results and generated answers for analytics.

**Table**: `queries`

**Schema**:

```sql
CREATE TABLE queries (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    user_session_id UUID NOT NULL,
    selected_text TEXT,  -- NULL if no text selection
    retrieved_chunk_ids TEXT[] NOT NULL,  -- Array of chunk IDs
    answer_text TEXT NOT NULL,
    citations JSONB NOT NULL,  -- Array of {title, anchor, url}
    similarity_scores FLOAT[] NOT NULL,  -- Parallel to retrieved_chunk_ids
    retrieval_time_ms INT NOT NULL,
    answer_time_ms INT NOT NULL,
    citation_time_ms INT NOT NULL,
    total_time_ms INT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_arrays CHECK (
        array_length(retrieved_chunk_ids, 1) = array_length(similarity_scores, 1)
    ),
    CONSTRAINT valid_times CHECK (
        total_time_ms >= retrieval_time_ms + answer_time_ms + citation_time_ms
    )
);

-- Indexes
CREATE INDEX idx_queries_session ON queries(user_session_id);
CREATE INDEX idx_queries_timestamp ON queries(timestamp);
CREATE INDEX idx_queries_total_time ON queries(total_time_ms);
```

**Python Model**:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class Citation(BaseModel):
    title: str  # Document title
    anchor: str  # Heading anchor ID
    url: str  # Full URL with hash

class Query(BaseModel):
    query_id: UUID = Field(default_factory=uuid4)
    query_text: str = Field(..., min_length=1, max_length=5000)
    user_session_id: UUID
    selected_text: Optional[str] = None
    retrieved_chunk_ids: List[str] = Field(..., min_items=0, max_items=10)
    answer_text: str
    citations: List[Citation] = Field(..., min_items=0)
    similarity_scores: List[float] = Field(..., min_items=0, max_items=10)
    retrieval_time_ms: int = Field(..., ge=0)
    answer_time_ms: int = Field(..., ge=0)
    citation_time_ms: int = Field(..., ge=0)
    total_time_ms: int = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints**:
- query_text must not be empty
- retrieved_chunk_ids and similarity_scores must have matching lengths
- All time measurements must be non-negative
- timestamps must be in UTC

**State Transitions**:
- Created: When query is processed successfully
- Immutable: No updates (append-only for analytics)

---

### Feedback

**Purpose**: Captures user thumbs-up/thumbs-down feedback on answers.

**Table**: `feedback`

**Schema**:

```sql
CREATE TABLE feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES queries(query_id) ON DELETE CASCADE,
    feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('positive', 'negative')),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_feedback_query ON feedback(query_id);
CREATE INDEX idx_feedback_type ON feedback(feedback_type);
CREATE INDEX idx_feedback_timestamp ON feedback(timestamp);
```

**Python Model**:

```python
from enum import Enum

class FeedbackType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"

class Feedback(BaseModel):
    feedback_id: UUID = Field(default_factory=uuid4)
    query_id: UUID
    feedback_type: FeedbackType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints**:
- query_id must reference existing query
- feedback_type must be 'positive' or 'negative'
- One feedback per query (enforced at application layer)

**State Transitions**:
- Created: When user clicks thumbs-up/down
- Immutable: No updates or deletes

---

### SyncJob

**Purpose**: Tracks content synchronization runs for monitoring and debugging.

**Table**: `sync_jobs`

**Schema**:

```sql
CREATE TABLE sync_jobs (
    sync_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    files_processed INT NOT NULL DEFAULT 0,
    files_failed INT NOT NULL DEFAULT 0,
    error_log JSONB,  -- Array of {file_path, error_message}

    CONSTRAINT valid_status CHECK (
        (status = 'running' AND end_time IS NULL) OR
        (status IN ('completed', 'failed') AND end_time IS NOT NULL)
    ),
    CONSTRAINT valid_counts CHECK (
        files_processed >= 0 AND files_failed >= 0
    )
);

-- Indexes
CREATE INDEX idx_sync_jobs_status ON sync_jobs(status);
CREATE INDEX idx_sync_jobs_start_time ON sync_jobs(start_time DESC);
```

**Python Model**:

```python
class SyncStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SyncError(BaseModel):
    file_path: str
    error_message: str

class SyncJob(BaseModel):
    sync_id: UUID = Field(default_factory=uuid4)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: SyncStatus = SyncStatus.RUNNING
    files_processed: int = Field(default=0, ge=0)
    files_failed: int = Field(default=0, ge=0)
    error_log: List[SyncError] = Field(default_factory=list)
```

**Constraints**:
- status = 'running' implies end_time is NULL
- status in ('completed', 'failed') requires end_time
- files_processed and files_failed must be non-negative

**State Transitions**:
- Created: When sync starts (status='running')
- Updated: When sync completes or fails
- Immutable after completion: Historical record

---

## 3. API Request/Response Models

### Query Request

**Endpoint**: `POST /api/query`

**Purpose**: Submit user question with optional text selection context.

**Schema**:

```python
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    session_id: str = Field(..., regex=r'^[0-9a-f-]{36}$')  # UUID format
    selected_text: Optional[str] = Field(None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is forward kinematics?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "selected_text": "The robot arm consists of..."
            }
        }
```

**Validation Rules**:
- query: 1-5000 characters
- session_id: Valid UUID v4
- selected_text: Optional, max 2000 characters

---

### Query Response

**Endpoint**: `POST /api/query` (response)

**Purpose**: Return answer with citations and metadata.

**Schema**:

```python
class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    sources: List[str]  # Unique document titles
    retrieval_time_ms: int
    answer_time_ms: int
    citation_time_ms: int
    total_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Forward kinematics calculates the position...",
                "citations": [
                    {
                        "title": "Robotics Fundamentals",
                        "anchor": "forward-kinematics",
                        "url": "/docs/chapter-01#forward-kinematics"
                    }
                ],
                "sources": ["Robotics Fundamentals"],
                "retrieval_time_ms": 45,
                "answer_time_ms": 1200,
                "citation_time_ms": 30,
                "total_time_ms": 1275
            }
        }
```

---

### Feedback Request

**Endpoint**: `POST /api/feedback`

**Purpose**: Submit thumbs-up/down feedback for a query.

**Schema**:

```python
class FeedbackRequest(BaseModel):
    query_id: UUID
    feedback_type: FeedbackType

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "123e4567-e89b-12d3-a456-426614174000",
                "feedback_type": "positive"
            }
        }
```

---

### Sync Trigger Request

**Endpoint**: `POST /api/sync/trigger`

**Purpose**: Manually trigger content synchronization.

**Schema**:

```python
class SyncTriggerRequest(BaseModel):
    force: bool = False  # If True, re-sync all files

class SyncTriggerResponse(BaseModel):
    sync_id: UUID
    status: str
    message: str
```

---

## 4. Entity Relationships

```
┌─────────────────┐
│ TextbookChunk   │ (Qdrant)
│ - chunk_id (PK) │
│ - vector        │
│ - metadata      │
└─────────────────┘
        ↑
        │ referenced by
        │
┌─────────────────┐      ┌──────────────┐
│ Query           │ 1:N  │ Feedback     │
│ - query_id (PK) │──────│ - query_id   │
│ - chunk_ids[]   │      └──────────────┘
└─────────────────┘

┌─────────────────┐
│ SyncJob         │ (independent)
│ - sync_id (PK)  │
│ - status        │
└─────────────────┘
```

**Key Relationships**:
- Query contains array of TextbookChunk IDs (denormalized for performance)
- Feedback references Query (1:N, one query can have one feedback)
- SyncJob is independent (no foreign keys)

---

## 5. Validation Rules

### Cross-Entity Constraints

1. **Chunk ID Format**: Must match `{file_path}:{chunk_index}` pattern
2. **Session ID**: Must be consistent across all queries in a tab session
3. **Citation URLs**: Must reference existing section_anchor in Qdrant
4. **Similarity Scores**: Must be in range [0.0, 1.0], ordered descending
5. **Time Measurements**: total_time_ms ≥ sum of component times

### Data Integrity

1. **Orphan Prevention**: Delete cascade for feedback when query deleted
2. **Chunk Consistency**: Delete Qdrant points when source files removed
3. **Sync State**: No two sync jobs with status='running' simultaneously
4. **Feedback Uniqueness**: One feedback per query (application-enforced)

---

## 6. Migration Strategy

### Initial Schema Creation

```sql
-- Run on Neon Postgres
\i migrations/001_create_queries_table.sql
\i migrations/002_create_feedback_table.sql
\i migrations/003_create_sync_jobs_table.sql
```

### Qdrant Collection Creation

```python
from qdrant_client import AsyncQdrantClient

async def create_collection():
    client = AsyncQdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    await client.create_collection(
        collection_name="textbook_chunks",
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
    )

    # Create payload indexes
    await client.create_payload_index(
        collection_name="textbook_chunks",
        field_name="file_path",
        field_schema="keyword"
    )
```

### Rollback Plan

- Qdrant: Delete collection and recreate
- Neon: Use transaction-wrapped migrations with rollback scripts

---

## 7. Performance Considerations

### Qdrant Optimizations

- Use batch upsert (100 points per request)
- Enable HNSW indexing for <100ms search
- Set payload index on frequently filtered fields

### Postgres Optimizations

- Use JSONB for flexible citation storage
- Index on query timestamp for analytics queries
- Partition queries table by month (if >10M rows)

### API Model Optimizations

- Use Pydantic v2 for fast validation
- Lazy-load citation metadata (only when needed)
- Cache frequently accessed documents

---

## Summary

All entities defined with complete schemas, constraints, and relationships. Data model supports:
- Efficient vector search (Qdrant)
- Analytics and monitoring (Neon)
- Type-safe API contracts (Pydantic)
- Data integrity (constraints and validation)

**Next Steps**:
1. Generate API contracts (OpenAPI spec)
2. Create database migration scripts
3. Update agent context with data model
