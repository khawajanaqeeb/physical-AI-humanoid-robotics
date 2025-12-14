# ADR-0003: Backend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-14
- **Feature:** 002-gemini-rag-chatbot
- **Context:** The RAG chatbot backend must handle async I/O for external APIs (Gemini, Qdrant, Postgres), provide RESTful endpoints for the frontend, enforce input validation, and support observability. The stack must integrate seamlessly with Python 3.11+, support OpenAPI documentation, and enable rapid development with minimal boilerplate.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use **FastAPI as the async Python backend framework** with the following integrated stack:

- **Framework**: FastAPI (Python 3.11+)
- **Async Runtime**: uvicorn (ASGI server)
- **Validation**: Pydantic v2 models for request/response schemas
- **API Documentation**: Auto-generated OpenAPI 3.0 specs via FastAPI
- **Middleware Stack**:
  - CORS: Restricted to Docusaurus domain whitelist
  - Rate Limiting: `slowapi` (100 requests/min per IP)
  - Logging: Structured JSON logs with request ID tracing
  - Timeout: 10s max per request
- **Testing**: pytest with pytest-asyncio for async test support
- **Dependencies**:
  - `google-generativeai`: Gemini API client
  - `qdrant-client`: Qdrant vector DB client
  - `asyncpg`: Postgres async connection pool
  - `pydantic`, `pydantic-settings`: Configuration and validation

## Consequences

### Positive

- **Native Async Support**: FastAPI built on ASGI; optimal for concurrent external API calls (Gemini, Qdrant, Postgres)
- **Automatic Validation**: Pydantic models enforce contract validation with zero boilerplate
- **OpenAPI Integration**: Auto-generated interactive API docs (`/docs`) for frontend developers
- **Type Safety**: Full Python type hints enable static analysis and IDE autocomplete
- **Developer Experience**: Minimal boilerplate, fast iteration, clear error messages
- **Performance**: Async I/O reduces latency for multi-step RAG pipeline (embed → search → generate)
- **Testing Ecosystem**: pytest-asyncio enables clean async test patterns

### Negative

- **Framework Lock-In**: Migration to Django/Flask would require significant refactoring
- **ASGI Complexity**: Debugging async code more challenging than synchronous alternatives
- **Middleware Configuration**: Requires careful ordering and setup (CORS, rate limiting, logging)
- **Memory Overhead**: Async event loop and connection pools increase baseline memory usage
- **Learning Curve**: Developers unfamiliar with async Python may face initial friction

## Alternatives Considered

### Alternative 1: Django + Django REST Framework (DRF)
- **Pros**: Mature ecosystem, built-in ORM, admin panel, extensive middleware
- **Cons**: Heavier framework, async support less mature, more boilerplate, overkill for simple API
- **Why Not Chosen**: Too heavy for a lightweight RAG API; FastAPI's async-first design better suited for external API calls

### Alternative 2: Flask + Flask-RESTful
- **Pros**: Lightweight, simple, widely known, easy to learn
- **Cons**: **No native async support** (requires `quart` fork), manual validation, no auto-generated OpenAPI docs
- **Why Not Chosen**: Async I/O critical for RAG pipeline performance; FastAPI provides better DX and validation

### Alternative 3: Starlette (Raw ASGI)
- **Pros**: Minimal overhead, full control over async behavior, FastAPI built on Starlette
- **Cons**: Requires manual request parsing, no automatic validation, no OpenAPI generation
- **Why Not Chosen**: FastAPI adds valuable abstractions (Pydantic integration, OpenAPI) with negligible performance cost

### Alternative 4: Node.js (Express or Fastify)
- **Pros**: Native async, large ecosystem, good for microservices
- **Cons**: Requires Python → JS interop for Gemini/Qdrant clients, type safety weaker than Python + Pydantic
- **Why Not Chosen**: Python specified as project language (3.11+); ecosystem better for ML/AI workloads

## References

- Feature Spec: `specs/002-gemini-rag-chatbot/spec.md`
- Implementation Plan: `specs/002-gemini-rag-chatbot/plan.md`
- Research Document: `specs/002-gemini-rag-chatbot/research.md` (Section 5: FastAPI Best Practices)
- Project Structure: `specs/002-gemini-rag-chatbot/plan.md` (backend/ directory layout)
- Related ADRs: ADR-0001 (AI/ML Stack), ADR-0002 (Data Storage)
- Evaluator Evidence: To be created during implementation phase
