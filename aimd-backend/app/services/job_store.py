"""
Media analysis job store backed by Supabase Postgres.

Replaces the previous in-memory dict. Each job is a row in the
`media_jobs` table. Forensic signals, heatmap regions, and other
structured data are stored as JSONB in `classification_result`.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.db.supabase_client import get_supabase
from app.models.schemas import (
    AnalyzeMediaResponse,
    ForensicSignal,
    HeatmapRegion,
    JobStatus,
    MediaType,
    ThreatLevel,
)

logger = logging.getLogger("aimd.job_store")

_in_memory_jobs: dict[str, AnalyzeMediaResponse] = {}


async def create_job(job_id: str, case_id: str | None = None) -> AnalyzeMediaResponse:
    """Insert a new queued media job into the database or in-memory fallback store."""
    now = datetime.now(timezone.utc)
    job = AnalyzeMediaResponse(
        job_id=job_id,
        case_id=case_id,
        status=JobStatus.queued,
        created_at=now,
    )
    _in_memory_jobs[job_id] = job

    try:
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            row = {
                "job_id": job_id,
                "status": JobStatus.queued.value,
                "created_at": now.isoformat(),
            }
            if case_id:
                row["case_id"] = case_id
            get_supabase().table("media_jobs").insert(row).execute()
    except Exception as exc:
        logger.warning("Supabase insert failed for job %s, using memory store: %s", job_id, exc)

    return job


async def get_job(job_id: str) -> Optional[AnalyzeMediaResponse]:
    """Fetch a media job by ID and deserialize into the response schema."""
    try:
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            result = (
                get_supabase()
                .table("media_jobs")
                .select("*")
                .eq("job_id", job_id)
                .maybe_single()
                .execute()
            )
            if result.data is not None:
                return _row_to_response(result.data)
    except Exception as exc:
        logger.warning("Supabase select failed for job %s, falling back to memory: %s", job_id, exc)

    return _in_memory_jobs.get(job_id)


async def update_job(job_id: str, **fields) -> Optional[AnalyzeMediaResponse]:
    """
    Update a media job with the given fields.
    """
    # Update in-memory job
    mem_job = _in_memory_jobs.get(job_id)
    if mem_job:
        for k, v in fields.items():
            if hasattr(mem_job, k):
                setattr(mem_job, k, v)

    try:
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            db_fields = _map_fields_to_db(fields)
            result = (
                get_supabase()
                .table("media_jobs")
                .update(db_fields)
                .eq("job_id", job_id)
                .execute()
            )
            if result.data:
                return _row_to_response(result.data[0])
    except Exception as exc:
        logger.warning("Supabase update failed for job %s: %s", job_id, exc)

    return _in_memory_jobs.get(job_id)


def _map_fields_to_db(fields: dict) -> dict:
    """
    Map AnalyzeMediaResponse field names to database column names.

    The DB uses a flatter schema:
    - forensic_signals, heatmap_regions → packed into classification_result JSONB
    - sha256_original → sha256_hash
    - media_type → file_type
    - confidence_score → confidence_score (same)
    """
    db = {}

    # Direct mappings
    direct = {
        "status": "status",
        "original_filename": "original_filename",
        "confidence_score": "confidence_score",
        "model_version": "model_version",
        "frames_analyzed": "frames_analyzed",
        "error": "error",
        "file_url": "file_url",
        "fallback_active": "fallback_active",
    }
    for src, dst in direct.items():
        if src in fields:
            value = fields[src]
            # Convert enums to their string values
            if hasattr(value, "value"):
                value = value.value
            db[dst] = value

    # Renamed fields
    if "sha256_original" in fields:
        db["sha256_hash"] = fields["sha256_original"]
    if "media_type" in fields:
        val = fields["media_type"]
        db["file_type"] = val.value if hasattr(val, "value") else val
    if "completed_at" in fields:
        val = fields["completed_at"]
        db["completed_at"] = val.isoformat() if isinstance(val, datetime) else val
    if "case_id" in fields:
        db["case_id"] = fields["case_id"]

    # Pack forensic signals + heatmap into classification_result JSONB
    classification = {}
    if "forensic_signals" in fields:
        classification["forensic_signals"] = [
            s.model_dump() if hasattr(s, "model_dump") else s
            for s in fields["forensic_signals"]
        ]
    if "heatmap_regions" in fields:
        classification["heatmap_regions"] = [
            r.model_dump() if hasattr(r, "model_dump") else r
            for r in fields["heatmap_regions"]
        ]
    if "threat_level" in fields:
        val = fields["threat_level"]
        classification["threat_level"] = val.value if hasattr(val, "value") else val

    if classification:
        db["classification_result"] = classification

    return db


def _row_to_response(row: dict) -> AnalyzeMediaResponse:
    """Deserialize a database row into an AnalyzeMediaResponse."""
    classification = row.get("classification_result") or {}

    # Extract forensic signals from JSONB
    forensic_signals = [
        ForensicSignal(**s) for s in classification.get("forensic_signals", [])
    ]
    heatmap_regions = [
        HeatmapRegion(**r) for r in classification.get("heatmap_regions", [])
    ]
    threat_level_str = classification.get("threat_level")

    return AnalyzeMediaResponse(
        job_id=row["job_id"],
        case_id=row.get("case_id"),
        status=JobStatus(row["status"]),
        original_filename=row.get("original_filename"),
        media_type=MediaType(row["file_type"]) if row.get("file_type") else None,
        file_url=row.get("file_url"),
        sha256_original=row.get("sha256_hash"),
        threat_level=ThreatLevel(threat_level_str) if threat_level_str else None,
        confidence_score=row.get("confidence_score"),
        forensic_signals=forensic_signals,
        heatmap_regions=heatmap_regions,
        frames_analyzed=row.get("frames_analyzed"),
        model_version=row.get("model_version"),
        fallback_active=row.get("fallback_active", False),
        created_at=row["created_at"],
        completed_at=row.get("completed_at"),
        error=row.get("error"),
    )
