"""
Section 65B certificate generation.

DESIGN NOTE — bridging decision: the original spec's route is
`GET /cases/{case_id}/pdf`, implying a persisted "case" entity in a
database. Case persistence (Supabase) isn't wired up yet (see README known
gaps across all modules), so for now `case_id` is an officer-supplied
identifier (e.g. the department's own case/FIR number) used purely for
display on the certificate, and the actual evidence is referenced by the
job_id(s) returned from /analyze/media and/or /analyze/audio. A single
certificate can bundle one of each (e.g. a video exhibit and a linked
audio exhibit under the same case). Once a real `cases` table exists, this
endpoint should look up case_id there instead of taking job ids directly
as query params — that's a route-internals change, not a route-shape
change, so nothing downstream needs to be rewritten.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.auth import verify_auth_token
from app.models.schemas import JobStatus
from app.services import audio_job_store, job_store, upload_store
from app.services.certificate import generate_section_65b_pdf
from app.services.hashing import sha256_file

logger = logging.getLogger("aimd.routes.cases")

router = APIRouter(prefix="/api/v1", tags=["cases"])


def _verify_integrity(job_id: str, original_hash: str | None) -> dict:
    """
    Re-hashes the evidence file as currently stored on this server and
    compares it against the hash captured at ingestion — a real chain-of-
    custody check, not a cosmetic one. Degrades gracefully (rather than
    failing the whole certificate) if the file is no longer present, e.g.
    ephemeral container storage was recycled since analysis ran.
    """
    path = upload_store.find_upload(job_id)
    if path is None:
        return {
            "recomputed_sha256": None,
            "match": None,
            "note": "Original evidence file is no longer present on this server for re-verification "
                    "(not yet migrated to permanent storage).",
        }
    recomputed = sha256_file(path)
    return {"recomputed_sha256": recomputed, "match": recomputed == original_hash}


@router.get("/cases/{case_id}/pdf")
async def get_case_certificate_pdf(
    case_id: str,
    officer_badge_id: str = Query(..., description="Badge ID of the certifying officer."),
    media_job_id: str | None = Query(default=None, description="job_id from a completed /analyze/media call."),
    audio_job_id: str | None = Query(default=None, description="job_id from a completed /analyze/audio call."),
    officer_name: str | None = Query(default=None, description="Full name of the certifying officer."),
    notes: str | None = Query(default=None, description="Optional free-text investigating officer notes."),
):
    """
    Generates a court-facing Section 65B DRAFT certificate PDF for one or
    both of a completed media/audio analysis job. Requires at least one
    of media_job_id / audio_job_id, and both referenced jobs (if given)
    must already be in `completed` status.
    """
    if not media_job_id and not audio_job_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one of media_job_id or audio_job_id.",
        )

    media_job = None
    media_integrity = None
    if media_job_id:
        media_job = await job_store.get_job(media_job_id)
        if media_job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"media_job_id '{media_job_id}' not found.")
        if media_job.status != JobStatus.completed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"media_job_id '{media_job_id}' is not completed yet (status={media_job.status.value}).",
            )
        media_integrity = _verify_integrity(media_job_id, media_job.sha256_original)

    audio_job = None
    audio_integrity = None
    if audio_job_id:
        audio_job = await audio_job_store.get_job(audio_job_id)
        if audio_job is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"audio_job_id '{audio_job_id}' not found.")
        if audio_job.status != JobStatus.completed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"audio_job_id '{audio_job_id}' is not completed yet (status={audio_job.status.value}).",
            )
        audio_integrity = _verify_integrity(audio_job_id, audio_job.sha256_original)

    pdf_bytes = generate_section_65b_pdf(
        case_id=case_id,
        officer_badge_id=officer_badge_id,
        officer_name=officer_name,
        notes=notes,
        media_job=media_job,
        media_job_id=media_job_id,
        audio_job=audio_job,
        audio_job_id=audio_job_id,
        media_integrity=media_integrity,
        audio_integrity=audio_integrity,
    )

    logger.info(
        "Generated Section 65B certificate for case %s (media_job=%s, audio_job=%s, officer_badge=%s)",
        case_id, media_job_id, audio_job_id, officer_badge_id,
    )

    filename = f"AIMD_Section65B_{case_id}.pdf".replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
