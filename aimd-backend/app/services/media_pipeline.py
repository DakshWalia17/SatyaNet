"""
Orchestrates the full /analyze/media pipeline:
  1. Download evidence file from Supabase Storage to a local temp path
  2. Hash the original upload (chain of custody)
  3. Detect image vs. video
  4. Extract frame(s) (sampled for video, per config.VIDEO_FRAME_SAMPLE_RATE)
  5. Run the classifier on each frame
  6. Aggregate into a single confidence score + threat level
  7. Build the Forensic Signal Matrix + heatmap regions for the frontend
  8. Write the final result into the Supabase media_jobs table
"""
import logging
import os
from datetime import datetime, timezone

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import numpy as np
except ImportError:
    np = None

from PIL import Image

from app.config import settings
from app.ml.deepfake_model import predict_frame
from app.models.schemas import (
    ForensicSignal,
    HeatmapRegion,
    BoundingBox,
    JobStatus,
    MediaType,
    ThreatLevel,
)
from app.services import job_store
from app.services.hashing import sha256_file
from app.services.upload_store import download_to_temp

logger = logging.getLogger("aimd.pipeline")

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def detect_media_type(filename: str) -> MediaType:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in VIDEO_EXTENSIONS:
        return MediaType.video
    return MediaType.image  # default; unknown types treated as image and let PIL raise if invalid


def _extract_video_frames(path: str) -> list[np.ndarray]:
    frames = []
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError("Could not open video file for frame extraction.")
    idx = 0
    try:
        while len(frames) < settings.MAX_FRAMES_PER_VIDEO:
            ok, frame_bgr = cap.read()
            if not ok:
                break
            if idx % settings.VIDEO_FRAME_SAMPLE_RATE == 0:
                frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
            idx += 1
    finally:
        cap.release()
    return frames


def _threat_level_for(score: float) -> ThreatLevel:
    if score >= 0.7:
        return ThreatLevel.deepfake
    if score >= 0.4:
        return ThreatLevel.tampered
    return ThreatLevel.authentic


async def run_analysis(job_id: str, storage_path: str, original_filename: str) -> None:
    """
    Entry point invoked as a FastAPI BackgroundTask.

    Downloads the evidence file from Supabase Storage, runs analysis,
    and writes results back to the media_jobs table.
    """
    temp_path = None
    try:
        await job_store.update_job(job_id, status=JobStatus.processing)

        # Download from Supabase Storage to local temp for processing
        temp_path = download_to_temp(storage_path)

        sha256_original = sha256_file(temp_path)
        media_type = detect_media_type(original_filename)

        if media_type == MediaType.video:
            frames = _extract_video_frames(temp_path)
            if not frames:
                raise ValueError("No frames could be extracted from the video.")
            pil_frames = [Image.fromarray(f) for f in frames]
        else:
            pil_frames = [Image.open(temp_path).convert("RGB")]

        predictions = [predict_frame(f) for f in pil_frames]
        scores = [p.fake_probability for p in predictions]
        aggregate_score = float(np.mean(scores))
        threat_level = _threat_level_for(aggregate_score)

        # Check if any prediction came from the mock/fallback model
        fallback_active = any(
            p.signals.get("note", "").startswith("MOCK") for p in predictions
        )

        heatmap_regions: list[HeatmapRegion] = []
        for i, pred in enumerate(predictions):
            if pred.heatmap is None:
                continue
            h, w = pred.heatmap.shape
            heatmap_regions.append(
                HeatmapRegion(
                    frame_index=i,
                    box=BoundingBox(x=0, y=0, width=float(w), height=float(h)),
                    intensity=float(pred.heatmap.mean()),
                )
            )

        temporal_consistency = (
            1.0 - float(np.std(scores)) if len(scores) > 1 else 1.0
        )
        forensic_signals = [
            ForensicSignal(
                name="Facial / Manipulation Confidence",
                score=aggregate_score,
                description="Aggregate classifier confidence that the media contains AI-generated or manipulated content.",
            ),
            ForensicSignal(
                name="Temporal Consistency",
                score=round(max(0.0, min(1.0, temporal_consistency)), 3),
                description="Cross-frame stability of the manipulation score (low = jitter/inconsistency across frames, a common deepfake artifact).",
            ),
            ForensicSignal(
                name="Compression / FFT Noise",
                score=round(
                    float(np.mean([p.signals.get("compression_fft_noise", 0.0) for p in predictions])),
                    3,
                ),
                description="Noise/texture irregularity signal from frame analysis.",
            ),
        ]

        await job_store.update_job(
            job_id,
            status=JobStatus.completed,
            original_filename=original_filename,
            media_type=media_type,
            sha256_original=sha256_original,
            threat_level=threat_level,
            confidence_score=round(aggregate_score, 4),
            forensic_signals=forensic_signals,
            heatmap_regions=heatmap_regions,
            frames_analyzed=len(pil_frames),
            model_version=settings.DEEPFAKE_MODEL_ID,
            fallback_active=fallback_active,
            completed_at=datetime.now(timezone.utc),
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Analysis failed for job %s", job_id)
        await job_store.update_job(
            job_id,
            status=JobStatus.failed,
            error=str(exc),
            completed_at=datetime.now(timezone.utc),
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
