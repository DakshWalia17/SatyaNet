from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────

class MediaType(str, Enum):
    image = "image"
    video = "video"


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ThreatLevel(str, Enum):
    authentic = "authentic"      # green
    tampered = "tampered"        # amber - inconclusive / edited but not necessarily AI-gen
    deepfake = "deepfake"        # red


class VoiceAuthenticity(str, Enum):
    authentic = "authentic"    # green - natural human speech
    inconclusive = "inconclusive"  # amber - mixed/ambiguous signal
    synthetic = "synthetic"    # red - AI-generated / cloned voice


class DomainStatus(str, Enum):
    safe = "SAFE"
    suspicious = "SUSPICIOUS"
    malicious = "MALICIOUS"


class CaseStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


# ──────────────────────────────────────────────────────────
# Shared sub-models
# ──────────────────────────────────────────────────────────

class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class HeatmapRegion(BaseModel):
    """A single Grad-CAM activation region for the frontend heatmap overlay."""
    frame_index: int
    box: BoundingBox
    intensity: float = Field(..., ge=0.0, le=1.0)


class ForensicSignal(BaseModel):
    """One row in the Forensic Signal Matrix panel."""
    name: str
    score: float = Field(..., ge=0.0, le=1.0)
    description: str


# ──────────────────────────────────────────────────────────
# Media analysis response
# ──────────────────────────────────────────────────────────

class AnalyzeMediaResponse(BaseModel):
    job_id: str
    case_id: Optional[str] = None
    status: JobStatus
    original_filename: Optional[str] = None
    media_type: Optional[MediaType] = None
    file_url: Optional[str] = None
    sha256_original: Optional[str] = None
    threat_level: Optional[ThreatLevel] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    forensic_signals: list[ForensicSignal] = []
    heatmap_regions: list[HeatmapRegion] = []
    frames_analyzed: Optional[int] = None
    model_version: Optional[str] = None
    fallback_active: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    disclaimer: str = (
        "This result is a probabilistic AI assessment and is NOT definitive "
        "proof of media authenticity or manipulation. It must be corroborated "
        "by human forensic review before use as evidence."
    )


class MediaAnalysisResult(BaseModel):
    """
    Standard hackathon & portal media analysis result schema.
    Computes cryptographic SHA-256 and returns real integrity metrics
    combined with high-impact mock origin metadata.
    """
    status: str = "success"
    file_name: str
    sha256_hash: str
    ai_probability_score: float = Field(default=0.94, ge=0.0, le=1.0)
    verdict: str = "HIGH RISK: Synthetic Media Detected"
    suspected_engine: str = "ElevenLabs v2 / Stable Diffusion XL (Mock Origin Trace)"
    timestamp: str
    job_id: Optional[str] = None
    media_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    forensic_details: Optional[dict] = None


# ──────────────────────────────────────────────────────────
# Audio analysis response
# ──────────────────────────────────────────────────────────

class AnalyzeAudioResponse(BaseModel):
    job_id: str
    case_id: Optional[str] = None
    status: JobStatus
    original_filename: Optional[str] = None
    file_url: Optional[str] = None
    sha256_original: Optional[str] = None
    voice_authenticity: Optional[VoiceAuthenticity] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    forensic_signals: list[ForensicSignal] = []
    duration_seconds: Optional[float] = None
    sample_rate_hz: Optional[int] = None
    # Base64-encoded PNG of the Mel-spectrogram, for the frontend's
    # spectrogram viewer panel. None until the job completes.
    mel_spectrogram_png_base64: Optional[str] = None
    mel_spectrogram_url: Optional[str] = None
    segments_analyzed: Optional[int] = None
    model_version: Optional[str] = None
    fallback_active: bool = False
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    disclaimer: str = (
        "This result is a probabilistic AI assessment and is NOT definitive "
        "proof that a voice is or is not AI-generated/cloned. It must be "
        "corroborated by human forensic and audio expert review before use "
        "as evidence."
    )


# ──────────────────────────────────────────────────────────
# Cases
# ──────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    """Request body for creating a new case."""
    officer_id: str = Field(..., description="Badge ID or Supabase user ID of the officer.")
    title: str = Field(..., min_length=1, max_length=500, description="Case title / FIR description.")


class CaseResponse(BaseModel):
    """Response for a single case."""
    case_id: str
    officer_id: str
    title: str
    status: CaseStatus = CaseStatus.open
    created_at: datetime
    media_jobs: list[AnalyzeMediaResponse] = []
    audio_jobs: list[AnalyzeAudioResponse] = []


class CaseListItem(BaseModel):
    """Lightweight case item for list endpoints."""
    case_id: str
    officer_id: str
    title: str
    status: CaseStatus
    created_at: datetime


# ──────────────────────────────────────────────────────────
# Chrome Extension — Media Scan
# ──────────────────────────────────────────────────────────

class ExtensionScanRequest(BaseModel):
    """Request body for the quick media scan endpoint."""
    url: str = Field(..., description="Public URL of an image or video to scan.")


class ExtensionScanResponse(BaseModel):
    """Light verdict payload for the Chrome Extension popup."""
    url: str
    verdict: Optional[ThreatLevel] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    threat_level: str = "unknown"
    fallback_active: bool = False
    sha256: Optional[str] = None
    error: Optional[str] = None


# ──────────────────────────────────────────────────────────
# Chrome Extension — Phishing / Domain Check
# ──────────────────────────────────────────────────────────

class PhishingCheckRequest(BaseModel):
    """Request body for the domain reputation check endpoint."""
    url: str = Field(..., description="Full URL of the page to check (domain is extracted).")


class PhishingCheckResponse(BaseModel):
    """Domain reputation result for the Chrome Extension."""
    domain: str
    status: DomainStatus = DomainStatus.safe
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    domain_age_days: Optional[int] = None
    warning_tags: list[str] = []
    report_summary: str = ""
    cached: bool = False


# ──────────────────────────────────────────────────────────
# Telegram Bot
# ──────────────────────────────────────────────────────────

class TelegramVerdictResponse(BaseModel):
    """Structured verdict returned internally before formatting for the Telegram user."""
    job_id: str
    media_type: str  # "image", "video", "audio"
    verdict: str  # Human-readable emoji verdict string
    confidence: Optional[float] = None
    fallback_active: bool = False
