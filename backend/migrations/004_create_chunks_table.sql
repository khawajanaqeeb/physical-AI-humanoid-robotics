-- Migration 004: Create chunks table for Gemini RAG
-- This table stores metadata for content chunks indexed in Qdrant
-- The actual vectors are stored in Qdrant, this is for metadata and reference

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_text TEXT NOT NULL CHECK (length(chunk_text) >= 50),
    file_path VARCHAR(512) NOT NULL,
    chapter VARCHAR(256),
    section VARCHAR(256),
    heading_path TEXT[],  -- Array of heading hierarchy
    source_url VARCHAR(512) NOT NULL,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    total_chunks INTEGER NOT NULL CHECK (total_chunks > chunk_index),
    qdrant_point_id UUID NOT NULL UNIQUE,  -- Reference to Qdrant vector point
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add constraint for valid file paths (Docusaurus markdown files)
ALTER TABLE chunks
    ADD CONSTRAINT valid_file_path
    CHECK (file_path ~ '^docs/.*\.(md|mdx)$');

-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_chunks_file_path ON chunks(file_path);
CREATE INDEX IF NOT EXISTS idx_chunks_qdrant_point_id ON chunks(qdrant_point_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chapter ON chunks(chapter);
CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at);

-- Create GIN index for full-text search on chunk_text (optional, for fallback search)
CREATE INDEX IF NOT EXISTS idx_chunks_text_search ON chunks USING gin(to_tsvector('english', chunk_text));

-- Add comment to table
COMMENT ON TABLE chunks IS 'Metadata for content chunks indexed in Qdrant vector database';
COMMENT ON COLUMN chunks.qdrant_point_id IS 'UUID matching the point ID in Qdrant collection';
COMMENT ON COLUMN chunks.heading_path IS 'Hierarchical path of headings (e.g., ["Chapter 1", "Section 1.1"])';
COMMENT ON COLUMN chunks.chunk_index IS 'Position of this chunk within the parent document (0-indexed)';
