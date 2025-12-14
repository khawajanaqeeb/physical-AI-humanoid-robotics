-- Migration: Create feedback table
-- Description: Captures user thumbs-up/thumbs-down feedback on answers

CREATE TABLE IF NOT EXISTS feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES queries(query_id) ON DELETE CASCADE,
    feedback_type VARCHAR(20) NOT NULL CHECK (feedback_type IN ('positive', 'negative')),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_feedback_query ON feedback(query_id);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp DESC);

-- Comment on table
COMMENT ON TABLE feedback IS 'Captures user thumbs-up/thumbs-down feedback on answers';
COMMENT ON COLUMN feedback.query_id IS 'Reference to the query that received feedback';
COMMENT ON COLUMN feedback.feedback_type IS 'Either positive (thumbs up) or negative (thumbs down)';
