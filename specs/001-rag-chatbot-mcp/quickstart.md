# Quickstart Guide: RAG Chatbot System

**Feature**: 001-rag-chatbot-mcp
**Date**: 2025-12-10
**Audience**: Developers setting up local environment

## Prerequisites

- Python 3.11+
- Node.js 18+ (for Docusaurus)
- Qdrant Cloud account
- Neon Postgres account
- OpenAI API key

---

## 1. Environment Setup

### Clone and Install Dependencies

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Environment Variables

Create `.env` file in `backend/`:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres
DATABASE_URL=postgresql://user:password@your-neon-host/dbname

# MCP Server
MCP_SERVER_PATH=/path/to/mcp-server

# Application
FRONTEND_URL=http://localhost:3000
API_PORT=8000
```

---

## 2. Database Setup

### Initialize Neon Postgres

```bash
cd backend
python scripts/init_database.py
```

This creates:
- `queries` table
- `feedback` table
- `sync_jobs` table
- Required indexes

### Initialize Qdrant Collection

```bash
python scripts/init_qdrant.py
```

This creates:
- `textbook_chunks` collection
- Payload indexes for file_path and section_anchor

---

## 3. Initial Content Sync

### Run First Sync

```bash
python scripts/sync_content.py --initial
```

This will:
1. Scan `../frontend/docs/` directory for markdown files
2. Extract chunks with MCP server
3. Generate embeddings with OpenAI
4. Upsert to Qdrant

Expected output:
```
[INFO] Starting initial content sync
[INFO] Found 15 markdown files
[INFO] Processing chapter-01/intro.md...
[INFO] Generated 12 chunks
[INFO] Embedded 12 chunks (cost: $0.002)
[INFO] Upserted to Qdrant
...
[SUCCESS] Sync completed: 15 files, 180 chunks, $0.023 total
```

---

## 4. Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Verify health:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "qdrant": "ok",
    "mcp_server": "ok",
    "openai_api": "ok"
  },
  "version": "1.0.0"
}
```

---

## 5. Start Frontend (Docusaurus)

```bash
cd frontend
npm start
```

This starts Docusaurus dev server at `http://localhost:3000`.

---

## 6. Test the System

### Test Query via API

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is forward kinematics?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Expected response:
```json
{
  "answer": "Forward kinematics is the process of calculating...",
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
```

### Test Chat Widget

1. Open `http://localhost:3000` in browser
2. Click floating chat button (bottom-right)
3. Type a question: "What is forward kinematics?"
4. Verify answer with clickable citations appears
5. Click citation link and verify navigation to section

### Test Text Selection

1. On any documentation page, select text (10+ characters)
2. Verify "Ask AI" button appears
3. Click button
4. Verify chat opens with selected text pre-populated

---

## 7. Common Issues

### Issue: "MCP server not responding"

**Solution**: Verify MCP server is running:
```bash
# Check MCP server process
ps aux | grep mcp-server

# Restart if needed
python -m mcp_server --port 5000
```

### Issue: "Qdrant connection failed"

**Solution**: Check Qdrant Cloud credentials:
```bash
# Test connection
python -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='YOUR_URL', api_key='YOUR_KEY')
print(client.get_collections())
"
```

### Issue: "OpenAI rate limit exceeded"

**Solution**: Reduce batch size in `backend/app/services/embeddings.py`:
```python
EMBEDDING_BATCH_SIZE = 50  # Reduced from 100
```

### Issue: "Database connection pool exhausted"

**Solution**: Increase pool size in `backend/app/database.py`:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,  # Increased from 10
    max_overflow=10
)
```

---

## 8. Next Steps

### Enable Scheduled Syncs

Add cron job to run sync every 6 hours:

```bash
# crontab -e
0 */6 * * * /path/to/venv/bin/python /path/to/backend/scripts/sync_content.py
```

### Deploy to Production

See deployment guide in `specs/001-rag-chatbot-mcp/plan.md` (Section 7).

### Monitor System

Access analytics queries:

```sql
-- Query volume per day
SELECT DATE(timestamp), COUNT(*)
FROM queries
GROUP BY DATE(timestamp)
ORDER BY DATE(timestamp) DESC;

-- Feedback sentiment
SELECT
  feedback_type,
  COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM feedback
GROUP BY feedback_type;

-- Average query latency
SELECT AVG(total_time_ms) as avg_latency_ms
FROM queries
WHERE timestamp > NOW() - INTERVAL '24 hours';
```

---

## Development Tips

### Hot Reload

- Backend: `uvicorn` with `--reload` watches for Python file changes
- Frontend: `npm start` watches for React/MDX file changes

### Debug Logging

Enable debug logs in `.env`:
```bash
LOG_LEVEL=DEBUG
```

### Test Individual Agents

```bash
# Test Retrieval Agent
python -m app.agents.retrieval --query "forward kinematics"

# Test Answer Agent
python -m app.agents.answer --context "chunk1.txt" --query "explain this"

# Test Citation Agent
python -m app.agents.citation --answer "answer.txt" --chunks "chunks.json"
```

### Database Migrations

Create migration:
```bash
cd backend
alembic revision -m "add_new_column"
# Edit generated migration file
alembic upgrade head
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Docusaurus Plugin Development](https://docusaurus.io/docs/advanced/plugins)
- [Context7 MCP Server](https://github.com/context7/mcp-server)

---

**Support**: For issues, check logs in `backend/logs/` or contact development team.
