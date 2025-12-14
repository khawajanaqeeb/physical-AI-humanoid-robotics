-- Migration: Create sync_jobs table
-- Description: Tracks content synchronization runs for monitoring and debugging

CREATE TABLE IF NOT EXISTS sync_jobs (
    sync_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
    files_processed INT NOT NULL DEFAULT 0,
    files_failed INT NOT NULL DEFAULT 0,
    error_log JSONB,  -- Array of {file_path, error_message}

    CONSTRAINT valid_status CHECK (
        (status = 'running' AND end_time IS NULL) OR
        (status IN ('completed', 'failed') AND end_time IS NOT NULL)
    ),
    CONSTRAINT valid_counts CHECK (
        files_processed >= 0 AND files_failed >= 0
    )
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON sync_jobs(status);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_start_time ON sync_jobs(start_time DESC);

-- Comment on table
COMMENT ON TABLE sync_jobs IS 'Tracks content synchronization runs for monitoring and debugging';
COMMENT ON COLUMN sync_jobs.status IS 'Sync job status: running, completed, or failed';
COMMENT ON COLUMN sync_jobs.files_processed IS 'Number of files successfully processed';
COMMENT ON COLUMN sync_jobs.files_failed IS 'Number of files that failed to process';
COMMENT ON COLUMN sync_jobs.error_log IS 'JSONB array of error objects with file_path and error_message';
