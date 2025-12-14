# ADR-0005: Deployment Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-14
- **Feature:** 002-gemini-rag-chatbot
- **Context:** The RAG chatbot consists of a FastAPI backend (Python) and a Docusaurus-embedded frontend (React). The backend must be publicly accessible via HTTPS for the frontend to call. The deployment strategy affects cost, operational complexity, scalability, and security. The solution must work within free-tier constraints and support CI/CD workflows.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use a **separated deployment architecture** with managed platforms:

- **Backend Deployment**:
  - Platform: **Render.com, Railway.app, or Fly.io** (free tier)
  - Containerization: Docker container with FastAPI + dependencies
  - Environment: Managed environment variables (API keys, DB URLs)
  - Health Checks: `/health` endpoint for uptime monitoring
  - Auto-Scaling: Platform-managed (serverless or containerized)
  - HTTPS: Automatic TLS certificates provided by platform
  - CI/CD: Deploy on push to `main` branch via GitHub integration

- **Frontend Deployment**:
  - Platform: **GitHub Pages** (existing Docusaurus deployment)
  - Build Process: Docusaurus build includes chatbot plugin
  - Configuration: `apiUrl` set via `docusaurus.config.js` build-time env var
  - CORS: Backend whitelist configured for GitHub Pages domain

- **Configuration Management**:
  - Backend: `.env` file (local dev) + platform env vars (production)
  - Frontend: Build-time env vars in Docusaurus config
  - Secrets: **Never commit API keys**; use `.env.example` template

- **Monitoring & Observability**:
  - Backend logs: Structured JSON logs to platform logging service
  - Uptime monitoring: Platform health checks + optional external monitor (UptimeRobot)
  - Error tracking: Console logs (initial); Sentry integration (future enhancement)

## Consequences

### Positive

- **Separation of Concerns**: Backend and frontend deployable independently; reduces coupling
- **Free-Tier Availability**: Both platforms offer free tiers sufficient for expected usage
- **Zero DevOps Overhead**: Managed platforms handle scaling, HTTPS, monitoring, and uptime
- **Automatic HTTPS**: TLS certificates managed by platform; no manual configuration
- **CI/CD Integration**: GitHub-native deployments enable automatic updates on code push
- **Platform Flexibility**: Easy to migrate between Render/Railway/Fly.io (similar Docker-based APIs)
- **Existing Docusaurus Workflow**: GitHub Pages already used for book; no new deployment pipeline

### Negative

- **Platform Lock-In**: Migration to AWS/GCP requires significant infrastructure changes
- **Cold Start Latency**: Free-tier containers may sleep after inactivity (Render: 15 min, Railway: 5 min)
- **Limited Free-Tier Resources**: CPU/memory constraints may require paid tier at scale
- **CORS Configuration**: Must correctly whitelist GitHub Pages domain; misconfiguration breaks API calls
- **Dual Deployment Complexity**: Two separate deployments to manage (backend + frontend)
- **Environment Variable Management**: Must sync backend API URL across environments (dev, staging, prod)

## Alternatives Considered

### Alternative 1: Monolithic Deployment (Backend + Frontend on Same Server)
- **Pros**: Single deployment, simpler CORS, easier local development
- **Cons**: Couples backend updates to frontend rebuilds, harder to scale independently, loses GitHub Pages hosting
- **Why Not Chosen**: Separation of concerns preferred; Docusaurus already deployed to GitHub Pages

### Alternative 2: Serverless Functions (AWS Lambda, Vercel Serverless, Cloudflare Workers)
- **Pros**: Auto-scaling, pay-per-request, no cold starts (Cloudflare Workers), simpler architecture
- **Cons**: Cold start latency (AWS Lambda), complex async dependencies (Qdrant, Postgres), function timeout limits (10s-15s)
- **Why Not Chosen**: RAG pipeline may exceed serverless timeout limits; containerized backend more flexible

### Alternative 3: Self-Hosted VPS (DigitalOcean, Linode, Hetzner)
- **Pros**: Full control, predictable pricing, no platform lock-in
- **Cons**: Manual HTTPS setup, server maintenance, security patching, no auto-scaling, higher operational burden
- **Why Not Chosen**: Excessive overhead for MVP; managed platforms eliminate DevOps work

### Alternative 4: AWS (EC2 + S3 + CloudFront)
- **Pros**: Enterprise-grade, highly scalable, rich ecosystem, fine-grained control
- **Cons**: Complex setup, steep learning curve, no meaningful free tier beyond 12 months, overkill for chatbot
- **Why Not Chosen**: Over-engineered for project scope; Render/Railway provide simpler, cost-effective solution

### Alternative 5: Netlify (Backend as Netlify Functions + Frontend)
- **Pros**: Unified platform, excellent DX, Git-based deploys, generous free tier
- **Cons**: Netlify Functions (AWS Lambda) have timeout limits; complex async dependencies harder to manage
- **Why Not Chosen**: Serverless timeout constraints; containerized backend (Render/Railway) better for RAG pipeline

## References

- Feature Spec: `specs/002-gemini-rag-chatbot/spec.md`
- Implementation Plan: `specs/002-gemini-rag-chatbot/plan.md`
- Research Document: `specs/002-gemini-rag-chatbot/research.md` (Section 7: Deployment Strategy)
- Related ADRs: ADR-0003 (Backend Stack), ADR-0004 (Frontend Integration)
- Evaluator Evidence: To be created during implementation phase
