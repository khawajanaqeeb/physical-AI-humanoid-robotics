-- Migration: Create queries table
-- Description: Stores user queries with retrieval results and generated answers

CREATE TABLE IF NOT EXISTS queries (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    user_session_id UUID NOT NULL,
    selected_text TEXT,  -- NULL if no text selection
    retrieved_chunk_ids TEXT[] NOT NULL,  -- Array of chunk IDs
    answer_text TEXT NOT NULL,
    citations JSONB NOT NULL,  -- Array of {title, anchor, url}
    similarity_scores FLOAT[] NOT NULL,  -- Parallel to retrieved_chunk_ids
    retrieval_time_ms INT NOT NULL,
    answer_time_ms INT NOT NULL,
    citation_time_ms INT NOT NULL,
    total_time_ms INT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_arrays CHECK (
        array_length(retrieved_chunk_ids, 1) = array_length(similarity_scores, 1)
    ),
    CONSTRAINT valid_times CHECK (
        total_time_ms >= retrieval_time_ms + answer_time_ms + citation_time_ms
    )
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_queries_session ON queries(user_session_id);
CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_queries_total_time ON queries(total_time_ms);

-- Comment on table
COMMENT ON TABLE queries IS 'Stores user queries with retrieval results and generated answers for analytics';
COMMENT ON COLUMN queries.query_text IS 'User question in English';
COMMENT ON COLUMN queries.user_session_id IS 'Browser session UUID from sessionStorage';
COMMENT ON COLUMN queries.selected_text IS 'Optional text selection for context';
COMMENT ON COLUMN queries.retrieved_chunk_ids IS 'Array of chunk IDs retrieved from Qdrant';
COMMENT ON COLUMN queries.citations IS 'JSONB array of citation objects with title, anchor, url';
COMMENT ON COLUMN queries.similarity_scores IS 'Parallel array of similarity scores for retrieved chunks';
