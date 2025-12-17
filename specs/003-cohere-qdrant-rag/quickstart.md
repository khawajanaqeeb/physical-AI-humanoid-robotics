# Quick Start Guide
**Feature**: RAG Chatbot Integration for Deployed Docusaurus Textbook (Cohere + Qdrant)
**Date**: 2025-12-16

## Prerequisites

### Required Accounts
1. **Cohere Account** (free tier sufficient for development)
   - Sign up: https://dashboard.cohere.com/
   - Generate API key from dashboard
   - Free tier includes: 1000 embeds/month, 1000 generations/month

2. **Qdrant Cloud Account** (free tier sufficient for development)
   - Sign up: https://qdrant.tech/
   - Create a cluster (1GB free tier)
   - Note cluster URL and API key

### Required Software
- Python 3.11 or higher
- pip (Python package manager)
- Git
- Text editor or IDE (VS Code recommended)

---

## Environment Setup

### 1. Clone Repository

```powershell
git clone <repository-url>
cd physical-AI-humanoid-robotics
git checkout 003-cohere-qdrant-rag
```

### 2. Install Dependencies

```powershell
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing
```

### 3. Configure Environment Variables

Create `.env` file in `backend/` directory:

```env
# Cohere API Configuration
COHERE_API_KEY=your-cohere-api-key-here

# Qdrant Cloud Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION_NAME=textbook_chunks

# API Configuration
CORS_ORIGINS=https://physical-ai-humanoid-robotics-e3c7.vercel.app/
API_KEY=your-secret-api-key-for-ingestion  # Optional, can be empty for dev

# Textbook Configuration
TEXTBOOK_SITEMAP_URL=https://physical-ai-humanoid-robotics-e3c7.vercel.app/sitemap.xml
```

**Security Note**: Never commit `.env` to Git. It's already in `.gitignore`.

---

## Local Development Workflow

### 1. Start the Server

```powershell
cd backend
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Verify Server Health

Open browser or use curl:
```powershell
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "cohere": {"status": "operational", "latency_ms": 45},
    "qdrant": {"status": "operational", "latency_ms": 30}
  },
  "timestamp": "2025-12-16T15:45:30Z"
}
```

---

## First Ingestion Run

### Trigger Ingestion

**Important**: Initial ingestion may take 5-10 minutes depending on textbook size.

```powershell
# Using PowerShell
$headers = @{ "X-API-Key" = "your-secret-api-key-for-ingestion" }
$body = @{ "force_refresh" = $false } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ingest" `
                  -Method POST `
                  -Headers $headers `
                  -Body $body `
                  -ContentType "application/json"
```

**Or use curl**:
```powershell
curl -X POST http://localhost:8000/api/v1/ingest `
     -H "X-API-Key: your-secret-api-key-for-ingestion" `
     -H "Content-Type: application/json" `
     -d "{\"force_refresh\": false}"
```

Expected response:
```json
{
  "job_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "status": "completed",
  "pages_processed": 150,
  "chunks_created": 1250,
  "chunks_updated": 0,
  "errors_encountered": [],
  "start_time": "2025-12-16T08:00:00Z",
  "end_time": "2025-12-16T08:07:30Z"
}
```

### Monitor Ingestion Progress

Check server logs for real-time progress:
```
INFO:     Processing page 1/150: https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/intro
INFO:     Created 8 chunks for page: Introduction to Humanoid Robotics
INFO:     Processing page 2/150: https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/setup
...
INFO:     Ingestion completed: 150 pages, 1250 chunks created
```

---

## First Query Test

### Submit a Test Query

```powershell
# Using PowerShell
$body = @{ "query" = "What are the main components of a humanoid robot?" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/query" `
                  -Method POST `
                  -Body $body `
                  -ContentType "application/json"
```

**Or use curl**:
```powershell
curl -X POST http://localhost:8000/api/v1/query `
     -H "Content-Type: application/json" `
     -d "{\"query\": \"What are the main components of a humanoid robot?\"}"
```

Expected response:
```json
{
  "answer": "Based on the textbook, the main components of a humanoid robot include actuators for movement, sensors for perception such as cameras and force sensors, control systems that coordinate all components, and power systems for energy supply...",
  "sources": [
    {
      "page_url": "https://physical-ai-humanoid-robotics-e3c7.vercel.app/docs/components",
      "page_title": "Robot Components",
      "chunk_text": "The primary components include actuators, sensors, control systems...",
      "relevance_score": 0.89
    }
  ],
  "metadata": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "response_time_ms": 1850,
    "retrieval_score_threshold": 0.7,
    "chunks_retrieved": 5
  }
}
```

---

## Running Tests

### Unit Tests
```powershell
cd backend
pytest tests/unit/ -v
```

### Integration Tests
```powershell
pytest tests/integration/ -v
```

### Contract Tests (requires real API keys)
```powershell
pytest tests/contract/ -v --slow
```

### All Tests with Coverage
```powershell
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser to view coverage report
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'cohere'"
**Solution**: Install dependencies
```powershell
pip install -r requirements.txt
```

### Issue: "ConnectionError: Failed to connect to Qdrant"
**Solutions**:
1. Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
2. Check Qdrant Cloud dashboard - cluster may be paused (free tier)
3. Test connection:
   ```powershell
   curl -H "api-key: your-api-key" https://your-cluster.qdrant.io/collections
   ```

### Issue: "CohereAPIError: invalid_api_key"
**Solution**: Verify `COHERE_API_KEY` in `.env` file
- Log in to https://dashboard.cohere.com/
- Navigate to API Keys section
- Copy correct API key

### Issue: "Rate limit exceeded" (429 error)
**Solutions**:
1. Wait 1 minute and retry (10 requests/minute limit)
2. For development, temporarily disable rate limiting in `src/api/middleware/rate_limit.py`

### Issue: Ingestion failing with "404 Not Found" for some pages
**Expected Behavior**: Some pages in sitemap may be removed or moved. Errors are logged but don't stop ingestion.
**Solution**: Check `errors_encountered` array in ingestion response. If critical pages are missing, update sitemap.

### Issue: Slow queries (>3 seconds)
**Possible Causes**:
1. Qdrant cluster cold start (first query after idle)
2. Cohere API latency
3. Large number of chunks retrieved

**Solutions**:
1. Reduce `max_results` parameter in query (default is 5)
2. Adjust `retrieval_score_threshold` to filter low-relevance chunks
3. Check Qdrant cluster metrics in dashboard

### Issue: Empty or irrelevant answers
**Possible Causes**:
1. Query doesn't match textbook content
2. Chunk quality issues (poor segmentation)
3. Retrieval threshold too high

**Solutions**:
1. Verify textbook contains relevant content
2. Adjust chunking parameters in `src/services/chunking_service.py`
3. Lower `retrieval_score_threshold` (default 0.7)
4. Re-run ingestion with `force_refresh=true`

---

## Next Steps

1. **Explore API Documentation**: http://localhost:8000/docs (auto-generated Swagger UI)
2. **Test with Real Queries**: Try questions from textbook exercises
3. **Monitor Logs**: Check structured logs for debugging
4. **Frontend Integration**: Update `frontend/plugins/rag-chatbot/chatWidget.js` to call backend API
5. **Deploy**: Choose deployment platform (Railway/Render/Cloud Run) and deploy backend

---

## Development Tips

### Hot Reload

FastAPI with `--reload` flag automatically restarts on code changes. No need to manually restart server during development.

### API Documentation

FastAPI provides interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Logging

Structured logs are written to stdout in JSON format. Use `jq` for pretty-printing:
```powershell
# If jq is installed
python -m uvicorn src.api.main:app | jq
```

### Testing Individual Components

```python
# Test Cohere service
from src.services.cohere_service import CohereService
cohere = CohereService()
embeddings = cohere.embed(["test text"])
print(f"Embedding dimensions: {len(embeddings[0])}")

# Test Qdrant service
from src.services.qdrant_service import QdrantService
qdrant = QdrantService()
health = qdrant.health_check()
print(f"Qdrant health: {health}")
```

---

## Additional Resources

- **API Contracts**: See `contracts/openapi.yaml`
- **Data Models**: See `data-model.md`
- **Implementation Plan**: See `plan.md`
- **Cohere Documentation**: https://docs.cohere.com/
- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
