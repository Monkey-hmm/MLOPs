import os
import uuid
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, Form, File, HTTPException, Query
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

from db import db
from models import (
    AppendResponse,
    DigestItem,
    ResultRequest,
    ResultResponse,
    DashboardResponse
)
from Storage.BucketHandler import BucketHandler, BucketHandlerError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bucket_handler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    global bucket_handler
    try:
        bucket_handler = BucketHandler()
    except BucketHandlerError as e:
        logger.error(f"Failed to initialize BucketHandler: {e}")
        raise RuntimeError("MinIO not configured correctly")
    
    await db.connect()
    yield
    # Teardown
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

@app.post("/append", response_model=AppendResponse)
async def append_item(
    team_id: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        # Upload to MinIO
        contents = await image.read()
        image_url = await asyncio.to_thread(
            bucket_handler.upload_bytes,
            contents, 
            image.filename, 
            image.content_type
        )
    except BucketHandlerError as e:
        logger.error(f"MinIO upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

    # Insert into DB
    try:
        job_id_str = await db.enqueue_job(team_id=team_id, image_url=image_url)
        job_id = uuid.UUID(job_id_str)
    except Exception as e:
        logger.error(f"DB enqueue error: {e}")
        raise HTTPException(status_code=500, detail="Failed to enqueue job")

    return AppendResponse(job_id=job_id)

@app.get("/digest", response_model=List[DigestItem])
async def digest_items(k: int = Query(10, gt=0)):
    try:
        jobs = await db.digest_jobs(k=k)
        return [
            DigestItem(job_id=uuid.UUID(str(job["job_id"])), image_url=job["image_url"], team_id=job["team_id"])
            for job in jobs
        ]
    except Exception as e:
        logger.error(f"DB digest error: {e}")
        raise HTTPException(status_code=500, detail="Failed to digest jobs")

@app.post("/result", response_model=ResultResponse)
async def add_result(result: ResultRequest):
    try:
        # asyncpg handles the updates
        success = await db.add_result(
            job_id=str(result.job_id), 
            prediction=result.prediction.value, 
            confidence=result.confidence
        )
    except Exception as e:
        logger.error(f"DB add result error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save result")
    
    return ResultResponse(ok=success, job_id=result.job_id)

@app.get("/", response_model=DashboardResponse)
async def get_dashboard():
    try:
        data = await db.get_dashboard_data()
        return DashboardResponse(**data)
    except Exception as e:
        logger.error(f"DB dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")

def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

if __name__ == "__main__":
    main()
