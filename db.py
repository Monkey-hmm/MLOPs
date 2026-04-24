import os
import asyncpg
from typing import List, Dict, Any, Optional

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            user=os.environ.get("POSTGRES_USER", "cyberthon"),
            password=os.environ.get("POSTGRES_PASSWORD", "cyberthon"),
            database=os.environ.get("POSTGRES_DB", "appdb"),
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=os.environ.get("POSTGRES_PORT", "5432"),
            min_size=1,
            max_size=10
        )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def enqueue_job(self, team_id: str, image_url: str) -> str:
        async with self.pool.acquire() as conn:
            # Ensure team exists
            await conn.execute(
                "INSERT INTO teams (id) VALUES ($1) ON CONFLICT (id) DO NOTHING",
                team_id
            )
            
            # Insert job
            job_id = await conn.fetchval(
                """
                INSERT INTO jobs (team_id, image_url, status)
                VALUES ($1, $2, 'queued')
                RETURNING id
                """,
                team_id, image_url
            )
            return str(job_id)

    async def digest_jobs(self, k: int) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            # FOR UPDATE SKIP LOCKED is critical for multiple workers
            records = await conn.fetch(
                """
                WITH selected_jobs AS (
                    SELECT id
                    FROM jobs
                    WHERE status = 'queued'
                    ORDER BY created_at ASC
                    LIMIT $1
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE jobs
                SET status = 'running',
                    started_at = NOW()
                FROM selected_jobs
                WHERE jobs.id = selected_jobs.id
                RETURNING jobs.id as job_id, jobs.image_url, jobs.team_id
                """,
                k
            )
            return [dict(record) for record in records]

    async def add_result(self, job_id: str, prediction: str, confidence: float) -> bool:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Idempotent insert
                result = await conn.execute(
                    """
                    INSERT INTO results (job_id, prediction, confidence)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (job_id) DO NOTHING
                    """,
                    job_id, prediction, confidence
                )
                
                # Update job status
                if result == "INSERT 0 1": # if it inserted
                    await conn.execute(
                        """
                        UPDATE jobs
                        SET status = 'completed',
                            finished_at = NOW()
                        WHERE id = $1
                        """,
                        job_id
                    )
                    return True
                return False

    async def get_dashboard_data(self) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            queued = await conn.fetch("SELECT * FROM jobs WHERE status = 'queued' ORDER BY created_at DESC LIMIT 50")
            running = await conn.fetch("SELECT * FROM jobs WHERE status = 'running' ORDER BY started_at DESC LIMIT 50")
            completed = await conn.fetch("SELECT * FROM jobs WHERE status = 'completed' ORDER BY finished_at DESC LIMIT 50")
            results = await conn.fetch("SELECT * FROM results ORDER BY created_at DESC LIMIT 50")
            
            return {
                "queued": [dict(r) for r in queued],
                "running": [dict(r) for r in running],
                "completed": [dict(r) for r in completed],
                "results": [dict(r) for r in results]
            }

db = Database()
