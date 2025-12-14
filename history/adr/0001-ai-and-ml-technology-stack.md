# ADR-0001: AI and ML Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-14
- **Feature:** 002-gemini-rag-chatbot
- **Context:** The RAG chatbot requires embedding generation for semantic search, vector similarity matching, and natural language response generation. The choice of AI/ML stack affects retrieval accuracy, cost, operational complexity, and long-term maintainability. The specification explicitly requires Google Gemini embeddings exclusively (no OpenAI dependencies).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use an **all-Google Gemini AI stack** for the RAG chatbot:

- **Embedding Model**: `models/embedding-001` (768-dimensional vectors)
- **Task Types**: `retrieval_document` for content indexing, `retrieval_query` for user questions
- **Response Generation**: Gemini Pro via `google-generativeai` SDK
- **SDK**: Official `google-generativeai` Python package for all AI operations
- **Rate Limiting**: Respect free-tier limits (60 requests/minute) with exponential backoff
- **Caching Strategy**: Cache embeddings; regenerate only for new/modified content

## Consequences

### Positive

- **Unified Ecosystem**: Single SDK and API key for embeddings and generation reduces integration complexity
- **Optimized for Retrieval**: Dedicated embedding model with task-type parameters improves semantic search accuracy
- **Free Tier Availability**: 60 requests/minute supports expected usage (~1,000 queries/day) without cost
- **Production-Ready SDK**: Official Google SDK handles authentication, retries, and error handling
- **Specification Compliance**: Meets explicit requirement for Gemini-only implementation (no OpenAI)
- **Consistent Vector Dimensions**: 768-dimensional embeddings are well-supported by modern vector databases

### Negative

- **Vendor Lock-In**: Switching to alternative embedding providers requires complete re-indexing of vector database
- **Rate Limit Constraints**: Free-tier limits (60 req/min) may require throttling during traffic spikes
- **Embedding Quality**: Less control over embedding model compared to fine-tuned custom models
- **API Dependency**: Service outages or API changes directly impact chatbot availability
- **No Multi-Provider Fallback**: Cannot easily switch to OpenAI/Cohere if Gemini encounters issues

## Alternatives Considered

### Alternative 1: OpenAI Embeddings (text-embedding-3-small/large)
- **Pros**: Industry-standard, extensive documentation, higher retrieval benchmarks on some datasets
- **Cons**: **Rejected** due to explicit specification requirement for Gemini-only implementation
- **Why Not Chosen**: Violates core project constraint (no OpenAI dependencies)

### Alternative 2: Multi-Provider Approach (Gemini + OpenAI fallback)
- **Pros**: Redundancy during outages, ability to A/B test embedding quality
- **Cons**: Requires dual indexing (separate vector collections), increased operational complexity, higher costs
- **Why Not Chosen**: Over-engineered for initial implementation; adds significant complexity without clear benefit

### Alternative 3: Self-Hosted Open-Source Embeddings (Sentence Transformers, BGE)
- **Pros**: No API rate limits, full control over model, no vendor lock-in
- **Cons**: Requires GPU infrastructure, model hosting overhead, maintenance burden, lower quality for specialized domains
- **Why Not Chosen**: Adds infrastructure complexity; managed API service preferred for MVP

### Alternative 4: Gemini Text Models for Embeddings (using generate_content)
- **Pros**: Uses same generation endpoint
- **Cons**: Not optimized for retrieval tasks, inconsistent vector representations, poor semantic search performance
- **Why Not Chosen**: Dedicated embedding models (`embedding-001`) are purpose-built for retrieval and significantly outperform text-to-text generation for semantic search

## References

- Feature Spec: `specs/002-gemini-rag-chatbot/spec.md`
- Implementation Plan: `specs/002-gemini-rag-chatbot/plan.md`
- Research Document: `specs/002-gemini-rag-chatbot/research.md` (Section 1: Gemini Embedding API Integration)
- Related ADRs: ADR-0002 (Data Storage Architecture)
- Evaluator Evidence: To be created during implementation phase
