# Data Model: Gemini RAG Chatbot

**Feature**: 002-gemini-rag-chatbot
**Date**: 2025-12-14
**Purpose**: Define entities, relationships, and validation rules for RAG chatbot system

---

## Entity Overview

The system manages five core entities across two data stores:

**Qdrant (Vector Storage)**:
- ContentChunk vectors (768-dim embeddings)

**Neon Postgres (Metadata & Logging)**:
- ContentChunk metadata
- Query logs (optional monitoring)

**Application Memory**:
- ConversationSession (stateless or short-lived)
- Query (request object)
- Response (result object)

---

## 1. ContentChunk

**Purpose**: Represents a segmented portion of book content optimized for semantic retrieval.

**Storage**:
- Vector: Qdrant (embedding + payload)
- Metadata: Postgres (`chunks` table)

### Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `id` | UUID | Yes | Unique identifier for chunk | Generated on creation |
| `chunk_text` | String | Yes | Actual text content (512-1024 tokens) | Min length: 50 chars, Max length: 8000 chars |
| `embedding_vector` | Float[768] | Yes | Gemini embedding representation | Exactly 768 dimensions, normalized |
| `file_path` | String | Yes | Source file path in Docusaurus | Must match pattern `docs/**/*.md` or `docs/**/*.mdx` |
| `chapter` | String | No | Chapter title (extracted from frontmatter) | Max length: 256 chars |
| `section` | String | No | Section heading within chapter | Max length: 256 chars |
| `heading_path` | String[] | No | Hierarchical heading path | Max 5 levels deep |
| `source_url` | String | Yes | Public URL to deployed book page | Valid HTTPS URL |
| `chunk_index` | Integer | Yes | Position within parent document | Zero-indexed, >= 0 |
| `total_chunks` | Integer | Yes | Total chunks for parent document | Must be > chunk_index |
| `qdrant_point_id` | UUID | Yes | Reference to Qdrant vector point | Matches Qdrant point ID |
| `created_at` | Timestamp | Yes | Chunk creation time | Auto-generated |
| `updated_at` | Timestamp | Yes | Last modification time | Auto-updated on change |

### Relationships

- **Parent**: Docusaurus Markdown file (one file → many chunks)
- **Qdrant Point**: One-to-one mapping (each chunk has exactly one vector in Qdrant)

### Validation Rules

1. `chunk_text` must not be empty or whitespace-only
2. `embedding_vector` must have exactly 768 dimensions (Gemini embedding size)
3. `chunk_index` must be < `total_chunks`
4. `source_url` must be accessible (validate during ingestion)
5. `heading_path` array must not contain empty strings
6. `file_path` must exist in Docusaurus content directory

### State Transitions

- **Created**: Initial ingestion of book content
- **Updated**: Re-ingestion when source file changes (updates `updated_at`, new `qdrant_point_id`)
- **Deleted**: Source file removed from book (delete from both Qdrant and Postgres)

### Example

```json
{
  "id": "a3f2e1d4-5c6b-7890-abcd-ef1234567890",
  "chunk_text": "Physical AI combines robotics with artificial intelligence to create systems that can perceive, reason, and act in the physical world. Unlike traditional AI that operates purely in software, physical AI must account for real-world constraints like gravity, friction, and sensor noise.",
  "embedding_vector": [0.023, -0.145, 0.678, ...],  // 768 dimensions
  "file_path": "docs/chapter-01/introduction.md",
  "chapter": "Chapter 1: Introduction to Physical AI",
  "section": "1.1 What is Physical AI?",
  "heading_path": ["Introduction to Physical AI", "What is Physical AI?"],
  "source_url": "https://book.example.com/chapter-01/introduction",
  "chunk_index": 0,
  "total_chunks": 3,
  "qdrant_point_id": "a3f2e1d4-5c6b-7890-abcd-ef1234567890",
  "created_at": "2025-12-14T10:30:00Z",
  "updated_at": "2025-12-14T10:30:00Z"
}
```

---

## 2. Query

**Purpose**: Represents a user question submitted to the chatbot.

**Storage**: Application memory (request object), optionally logged to Postgres

### Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `question` | String | Yes | User's natural language question | Min length: 3 chars, Max length: 1000 chars |
| `embedding_vector` | Float[768] | Yes (generated) | Gemini embedding of question | Exactly 768 dimensions |
| `session_id` | String | No | Conversation session identifier | UUID format if provided |
| `max_results` | Integer | No | Number of chunks to retrieve | Default: 3, Range: 1-10 |
| `timestamp` | Timestamp | Yes | Query submission time | Auto-generated |

### Validation Rules

1. `question` must not be empty or whitespace-only
2. `question` must not contain malicious patterns (basic SQL injection, script tags)
3. `max_results` must be between 1 and 10
4. `session_id` must be valid UUID if provided

### Example

```json
{
  "question": "What is the difference between forward and inverse kinematics?",
  "embedding_vector": [0.112, -0.034, 0.456, ...],  // Generated via Gemini
  "session_id": "b4c3d2e1-6789-1234-cdef-567890abcdef",
  "max_results": 5,
  "timestamp": "2025-12-14T14:22:15Z"
}
```

---

## 3. RetrievedContext

**Purpose**: Represents chunks retrieved from Qdrant for a specific query.

**Storage**: Application memory (intermediate processing object)

### Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `chunk` | ContentChunk | Yes | Reference to retrieved chunk | Must be valid ContentChunk |
| `similarity_score` | Float | Yes | Cosine similarity to query | Range: 0.0-1.0 |
| `rank` | Integer | Yes | Position in retrieval results | 1-indexed |

### Validation Rules

1. `similarity_score` must be between 0.0 and 1.0
2. `rank` must be positive integer
3. Results must be sorted by `similarity_score` descending

### Example

```json
{
  "chunk": { /* ContentChunk object */ },
  "similarity_score": 0.87,
  "rank": 1
}
```

---

## 4. Response

**Purpose**: Represents the chatbot's answer to a user query.

**Storage**: Application memory (response object), optionally logged to Postgres

### Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `answer` | String | Yes | Generated response text | Min length: 10 chars |
| `sources` | SourceCitation[] | Yes | References to book sections | Min 0, Max 10 citations |
| `confidence` | Float | No | Response confidence score | Range: 0.0-1.0 |
| `response_time_ms` | Integer | Yes | Time to generate response | Positive integer |
| `query` | Query | Yes | Associated query object | Valid Query reference |

### SourceCitation Sub-Entity

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `chapter` | String | Yes | Chapter title | Max 256 chars |
| `section` | String | No | Section heading | Max 256 chars |
| `source_url` | String | Yes | Link to book page | Valid HTTPS URL |
| `relevance_score` | Float | Yes | Similarity score from retrieval | Range: 0.0-1.0 |

### Validation Rules

1. `answer` must not be empty
2. `sources` must contain at least one citation if `confidence` > 0.5
3. `response_time_ms` must be positive
4. `confidence` must be between 0.0 and 1.0
5. SourceCitation `relevance_score` must match corresponding RetrievedContext score

### Example

```json
{
  "answer": "Forward kinematics calculates the end-effector position given joint angles, while inverse kinematics solves for joint angles given a desired end-effector position. Forward kinematics is deterministic and computationally simple, but inverse kinematics can have multiple solutions or no solution at all.",
  "sources": [
    {
      "chapter": "Chapter 3: Robotic Kinematics",
      "section": "3.2 Forward Kinematics",
      "source_url": "https://book.example.com/chapter-03/forward-kinematics",
      "relevance_score": 0.89
    },
    {
      "chapter": "Chapter 3: Robotic Kinematics",
      "section": "3.3 Inverse Kinematics",
      "source_url": "https://book.example.com/chapter-03/inverse-kinematics",
      "relevance_score": 0.85
    }
  ],
  "confidence": 0.87,
  "response_time_ms": 1850,
  "query": { /* Query object */ }
}
```

---

## 5. ConversationSession

**Purpose**: Represents a user's interaction session with the chatbot (multi-turn conversations).

**Storage**: Application memory (optional persistence in Postgres for future enhancement)

### Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `session_id` | UUID | Yes | Unique session identifier | Generated on first query |
| `conversation_history` | QueryResponsePair[] | Yes | List of query-response exchanges | Max 10 exchanges (prevent unbounded growth) |
| `created_at` | Timestamp | Yes | Session start time | Auto-generated |
| `last_activity_at` | Timestamp | Yes | Last query timestamp | Auto-updated |
| `is_active` | Boolean | Yes | Session active status | True if last activity < 30 min ago |

### QueryResponsePair Sub-Entity

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `query` | Query | Yes | User query | Valid Query object |
| `response` | Response | Yes | Chatbot response | Valid Response object |
| `timestamp` | Timestamp | Yes | Exchange timestamp | Auto-generated |

### Validation Rules

1. `conversation_history` must not exceed 10 exchanges (enforce client-side and server-side)
2. `is_active` computed based on `last_activity_at` (session expires after 30 minutes of inactivity)
3. `session_id` must be unique across active sessions

### State Transitions

- **Created**: First query from new user
- **Active**: Any query within 30 minutes of last activity
- **Expired**: No activity for 30 minutes (can be garbage collected)

### Example

```json
{
  "session_id": "b4c3d2e1-6789-1234-cdef-567890abcdef",
  "conversation_history": [
    {
      "query": { /* Query object */ },
      "response": { /* Response object */ },
      "timestamp": "2025-12-14T14:22:15Z"
    },
    {
      "query": { /* Follow-up query */ },
      "response": { /* Follow-up response */ },
      "timestamp": "2025-12-14T14:23:42Z"
    }
  ],
  "created_at": "2025-12-14T14:22:15Z",
  "last_activity_at": "2025-12-14T14:23:42Z",
  "is_active": true
}
```

---

## Database Schema (Postgres)

### Table: `chunks`

```sql
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_text TEXT NOT NULL CHECK (length(chunk_text) >= 50),
    file_path VARCHAR(512) NOT NULL,
    chapter VARCHAR(256),
    section VARCHAR(256),
    heading_path TEXT[],
    source_url VARCHAR(512) NOT NULL,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    total_chunks INTEGER NOT NULL CHECK (total_chunks > chunk_index),
    qdrant_point_id UUID NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT valid_file_path CHECK (file_path ~ '^docs/.*\.(md|mdx)$')
);

CREATE INDEX idx_file_path ON chunks(file_path);
CREATE INDEX idx_qdrant_point_id ON chunks(qdrant_point_id);
CREATE INDEX idx_chapter ON chunks(chapter);
```

### Table: `query_logs` (Optional - Monitoring)

```sql
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    response_text TEXT,
    chunks_retrieved INTEGER CHECK (chunks_retrieved BETWEEN 0 AND 10),
    response_time_ms INTEGER CHECK (response_time_ms > 0),
    confidence_score REAL CHECK (confidence_score BETWEEN 0.0 AND 1.0),
    session_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_session_id ON query_logs(session_id);
CREATE INDEX idx_created_at ON query_logs(created_at);
```

---

## Entity Lifecycle Summary

```
1. INGESTION PHASE:
   Docusaurus Content → Chunking → Gemini Embedding → ContentChunk
   ContentChunk → (Vector: Qdrant, Metadata: Postgres)

2. QUERY PHASE:
   User Question → Query → Gemini Embedding
   Query Vector → Qdrant Search → RetrievedContext[]
   RetrievedContext + Query → LLM Generation → Response

3. SESSION MANAGEMENT:
   Query + Response → ConversationSession.conversation_history
   Session timeout (30 min) → Session expiry
```

---

## Validation Summary

| Entity | Critical Validations |
|--------|---------------------|
| ContentChunk | Vector dimension = 768, chunk_index < total_chunks, non-empty text |
| Query | 3-1000 char question, max_results 1-10, sanitized input |
| Response | Non-empty answer, sources present if confidence > 0.5 |
| ConversationSession | Max 10 exchanges, 30-min timeout |
| SourceCitation | Valid URL, relevance_score 0.0-1.0 |

---

**Next Steps**: Proceed to contract generation (OpenAPI spec) and quickstart documentation.
