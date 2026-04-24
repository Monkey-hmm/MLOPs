# Cyberthon MLOps Job Queue Backend

A minimal, production-safe FastAPI backend for an HPC-based image inference job queue system. This leverages PostgreSQL as the queue and MinIO for S3-compatible image storage.

## Features
- **Upload queue:** Images are uploaded to MinIO and jobs are recorded atomically in PostgreSQL.
- **HPC Pull-based Processing:** Workers pull batches of jobs using atomic locking (`FOR UPDATE SKIP LOCKED`) to ensure no duplicate processing.
- **Results Logging:** Workers submit processing results back safely via idempotent updates (`ON CONFLICT DO NOTHING`).
- **Dashboard:** Provides a JSON response displaying queued, running, completed jobs, and results.

## Requirements
- Python 3.11+
- `uv` package manager (or `pip` and a virtual environment)
- Docker & Docker Compose (for PostgreSQL and MinIO)

## Running Locally

### 1. Start Services
First, start PostgreSQL and MinIO using Docker Compose:

```bash
docker-compose up -d
```
This starts:
- PostgreSQL on port `5432`
- MinIO API on port `9000` (Console on `9090`)

A helper container (`minio-init`) automatically runs to create the `uploads` bucket and set it to public access. 

### 2. Initialize Database
Apply the schema to the database:

```bash
docker-compose exec -T db psql -U cyberthon -d appdb < schema.sql
```

### 3. Start the FastAPI App
Sync the python dependencies using `uv` and start the uvicorn server:

```bash
uv sync
uv run python main.py
```
*(Or use `uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload`)*

The API will now be running at `http://localhost:8080`.
Check the docs at `http://localhost:8080/docs`.

---

## API Endpoints

### `POST /append`
Uploads an image to MinIO and enqueues a job.
- **Body (Multipart/form-data):** `team_id` (string), `image` (file)
- **Response:** `{"job_id": "<uuid>"}`

### `GET /digest?k=10`
Pulls up to `k` queued jobs for processing. Automatically marks them as `running` safely.
- **Response:** Array of `{"job_id": "...", "image_url": "...", "team_id": "..."}`

### `POST /result`
Submits a result for a completed job.
- **Body (JSON):** `{"job_id": "<uuid>", "prediction": "real|fake", "confidence": 0.95}`
- **Response:** `{"ok": true, "job_id": "<uuid>"}`

### `GET /`
A minimal JSON dashboard of recent jobs and results.
