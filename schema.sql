-- =========================
-- EXTENSIONS
-- =========================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =========================
-- ENUMS (keeps logic tight)
-- =========================
CREATE TYPE job_status AS ENUM (
    'queued',
    'running',
    'completed',
    'failed'
);

CREATE TYPE prediction_label AS ENUM (
    'real',
    'fake'
);

-- =========================
-- TEAMS
-- =========================
CREATE TABLE teams (
    id TEXT PRIMARY KEY,          -- keep simple (you already have IDs)
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- JOBS (QUEUE + SOURCE OF TRUTH)
-- =========================
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    team_id TEXT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,

    image_url TEXT NOT NULL,          -- stored in MinIO
    status job_status DEFAULT 'queued',

    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    finished_at TIMESTAMP,

    retry_count INT DEFAULT 0,
    error TEXT
);

-- 🔥 Critical for queue performance
CREATE INDEX idx_jobs_status_created
ON jobs(status, created_at);

-- =========================
-- RESULTS (FINAL OUTPUT)
-- =========================
CREATE TABLE results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    job_id UUID UNIQUE NOT NULL
        REFERENCES jobs(id) ON DELETE CASCADE,

    prediction prediction_label,
    confidence FLOAT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- =========================
-- OPTIONAL: WORKER LOGS (DEBUGGING)
-- =========================
CREATE TABLE logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    level TEXT,                     -- info / warning / error
    message TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_logs_job_id ON logs(job_id);

-- =========================
-- OPTIONAL: DEAD LETTER / FAILED JOBS VIEW
-- =========================
CREATE VIEW failed_jobs AS
SELECT *
FROM jobs
WHERE status = 'failed';

-- =========================
-- OPTIONAL: QUEUE METRICS VIEW (for UI)
-- =========================
CREATE VIEW job_metrics AS
SELECT
    COUNT(*) FILTER (WHERE status = 'queued')   AS queued,
    COUNT(*) FILTER (WHERE status = 'running')  AS running,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed,
    COUNT(*) FILTER (WHERE status = 'failed')   AS failed
FROM jobs;