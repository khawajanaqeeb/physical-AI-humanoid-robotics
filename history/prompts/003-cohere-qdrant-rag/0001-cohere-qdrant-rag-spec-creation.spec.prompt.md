---
id: 0001
title: Cohere Qdrant RAG Spec Creation
stage: spec
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-cohere-qdrant-rag
branch: 003-cohere-qdrant-rag
user: datanaqeeb
command: /sp.specify
labels: ["rag", "cohere", "qdrant", "specification", "chatbot", "docusaurus"]
links:
  spec: specs/003-cohere-qdrant-rag/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-cohere-qdrant-rag/spec.md
  - specs/003-cohere-qdrant-rag/checklists/requirements.md
tests:
  - Specification validation checklist (all items passed)
---

## Prompt

/sp.specify

Project Title:
RAG Chatbot Integration for Deployed Docusaurus Textbook (Cohere + Qdrant)

Context:
This specification defines the RAG chatbot integration phase for an already deployed Docusaurus textbook hosted on Vercel.

Deployed Book URL:
https://physical-ai-humanoid-robotics-e3c7.vercel.app/

Sitemap URL (Primary ingestion source):
https://physical-ai-humanoid-robotics-e3c7.vercel.app/sitemap.xml

This specification COMPLETELY OVERRIDES any previous specifications related to OpenAI, Gemini, or other embedding providers. All legacy assumptions must be discarded.

---

Primary Goal:
Design a clean, production-ready Retrieval-Augmented Generation (RAG) chatbot that answers user questions strictly based on the textbook content, and can be embedded into the existing Docusaurus frontend.

---

Confirmed Technology Stack:

Backend:
- Python
- FastAPI

Embeddings & Generation:
- Cohere (via COHERE_API_KEY from .env)
- No OpenAI APIs
- No Gemini APIs

Vector Database:
- Qdrant Cloud
- Collection-based storage for textbook chunks

Frontend:
- Existing Docusaurus site (already deployed on Vercel)
- No redesign required
- Only integration of chatbot client logic

Infrastructure & Tooling Constraints:
- All secrets are managed via `.env`
- No PostgreSQL or relational database
- No OpenAI Agents SDK
- No Gemini SDK
- No automatic GitHub commits or pushes by the AI
- All GitHub commits and file pushes will be performed manually by the developer
- Do NOT use Bash commands
- Use only Windows Command Prompt (cmd) or Windows PowerShell commands when needed
- Context7 MCP server is available and may be used where appropriate

---

Data Ingestion Requirements:
- Use sitemap.xml as the authoritative source for content discovery
- Crawl and fetch Docusaurus pages listed in the sitemap
- Extract clean, readable text content
- Chunk content appropriately for embeddings
- Generate embeddings using Cohere
- Store vectors and metadata in Qdrant
- Metadata must include:
  - page URL
  - page title (if available)
  - section or heading context (if available)

---

Query & Retrieval Requirements:
- Accept user questions via a FastAPI endpoint
- Embed user queries using Cohere
- Perform semantic similarity search in Qdrant
- Retrieve top-K relevant chunks
- Generate grounded answers using only retrieved context
- Responses must not hallucinate beyond the provided content
- Include references or source URLs in the response where possible

---

API Design Requirements:
- Public endpoints for querying/chat
- Optional protected endpoints for ingestion or re-sync
- Support API_KEY-based protection for sensitive endpoints
- Proper CORS configuration for the deployed Vercel frontend

---

Environment Configuration:
The system must rely only on the following environment variables:
- COHERE_API_KEY
- QDRANT_URL
- QDRANT_API_KEY
- QDRANT_COLLECTION_NAME
- CORS_ORIGINS
- API_KEY (optional, may be empty during development)

No other environment variables should be assumed.

---

Non-Goals (Explicitly Excluded):
- No OpenAI integration
- No Gemini integration (this OVERRIDES previous specs)
- No PostgreSQL or relational database
- No authentication/authorization for end users
- No chat history persistence
- No automatic sitemap monitoring
- Only Cohere for embeddings and generation

## Response snapshot

Created comprehensive feature specification for RAG Chatbot Integration using Cohere + Qdrant:

**Feature Branch Created**: 003-cohere-qdrant-rag

**Specification Structure**:
1. Three prioritized user stories (P1: Query Content, P2: Navigation, P3: Synchronization) with independent testing criteria
2. 28 detailed functional requirements covering:
   - Data ingestion (FR-001 to FR-008): sitemap parsing, content extraction, chunking, embeddings, Qdrant storage
   - Query & retrieval (FR-009 to FR-016): query processing, semantic search, grounded response generation
   - API & integration (FR-017 to FR-023): public/protected endpoints, authentication, CORS, rate limiting
   - Error handling (FR-024 to FR-028): graceful degradation, retries, validation
3. Eight measurable success criteria (response time <3s, 95% citation accuracy, 85% answer success rate, 99% uptime)
4. Key entities: Document Chunk, Query Session, Ingestion Job
5. Clear scope boundaries and explicitly excluded features
6. Comprehensive edge cases (8 scenarios covering API limits, malformed data, service outages)

**Quality Validation**: All checklist items passed
- No implementation details leaked into specification
- All requirements testable and unambiguous
- Success criteria measurable and technology-agnostic
- Zero [NEEDS CLARIFICATION] markers (user provided complete requirements)

**Files Created**:
- specs/003-cohere-qdrant-rag/spec.md
- specs/003-cohere-qdrant-rag/checklists/requirements.md

## Outcome

- ✅ Impact: Complete, validated specification ready for architectural planning. Establishes clear requirements for Cohere-based RAG system replacing previous Gemini implementation.
- 🧪 Tests: Specification quality checklist validation passed (all items). Three independently testable user stories defined.
- 📁 Files: Created spec.md (207 lines) and requirements.md checklist
- 🔁 Next prompts: `/sp.plan` to design architecture, or `/sp.clarify` if refinement needed (not required - spec is complete)
- 🧠 Reflection: User provided exceptionally detailed requirements including technology stack constraints, API requirements, and explicit non-goals. This eliminated ambiguity and enabled creation of a complete specification without clarification questions. The clear separation from previous Gemini implementation ensures no legacy assumptions carry forward.

## Evaluation notes (flywheel)

- Failure modes observed: None. User requirements were comprehensive and unambiguous.
- Graders run and results (PASS/FAIL): Specification quality checklist - PASS (all items validated)
- Prompt variant (if applicable): Standard /sp.specify workflow with comprehensive user input
- Next experiment (smallest change to try): None needed. Proceed to planning phase with current specification.
