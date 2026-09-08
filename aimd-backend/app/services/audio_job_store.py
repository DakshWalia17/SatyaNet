"""
Audio analysis job store backed by Supabase Postgres.

Replaces the previous in-memory dict. Each job is a row in the
`audio_jobs` table. Forensic signals and other structured data
are stored as JSONB in `classification_result`.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.db.supabase_client import get_supabase
from app.models.schemas import (
    AnalyzeAudioResponse,
    ForensicSignal,
    JobStatus,
    VoiceAuthenticity,
)

logger = logging.getLogger("aimd.audio_job_store")

_in_memory_audio_jobs: dict[str, AnalyzeAudioResponse] = {}


async def create_job(job_id: str, case_id: str | None = None) -> AnalyzeAudioResponse:
    """Insert a new queued audio job into the database or in-memory fallback store."""
    now = datetime.now(timezone.utc)
    job = AnalyzeAudioResponse(
        job_id=job_id,
        case_id=case_id,
        status=JobStatus.queued,
        created_at=now,
    )
    _in_memory_audio_jobs[job_id] = job

    try:
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            row = {
                "job_id": job_id,
                "status": JobStatus.queued.value,
                "created_at": now.isoformat(),
            }
            if case_id:
                row["case_id"] = case_id
            get_supabase().table("audio_jobs").insert(row).execute()
    except Exception as exc:
        logger.warning("Supabase insert failed for audio job %s, using memory store: %s", job_id, exc)

    return job


async def get_job(job_id: str) -> Optional[AnalyzeAudioResponse]:
    """Fetch an audio job by ID and deserialize into the response schema."""
    try:
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            result = (
                get_supabase()
                .table("audio_jobs")
                .select("*")
                .eq("job_id", job_id)
                .maybe_single()
                .execute()
            )
            if result.data is not None:
                return _row_to_response(result.data)
    except Exception as exc:
        logger.warning("Supabase select failed for audio job %s, falling back to memory: %s", job_id, exc)

    return _in_memory_audio_jobs.get(job_id)


async def update_job(job_id: str, **fields) -> Optional[AnalyzeAudioResponse]:
    """
    Update an audio job with the given fields.
    """
    # Update in-memory job
    mem_job = _in_memory_audio_jobs.get(job_id)
    if mem_job:
        for k, v in fields.items():
            if hasattr(mem_job, k):
                setattr(mem_job, k, v)

    try:
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            db_fields = _map_fields_to_db(fields)
            result = (
                get_supabase()
                .table("audio_jobs")
                .update(db_fields)
                .eq("job_id", job_id)
                .execute()
            )
            if result.data:
                return _row_to_response(result.data[0])
    except Exception as exc:
        logger.warning("Supabase update failed for audio job %s: %s", job_id, exc)

    return _in_memory_audio_jobs.get(job_id)


def _map_fields_to_db(fields: dict) -> dict:
    """Map AnalyzeAudioResponse field names to database column names."""
    db = {}

    # Direct mappings
    direct = {
        "status": "status",
        "original_filename": "original_filename",
        "confidence_score": "synthetic_voice_score",
        "duration_seconds": "duration_seconds",
        "sample_rate_hz": "sample_rate_hz",
        "segments_analyzed": "segments_analyzed",
        "model_version": "model_version",
        "mel_spectrogram_url": "mel_spectrogram_url",
        "error": "error",
        "file_url": "file_url",
        "fallback_active": "fallback_active",
    }
    for src, dst in direct.items():
        if src in fields:
            value = fields[src]
            if hasattr(value, "value"):
                value = value.value
            db[dst] = value

    # Renamed fields
    if "sha256_original" in fields:
        db["sha256_hash"] = fields["sha256_original"]
    if "completed_at" in fields:
        val = fields["completed_at"]
        db["completed_at"] = val.isoformat() if isinstance(val, datetime) else val
    if "case_id" in fields:
        db["case_id"] = fields["case_id"]

    # Pack forensic signals + voice_authenticity into classification_result JSONB
    classification = {}
    if "forensic_signals" in fields:
        classification["forensic_signals"] = [
            s.model_dump() if hasattr(s, "model_dump") else s
            for s in fields["forensic_signals"]
        ]
    if "voice_authenticity" in fields:
        val = fields["voice_authenticity"]
        classification["voice_authenticity"] = val.value if hasattr(val, "value") else val

    if classification:
        db["classification_result"] = classification

    # mel_spectrogram_png_base64 is NOT stored in the DB — the URL is stored instead.
    # Callers should upload the PNG to Supabase Storage and pass mel_spectrogram_url.

    return db


def _row_to_response(row: dict) -> AnalyzeAudioResponse:
    """Deserialize a database row into an AnalyzeAudioResponse."""
    classification = row.get("classification_result") or {}

    forensic_signals = [
        ForensicSignal(**s) for s in classification.get("forensic_signals", [])
    ]
    voice_auth_str = classification.get("voice_authenticity")

    return AnalyzeAudioResponse(
        job_id=row["job_id"],
        case_id=row.get("case_id"),
        status=JobStatus(row["status"]),
        original_filename=row.get("original_filename"),
        file_url=row.get("file_url"),
        sha256_original=row.get("sha256_hash"),
        voice_authenticity=VoiceAuthenticity(voice_auth_str) if voice_auth_str else None,
        confidence_score=row.get("synthetic_voice_score"),
        forensic_signals=forensic_signals,
        duration_seconds=row.get("duration_seconds"),
        sample_rate_hz=row.get("sample_rate_hz"),
        mel_spectrogram_url=row.get("mel_spectrogram_url"),
        segments_analyzed=row.get("segments_analyzed"),
        model_version=row.get("model_version"),
        fallback_active=row.get("fallback_active", False),
        created_at=row["created_at"],
        completed_at=row.get("completed_at"),
        error=row.get("error"),
    )
