"""
Orchestrates the full /analyze/audio pipeline:
  1. Download evidence file from Supabase Storage to a local temp path
  2. Hash the original upload (chain of custody)
  3. Extract audio track via FFmpeg -> mono 16kHz WAV
  4. Generate a Mel-spectrogram PNG and upload to Supabase Storage
  5. Split into fixed-length segments and classify each for synthetic/
     cloned voice probability
  6. Aggregate into a single confidence score + voice authenticity verdict
  7. Write the final result into the Supabase audio_jobs table
"""
import base64
import logging
import os
import tempfile
import wave
from datetime import datetime, timezone

try:
    import numpy as np
except ImportError:
    np = None

from app.config import settings
from app.ml.audio_model import (
    generate_mel_spectrogram_png,
    predict_segment,
)
from app.models.schemas import ForensicSignal, JobStatus, VoiceAuthenticity
from app.services import audio_job_store
from app.services.audio_extraction import (
    AudioExtractionError,
    TARGET_SAMPLE_RATE,
    extract_audio_to_wav,
    probe_duration_seconds,
)
from app.services.hashing import sha256_file
from app.services.upload_store import download_to_temp, upload_spectrogram

logger = logging.getLogger("aimd.audio_pipeline")


def _read_wav_as_float32(wav_path: str) -> np.ndarray:
    with wave.open(wav_path, "rb") as wf:
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
        sample_width = wf.getsampwidth()

    if sample_width != 2:
        raise ValueError(f"Expected 16-bit PCM WAV, got sample width {sample_width}.")

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return samples


def _voice_authenticity_for(score: float) -> VoiceAuthenticity:
    if score >= 0.7:
        return VoiceAuthenticity.synthetic
    if score >= 0.4:
        return VoiceAuthenticity.inconclusive
    return VoiceAuthenticity.authentic


async def run_audio_analysis(job_id: str, storage_path: str, original_filename: str) -> None:
    """
    Entry point invoked as a FastAPI BackgroundTask.

    Downloads the evidence file from Supabase Storage, runs audio analysis,
    and writes results back to the audio_jobs table.
    """
    temp_path = None
    wav_path = None
    try:
        await audio_job_store.update_job(job_id, status=JobStatus.processing)

        # Download from Supabase Storage to local temp for processing
        temp_path = download_to_temp(storage_path)

        sha256_original = sha256_file(temp_path)

        wav_fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(wav_fd)
        try:
            extract_audio_to_wav(temp_path, wav_path)
        except AudioExtractionError as exc:
            raise ValueError(str(exc)) from exc

        duration_seconds = probe_duration_seconds(temp_path) or probe_duration_seconds(wav_path)
        samples = _read_wav_as_float32(wav_path)
        if samples.size == 0:
            raise ValueError("Extracted audio track is empty.")

        spectrogram_png_b64 = generate_mel_spectrogram_png(samples, TARGET_SAMPLE_RATE)

        # Upload spectrogram PNG to Supabase Storage
        mel_spectrogram_url = None
        if spectrogram_png_b64:
            png_bytes = base64.b64decode(spectrogram_png_b64)
            spec_storage_path = upload_spectrogram(job_id, png_bytes)
            # Store the storage path; callers can generate signed URLs as needed
            mel_spectrogram_url = spec_storage_path

        segment_len = int(settings.AUDIO_SEGMENT_SECONDS * TARGET_SAMPLE_RATE)
        segments = [
            samples[i:i + segment_len]
            for i in range(0, len(samples), segment_len)
            if len(samples[i:i + segment_len]) > TARGET_SAMPLE_RATE * 0.5  # skip sub-0.5s tail scraps
        ][: settings.MAX_AUDIO_SEGMENTS]
        if not segments:
            segments = [samples]  # very short clip: analyze as a single segment

        predictions = [predict_segment(seg, TARGET_SAMPLE_RATE) for seg in segments]
        scores = [p.synthetic_probability for p in predictions]
        aggregate_score = float(np.mean(scores))
        verdict = _voice_authenticity_for(aggregate_score)

        # Check if any prediction came from the mock/fallback model
        fallback_active = any(
            p.signals.get("note", "").startswith("MOCK") for p in predictions
        )

        segment_consistency = 1.0 - float(np.std(scores)) if len(scores) > 1 else 1.0
        forensic_signals = [
            ForensicSignal(
                name="Synthetic Voice Confidence",
                score=round(aggregate_score, 3),
                description="Aggregate classifier confidence that the voice is AI-generated or cloned rather than natural human speech.",
            ),
            ForensicSignal(
                name="Segment Consistency",
                score=round(max(0.0, min(1.0, segment_consistency)), 3),
                description="Stability of the synthetic-voice score across segments (low = inconsistent, e.g. only part of the clip is cloned).",
            ),
        ]

        await audio_job_store.update_job(
            job_id,
            status=JobStatus.completed,
            original_filename=original_filename,
            sha256_original=sha256_original,
            voice_authenticity=verdict,
            confidence_score=round(aggregate_score, 4),
            forensic_signals=forensic_signals,
            duration_seconds=round(duration_seconds, 2),
            sample_rate_hz=TARGET_SAMPLE_RATE,
            mel_spectrogram_url=mel_spectrogram_url,
            segments_analyzed=len(segments),
            model_version=settings.AUDIO_MODEL_ID,
            fallback_active=fallback_active,
            completed_at=datetime.now(timezone.utc),
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Audio analysis failed for job %s", job_id)
        await audio_job_store.update_job(
            job_id,
            status=JobStatus.failed,
            error=str(exc),
            completed_at=datetime.now(timezone.utc),
        )
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
