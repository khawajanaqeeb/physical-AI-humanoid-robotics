# ADR-0002: Data Storage Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-14
- **Feature:** 002-gemini-rag-chatbot
- **Context:** The RAG system requires storage for 768-dimensional embedding vectors, chunk metadata, and query logs. The architecture must support semantic similarity search at scale while maintaining separation of concerns between vector operations and relational metadata. Free-tier constraints require cloud-based managed services with sufficient capacity for a typical technical book (~100,000 words).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use a **dual-database architecture** with separation of concerns:

- **Vector Storage**: Qdrant Cloud (Free Tier) for 768-dimensional embeddings
  - Collection: `docusaurus_book_chunks`
  - Distance metric: Cosine similarity
  - Capacity: 1GB (~500K vectors)
  - Payload storage: Full chunk metadata in Qdrant

- **Relational Metadata**: Neon Serverless Postgres (Free Tier)
  - Tables: `chunks` (metadata), `query_logs` (optional monitoring)
  - Connection: `asyncpg` connection pool (min 2, max 10)
  - Capacity: 0.5GB storage
  - Purpose: Chunk traceability, re-indexing support, analytics

- **Indexing Strategy**: Synchronous dual writes (Qdrant + Postgres) during ingestion
- **Querying Strategy**: Qdrant-first search, metadata enrichment from payload

## Consequences

### Positive

- **Separation of Concerns**: Vector operations isolated from relational queries; optimized tooling for each
- **Managed Services**: Both platforms offer free tiers with auto-scaling, eliminating infrastructure overhead
- **Cosine Similarity Optimization**: Qdrant natively optimized for semantic search with HNSW indexing
- **Re-indexing Support**: Postgres tracks chunk-to-file mappings, enabling selective re-indexing on content changes
- **Free Tier Capacity**: 1GB vector storage supports 500K+ embeddings (far exceeding typical book needs)
- **Native Async Support**: Both clients integrate cleanly with FastAPI async patterns

### Negative

- **Dual Write Complexity**: Must maintain consistency across two databases during ingestion
- **Increased Latency**: Metadata enrichment may require Postgres lookups in addition to Qdrant search
- **Free-Tier Dependency**: Scaling beyond free tiers requires paid plans or migration
- **Operational Overhead**: Two separate services to monitor, debug, and maintain
- **Data Synchronization Risk**: If Qdrant and Postgres diverge, manual reconciliation required

## Alternatives Considered

### Alternative 1: Qdrant-Only (Metadata in Payload)
- **Pros**: Single database, simpler architecture, no dual-write complexity
- **Cons**: Limited relational query capabilities, harder to track provenance, less flexible for analytics
- **Why Not Chosen**: Postgres adds minimal cost while significantly improving metadata management and re-indexing workflows

### Alternative 2: Pinecone (Vector DB) + Supabase (Postgres)
- **Pros**: Similar architecture, Pinecone has mature ecosystem, Supabase offers more features than Neon
- **Cons**: Pinecone free tier (1M vectors, 1 index) may be restrictive; Supabase Auth/Storage features unnecessary
- **Why Not Chosen**: Qdrant preferred for open-source compatibility and better free-tier storage limits

### Alternative 3: FAISS (Local Vector Search) + SQLite
- **Pros**: No external dependencies, full control, no rate limits, offline-capable
- **Cons**: Requires manual persistence, poor scalability, lacks managed deployment, no serverless support
- **Why Not Chosen**: Managed cloud services eliminate operational burden; local storage incompatible with serverless backend

### Alternative 4: PostgreSQL with pgvector Extension (Single Database)
- **Pros**: Single database, simpler stack, native SQL integration, good for small-scale RAG
- **Cons**: Slower similarity search compared to Qdrant's HNSW indexing, requires self-hosting or paid tier (Neon doesn't support pgvector on free tier)
- **Why Not Chosen**: Qdrant provides superior semantic search performance; dual-database trade-off justified by retrieval speed gains

### Alternative 5: Elasticsearch/OpenSearch for Vector Search
- **Pros**: Mature ecosystem, full-text + vector hybrid search, powerful analytics
- **Cons**: Complex setup, no meaningful free tier, overkill for RAG use case, higher operational overhead
- **Why Not Chosen**: Over-engineered for chatbot needs; Qdrant provides simpler, purpose-built solution

## References

- Feature Spec: `specs/002-gemini-rag-chatbot/spec.md`
- Implementation Plan: `specs/002-gemini-rag-chatbot/plan.md`
- Research Document: `specs/002-gemini-rag-chatbot/research.md` (Sections 3 & 4: Qdrant and Postgres)
- Data Model: `specs/002-gemini-rag-chatbot/data-model.md` (Database Schema section)
- Related ADRs: ADR-0001 (AI/ML Stack)
- Evaluator Evidence: To be created during implementation phase
