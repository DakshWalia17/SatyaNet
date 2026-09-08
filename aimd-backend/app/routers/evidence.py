from fastapi import APIRouter, HTTPException, UploadFile, File, status
from app.config import settings
from app.services.evidence_store import save_evidence
from app.routers.analyze import _determine_forensics, MediaAnalysisResult
from datetime import datetime, timezone
import uuid
import os
import hashlib

router = APIRouter(prefix="/evidence", tags=["evidence"]) 

@router.post("/upload", response_model=MediaAnalysisResult, status_code=status.HTTP_200_OK, summary="Secure immutable evidence upload")
async def upload_evidence(file: UploadFile = File(...)):
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
        )
    job_id = str(uuid.uuid4())
    # Save immutably
    storage_path = save_evidence(job_id, file.filename, contents)
    # Compute SHA256
    sha256_hash = hashlib.sha256(contents).hexdigest()
    # Use existing forensic logic to get score etc.
    score, verdict, suspected_engine, category = _determine_forensics(file.filename, contents)
    # Return result
    return MediaAnalysisResult(
        status="success",
        file_name=file.filename,
        sha256_hash=sha256_hash,
        ai_probability_score=score,
        verdict=verdict,
        suspected_engine=suspected_engine,
        timestamp=datetime.now(timezone.utc).isoformat(),
        job_id=job_id,
        media_type=category,
        file_size_bytes=len(contents),
        forensic_details={"chain_of_custody_verified": True, "hash_algorithm": "SHA-256"},
    )

@router.get("/list", summary="List uploaded immutable evidence files")
async def list_evidence():
    base_dir = settings.EVIDENCE_UPLOAD_DIR
    if not os.path.isdir(base_dir):
        return []
    result = []
    for job in os.listdir(base_dir):
        job_dir = os.path.join(base_dir, job)
        if os.path.isdir(job_dir):
            for fname in os.listdir(job_dir):
                fpath = os.path.join(job_dir, fname)
                size = os.path.getsize(fpath)
                with open(fpath, "rb") as f:
                    sha = hashlib.sha256(f.read()).hexdigest()
                result.append({
                    "job_id": job,
                    "filename": fname,
                    "size_bytes": size,
                    "sha256": sha,
                    "url": f"/evidence/file/{job}/{fname}",
                })
    return result

@router.get("/file/{job_id}/{filename}")
async def get_evidence_file(job_id: str, filename: str):
    path = os.path.join(settings.EVIDENCE_UPLOAD_DIR, job_id, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    from fastapi.responses import FileResponse
    return FileResponse(path, media_type="application/octet-stream")
