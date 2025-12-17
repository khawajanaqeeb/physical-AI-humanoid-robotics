---
id: 0002
title: Cohere Qdrant RAG Implementation Plan
stage: plan
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-cohere-qdrant-rag
branch: 003-cohere-qdrant-rag
user: datanaqeeb
command: /sp.plan
labels: ["planning", "architecture", "rag", "cohere", "qdrant", "fastapi"]
links:
  spec: specs/003-cohere-qdrant-rag/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-cohere-qdrant-rag/plan.md
  - specs/003-cohere-qdrant-rag/research.md
  - specs/003-cohere-qdrant-rag/data-model.md
  - specs/003-cohere-qdrant-rag/contracts/openapi.yaml
  - specs/003-cohere-qdrant-rag/contracts/schemas.json
  - specs/003-cohere-qdrant-rag/quickstart.md
  - CLAUDE.md
tests:
  - Phase 0 research complete with 7 key technical decisions
  - Phase 1 artifacts validated against spec.md requirements
---

## Prompt

/sp.plan

Context:
This planning phase follows the approved /sp.specify for the RAG chatbot integration of an already deployed Docusaurus textbook.

The specification is the single source of truth and must be followed exactly.

Objective of /sp.plan:
Produce a clear, step-by-step implementation plan for building the RAG chatbot using Cohere and Qdrant, suitable for manual execution and GitHub commits by the developer.

The plan must decompose the system into logical phases, responsibilities, and deliverables without writing implementation code.

Confirmed Constraints (must be respected):
- Embeddings and generation: Cohere only
- Vector database: Qdrant Cloud
- Backend: FastAPI (Python)
- Frontend: Existing Docusaurus site on Vercel
- No OpenAI/Gemini APIs
- No PostgreSQL or relational database
- No auto-commit or auto-push to GitHub
- Windows Command Prompt or PowerShell only
- Context7 MCP server available
- All secrets via .env
- CORS must allow Vercel frontend

Planning Requirements:
The plan must cover Project Structure, Environment Strategy, Data Ingestion Pipeline, Retrieval & RAG Pipeline, API Design, Frontend Integration, Testing, and Deployment.

## Response snapshot

Created comprehensive implementation plan for Cohere + Qdrant RAG chatbot with complete Phase 0 (Research) and Phase 1 (Design & Contracts) deliverables:

**Phase 0 Completed - Research & Architecture Decisions**:
1. Cohere embed-english-v3.0 (1024-dim) + command-r for RAG with citations
2. Qdrant Cloud single collection with COSINE similarity, HNSW indexing
3. BeautifulSoup HTML parsing with recursive semantic chunking (500-800 chars, 100-char overlap)
4. FastAPI + SlowAPI rate limiting (10 req/min per IP)
5. Tenacity retry library with exponential backoff
6. Pytest three-tier testing (unit, integration, contract)
7. Structured JSON logging for observability

**Phase 1 Completed - Design & Contracts**:
1. data-model.md: 5 domain entities (DocumentChunk, QuerySession, IngestionJob, SourceCitation, ErrorRecord) with validation rules, Qdrant mapping, and data flows
2. contracts/openapi.yaml: Complete OpenAPI 3.0 spec with 3 endpoints (POST /query, POST /ingest, GET /health), request/response schemas, error codes
3. contracts/schemas.json: JSON Schema validation rules for all API contracts
4. quickstart.md: Developer onboarding guide with prerequisites, environment setup, first ingestion, first query, troubleshooting

**Project Structure Defined**:
- Backend: Clean architecture (API, services, models, core, utils layers)
- 8-stage implementation sequence from foundation to deployment
- Testing strategy with unit/integration/contract tiers
- Deployment options (Railway/Render/Cloud Run/Lambda) with checklists

**Key Artifacts**:
- plan.md: 460 lines - complete implementation roadmap
- research.md: 450+ lines - 7 research areas with decisions, rationale, alternatives
- data-model.md: 350+ lines - complete entity specifications with validation
- openapi.yaml: 330 lines - production-ready API contract
- quickstart.md: 280+ lines - comprehensive developer guide

## Outcome

- ✅ Impact: Complete, production-ready implementation plan with all Phase 0 and Phase 1 deliverables. Establishes clear architectural foundation for Cohere-based RAG system with detailed technical decisions, API contracts, and developer onboarding.
- 🧪 Tests: Testing strategy defined (pytest with 3 tiers). Agent context updated with Python 3.11+, FastAPI, Cohere, Qdrant, BeautifulSoup4, tenacity, slowapi.
- 📁 Files: Created plan.md, research.md, data-model.md, openapi.yaml, schemas.json, quickstart.md. Updated CLAUDE.md with technology stack.
- 🔁 Next prompts: `/sp.tasks` to generate implementation task breakdown (Phase 2)
- 🧠 Reflection: Leveraged Context7 MCP server to fetch official Cohere and Qdrant documentation, ensuring implementation decisions based on authoritative sources. The plan provides clear separation between phases with well-defined outputs and dependencies. 8-stage implementation sequence provides logical progression from foundation to deployment.

## Evaluation notes (flywheel)

- Failure modes observed: None. User requirements from spec were comprehensive and unambiguous.
- Graders run and results (PASS/FAIL): Constitution check - PASS (all principles aligned, no violations)
- Prompt variant (if applicable): Standard /sp.plan workflow with Context7 MCP integration for research
- Next experiment (smallest change to try): None needed. Ready for /sp.tasks to generate implementation task breakdown.
