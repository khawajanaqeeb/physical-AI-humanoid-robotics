# Quickstart Guide: Gemini RAG Chatbot

**Feature**: 002-gemini-rag-chatbot
**Date**: 2025-12-14
**Audience**: Developers implementing the RAG chatbot system

---

## Overview

This guide provides step-by-step instructions to set up, develop, and deploy the Gemini-powered RAG chatbot for your Docusaurus book. Follow the phases in order for a successful implementation.

**Estimated Time**: 6-8 hours for complete implementation (excluding testing and content ingestion)

---

## Prerequisites

### Required Accounts & Services

1. **Google AI Studio Account**
   - Sign up at: https://makersuite.google.com/
   - Create API key for Gemini embeddings and generation
   - Free tier: 60 requests/minute

2. **Qdrant Cloud Account**
   - Sign up at: https://qdrant.tech/
   - Create a cluster (Free Tier: 1GB storage)
   - Note cluster URL and API key

3. **Neon Serverless Postgres Account**
   - Sign up at: https://neon.tech/
   - Create a database (Free Tier: 0.5GB storage)
   - Note connection string (DATABASE_URL)

4. **Cloud Deployment Platform** (Backend)
   - Recommended: Render.com, Railway.app, or Fly.io
   - Free tier available on all platforms

### Development Environment

- **Python**: 3.11 or higher
- **Node.js**: 18+ (for frontend development)
- **Git**: For version control
- **Code Editor**: VS Code recommended

---

## Phase 1: Backend Setup

### Step 1: Initialize Backend Project

```bash
# Create backend directory
mkdir -p backend/src/{models,services,api/endpoints,db}
mkdir -p backend/tests/{unit,integration,contract}
mkdir -p backend/scripts

cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.110.0
uvicorn[standard]==0.27.0
google-generativeai==0.3.2
qdrant-client==1.7.3
asyncpg==0.29.0
pydantic==2.6.0
pydantic-settings==2.1.0
python-dotenv==1.0.1
slowapi==0.1.9
pytest==8.0.0
pytest-asyncio==0.23.5
httpx==0.26.0
EOF

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Create .env file
cat > .env << EOF
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here

# Neon Postgres
DATABASE_URL=postgresql://user:password@your-neon-host/dbname

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,https://your-docusaurus-site.com
RATE_LIMIT=100/minute
EOF

# Create .env.example (safe to commit)
cat > .env.example << EOF
GEMINI_API_KEY=
QDRANT_URL=
QDRANT_API_KEY=
DATABASE_URL=
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=
RATE_LIMIT=100/minute
EOF
```

### Step 3: Set Up Database Schema

```bash
# Create database initialization script
cat > scripts/init_db.py << 'EOF'
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def init_database():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    # Create chunks table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
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
            CONSTRAINT valid_file_path CHECK (file_path ~ '^docs/.*\\.(md|mdx)$')
        );
    ''')

    # Create indexes
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON chunks(file_path);')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_qdrant_point_id ON chunks(qdrant_point_id);')
    await conn.execute('CREATE INDEX IF NOT EXISTS idx_chapter ON chunks(chapter);')

    # Create query_logs table (optional)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS query_logs (
            id SERIAL PRIMARY KEY,
            query_text TEXT NOT NULL,
            response_text TEXT,
            chunks_retrieved INTEGER CHECK (chunks_retrieved BETWEEN 0 AND 10),
            response_time_ms INTEGER CHECK (response_time_ms > 0),
            confidence_score REAL CHECK (confidence_score BETWEEN 0.0 AND 1.0),
            session_id UUID,
            created_at TIMESTAMP DEFAULT NOW()
        );
    ''')

    await conn.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON query_logs(session_id);')

    await conn.close()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(init_database())
EOF

# Run initialization
python scripts/init_db.py
```

### Step 4: Initialize Qdrant Collection

```bash
# Create Qdrant initialization script
cat > scripts/init_qdrant.py << 'EOF'
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
from dotenv import load_dotenv

load_dotenv()

def init_qdrant():
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

    collection_name = "docusaurus_book_chunks"

    # Check if collection exists
    collections = client.get_collections().collections
    if collection_name in [c.name for c in collections]:
        print(f"⚠️  Collection '{collection_name}' already exists")
        return

    # Create collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=768,  # Gemini embedding-001 dimension
            distance=Distance.COSINE
        )
    )

    print(f"✅ Qdrant collection '{collection_name}' created successfully")

if __name__ == "__main__":
    init_qdrant()
EOF

# Run initialization
python scripts/init_qdrant.py
```

### Step 5: Implement Core Backend (Minimal Scaffold)

```bash
# Create config.py
cat > src/config.py << 'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    database_url: str
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    rate_limit: str = "100/minute"

    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Create main.py (FastAPI app entry point)
cat > src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

app = FastAPI(
    title="Gemini RAG Chatbot API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Gemini RAG Chatbot API", "version": "1.0.0"}

# TODO: Import and register query and health endpoints
EOF
```

### Step 6: Run Backend Locally

```bash
# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Test**: Visit http://localhost:8000/docs to see OpenAPI documentation

---

## Phase 2: Content Ingestion

### Step 1: Prepare Docusaurus Content

Ensure your Docusaurus book is structured correctly:

```
docusaurus-book/
├── docs/
│   ├── chapter-01/
│   │   ├── introduction.md
│   │   └── ...
│   ├── chapter-02/
│   │   └── ...
│   └── ...
```

### Step 2: Implement Ingestion Script

```bash
# Create ingestion script (see implementation in tasks.md)
# Key functions:
# 1. Parse markdown files
# 2. Chunk content (512-1024 tokens, 128 overlap)
# 3. Generate Gemini embeddings
# 4. Upsert to Qdrant
# 5. Insert metadata to Postgres

python scripts/ingest_book.py --docs-path /path/to/docusaurus/docs
```

**Validation**: Check Qdrant dashboard and Postgres for ingested content

---

## Phase 3: Frontend Setup

### Step 1: Initialize Frontend Project

```bash
# Create frontend directory
mkdir -p frontend/src/{components,services,types}
mkdir -p frontend/tests

cd frontend

# Initialize npm project
npm init -y

# Install dependencies
npm install react@18 react-dom@18 typescript@5
npm install -D @types/react @types/react-dom
npm install axios  # For API calls

# Install testing dependencies
npm install -D jest @testing-library/react @testing-library/jest-dom

# Create tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM"],
    "jsx": "react",
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
EOF
```

### Step 2: Create Chat Component Scaffold

```typescript
// src/components/ChatWidget.tsx
import React, { useState } from 'react';
import { sendQuery } from '../services/api';

export const ChatWidget: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    try {
      const response = await sendQuery(question);
      setMessages([...messages, { type: 'user', text: question }, { type: 'bot', ...response }]);
      setQuestion('');
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-widget">
      {/* Chat UI implementation */}
    </div>
  );
};
```

### Step 3: Integrate with Docusaurus

**Option A: Custom Plugin (Recommended)**

```javascript
// In Docusaurus project root, create: plugins/rag-chat/index.js
module.exports = function (context, options) {
  return {
    name: 'docusaurus-plugin-rag-chat',
    injectHtmlTags() {
      return {
        headTags: [],
        postBodyTags: [
          {
            tagName: 'div',
            attributes: {
              id: 'rag-chat-root',
            },
          },
          {
            tagName: 'script',
            attributes: {
              src: '/js/rag-chat.bundle.js',
              defer: true,
            },
          },
        ],
      };
    },
  };
};

// docusaurus.config.js
module.exports = {
  plugins: [
    ['./plugins/rag-chat', { apiUrl: 'http://localhost:8000' }]
  ],
};
```

---

## Phase 4: Testing

### Backend Tests

```bash
cd backend
pytest tests/unit -v
pytest tests/integration -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Phase 5: Deployment

### Backend Deployment (Render.com Example)

1. Push code to GitHub
2. Create new Web Service on Render.com
3. Connect repository
4. Configure environment variables (from `.env`)
5. Deploy
6. Note public URL (e.g., `https://your-app.onrender.com`)

### Frontend Deployment

1. Build Docusaurus with chatbot integrated
2. Deploy to GitHub Pages as usual
3. Update frontend API URL to point to deployed backend

---

## Validation Checklist

- [ ] Backend `/health` endpoint returns `"status": "healthy"`
- [ ] Qdrant contains book chunks with 768-dim vectors
- [ ] Postgres contains chunk metadata
- [ ] Frontend can send queries to backend
- [ ] Responses include accurate answers and source citations
- [ ] CORS is correctly configured for production domain
- [ ] Rate limiting prevents abuse
- [ ] Error handling displays user-friendly messages

---

## Troubleshooting

**Issue: Gemini API rate limit errors during ingestion**
- Solution: Add delays between batch requests, reduce batch size

**Issue: CORS errors from frontend**
- Solution: Verify `CORS_ORIGINS` includes correct Docusaurus domain

**Issue: Poor retrieval quality**
- Solution: Adjust chunking strategy, experiment with chunk size and overlap

**Issue: Slow query responses**
- Solution: Reduce `max_results`, optimize Qdrant indexing, enable caching

---

## Next Steps

After completing this quickstart:
1. Review `/sp.tasks` for detailed implementation tasks
2. Run `/sp.implement` to execute task-based workflow
3. Iterate on chunking strategy based on real book content
4. Add monitoring and logging for production
5. Gather user feedback and iterate on UX

---

**Additional Resources**:
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docusaurus Plugins](https://docusaurus.io/docs/using-plugins)
