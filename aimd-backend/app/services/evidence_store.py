import os
from pathlib import Path
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def save_evidence(job_id: str, filename: str, contents: bytes) -> str:
    """Save evidence file immutably.
    Creates a directory under settings.EVIDENCE_UPLOAD_DIR/job_id,
    writes the file, then sets read‑only permissions (0o444).
    Returns the absolute file path.
    """
    base_dir = Path(settings.EVIDENCE_UPLOAD_DIR)
    job_dir = base_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    # Ensure filename is safe
    safe_name = Path(filename).name
    file_path = job_dir / safe_name
    with open(file_path, "wb") as f:
        f.write(contents)
    # Make file read‑only (immutable for this process)
    try:
        os.chmod(file_path, 0o444)
    except Exception as exc:
        logger.warning("Failed to set read‑only permissions on %s: %s", file_path, exc)
    return str(file_path)
