"""
models.py – Pydantic schemas for request / response bodies.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums (mirror the PostgreSQL ENUM types)
# ---------------------------------------------------------------------------

class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class PredictionLabel(str, Enum):
    real = "real"
    fake = "fake"


# ---------------------------------------------------------------------------
# /append  – response
# ---------------------------------------------------------------------------

class AppendResponse(BaseModel):
    job_id: uuid.UUID


# ---------------------------------------------------------------------------
# /digest  – response item
# ---------------------------------------------------------------------------

class DigestItem(BaseModel):
    job_id: uuid.UUID
    image_url: str
    team_id: str


# ---------------------------------------------------------------------------
# /result  – request body
# ---------------------------------------------------------------------------

class ResultRequest(BaseModel):
    job_id: uuid.UUID
    prediction: PredictionLabel
    confidence: float = Field(..., ge=0.0, le=1.0)


class ResultResponse(BaseModel):
    ok: bool
    job_id: uuid.UUID


# ---------------------------------------------------------------------------
# GET /  – dashboard response
# ---------------------------------------------------------------------------

class JobRow(BaseModel):
    id: uuid.UUID
    team_id: str
    image_url: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    retry_count: int
    error: Optional[str] = None


class ResultRow(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    prediction: PredictionLabel
    confidence: float
    created_at: datetime


class DashboardResponse(BaseModel):
    queued: list[JobRow]
    running: list[JobRow]
    completed: list[JobRow]
    results: list[ResultRow]
