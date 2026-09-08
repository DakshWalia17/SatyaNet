"""
Evidence file storage backed by Supabase Object Storage.

Replaces the previous local-disk (tempdir) implementation. All evidence
files are uploaded to the configured Supabase Storage bucket so they
persist across container restarts and can be re-downloaded for integrity
checks at certificate-generation time.
"""
import logging
import os
import tempfile
from typing import Optional

from app.config import settings
from app.db.supabase_client import get_supabase, storage_client

logger = logging.getLogger("aimd.upload_store")


# Local fallback directory when Supabase is not configured
_FALLBACK_DIR = os.path.join(tempfile.gettempdir(), "aimd_evidence_uploads")
os.makedirs(_FALLBACK_DIR, exist_ok=True)
_local_index: dict[str, str] = {}


def save_upload(job_id: str, filename: str, contents: bytes) -> str:
    """
    Upload evidence bytes to Supabase Storage, with fallback to local disk.

    Returns the storage path of the uploaded file.
    """
    suffix = os.path.splitext(filename or "")[1] or ".bin"
    storage_path = f"{job_id}/{job_id}{suffix}"

    # Always save locally as fallback / cache
    local_job_dir = os.path.join(_FALLBACK_DIR, job_id)
    os.makedirs(local_job_dir, exist_ok=True)
    local_file_path = os.path.join(local_job_dir, f"{job_id}{suffix}")
    with open(local_file_path, "wb") as f:
        f.write(contents)
    _local_index[job_id] = local_file_path

    # Try Supabase Storage if configured
    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
        try:
            content_type = _guess_content_type(suffix)
            bucket = storage_client().from_(settings.SUPABASE_MEDIA_BUCKET)
            bucket.upload(
                path=storage_path,
                file=contents,
                file_options={"content-type": content_type},
            )
            logger.info("Uploaded evidence file to Supabase %s/%s", settings.SUPABASE_MEDIA_BUCKET, storage_path)
            return storage_path
        except Exception as exc:
            logger.warning("Supabase upload failed, using local storage: %s", exc)

    return storage_path


def get_file_url(storage_path: str) -> str:
    """
    Return a signed URL for a file in the evidence bucket.
    The URL is valid for 1 hour (3600 seconds).
    """
    bucket = storage_client().from_(settings.SUPABASE_MEDIA_BUCKET)
    result = bucket.create_signed_url(storage_path, 3600)
    return result["signedURL"]


def find_upload(job_id: str) -> Optional[str]:
    """
    Locate a previously-uploaded evidence file by job_id.
    """
    if job_id in _local_index and os.path.exists(_local_index[job_id]):
        return _local_index[job_id]

    local_job_dir = os.path.join(_FALLBACK_DIR, job_id)
    if os.path.isdir(local_job_dir):
        files = os.listdir(local_job_dir)
        if files:
            return os.path.join(local_job_dir, files[0])

    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
        try:
            bucket = storage_client().from_(settings.SUPABASE_MEDIA_BUCKET)
            files = bucket.list(path=job_id)
            if files:
                return f"{job_id}/{files[0]['name']}"
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not list files for job %s: %s", job_id, exc)

    return None


def download_to_temp(storage_path: str) -> str:
    """
    Download a file from Supabase Storage to a local temp file, or return existing local path.
    """
    if os.path.exists(storage_path):
        return storage_path

    if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
        try:
            bucket = storage_client().from_(settings.SUPABASE_MEDIA_BUCKET)
            file_bytes = bucket.download(storage_path)

            _, ext = os.path.splitext(storage_path)
            fd, temp_path = tempfile.mkstemp(suffix=ext or ".bin")
            try:
                os.write(fd, file_bytes)
            finally:
                os.close(fd)

            logger.debug("Downloaded %s to temp file %s", storage_path, temp_path)
            return temp_path
        except Exception as exc:
            logger.warning("Failed downloading from Supabase storage: %s", exc)

    # If storage_path is job_id/job_id.ext
    parts = storage_path.replace("\\", "/").split("/")
    if len(parts) >= 2:
        candidate = os.path.join(_FALLBACK_DIR, parts[0], parts[1])
        if os.path.exists(candidate):
            return candidate

    raise FileNotFoundError(f"Evidence file not found: {storage_path}")


def upload_spectrogram(job_id: str, png_bytes: bytes) -> str:
    """
    Upload a mel-spectrogram PNG to Supabase Storage and return the
    storage path. Used by the audio pipeline to persist spectrogram
    visualizations.
    """
    storage_path = f"{job_id}/spectrogram.png"
    bucket = storage_client().from_(settings.SUPABASE_MEDIA_BUCKET)
    bucket.upload(
        path=storage_path,
        file=png_bytes,
        file_options={"content-type": "image/png"},
    )
    logger.info("Uploaded spectrogram for job %s", job_id)
    return storage_path


def _guess_content_type(ext: str) -> str:
    """Map common file extensions to MIME types."""
    mapping = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
        ".mkv": "video/x-matroska",
        ".webm": "video/webm",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
    }
    return mapping.get(ext.lower(), "application/octet-stream")
