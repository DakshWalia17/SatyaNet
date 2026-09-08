"""
Synthetic speech / voice-clone detector.

Same design pattern as app/ml/deepfake_model.py: every other module talks
to this file through `predict_segment()` and `generate_mel_spectrogram_png()`
only, so the underlying checkpoint is swappable via the
AUDIO_MODEL_ID env var without touching pipeline/routing code.

Model choice rationale (CPU-only HF Spaces free tier):
  - wav2vec2-based spoof/deepfake-speech classifiers are the standard
    lightweight approach and run at a few hundred ms per ~4s clip on CPU.
  - Long recordings are split into fixed-length segments (see
    config.AUDIO_SEGMENT_SECONDS) and scores are aggregated, same idea as
    frame-sampling for video.
  - Default: MelodyMachine/Deepfake-audio-detection-V2 (wav2vec2-family,
    binary bona-fide/spoof classification). Swap via AUDIO_MODEL_ID.
"""
import base64
import io
import logging
import threading
from dataclasses import dataclass, field

try:
    import numpy as np
except ImportError:
    np = None
from PIL import Image

from app.config import settings

logger = logging.getLogger("aimd.ml.audio")

_model_lock = threading.Lock()
_pipeline = None
_load_failed_reason: str | None = None


@dataclass
class SegmentPrediction:
    synthetic_probability: float  # 0.0 (authentic) - 1.0 (synthetic/cloned)
    label: str
    signals: dict = field(default_factory=dict)


def _load_pipeline():
    global _pipeline, _load_failed_reason
    with _model_lock:
        if _pipeline is not None or _load_failed_reason is not None:
            return
        try:
            from transformers import pipeline  # heavy import, deferred

            _pipeline = pipeline(
                "audio-classification",
                model=settings.AUDIO_MODEL_ID,
                device=-1,  # CPU
            )
            logger.info("Loaded audio deepfake model: %s", settings.AUDIO_MODEL_ID)
        except Exception as exc:  # noqa: BLE001 - degrade, don't crash
            _load_failed_reason = str(exc)
            logger.error(
                "Failed to load audio model %s: %s. Falling back to mock "
                "inference so the API stays usable during development.",
                settings.AUDIO_MODEL_ID,
                exc,
            )


def _mock_predict(samples: np.ndarray, sample_rate: int) -> SegmentPrediction:
    """
    Placeholder used only when the real model can't be loaded. Uses crude
    signal statistics (spectral flatness proxy via zero-crossing rate
    variance) purely so the rest of the pipeline is testable — never treat
    this as a real voice-clone detector.
    """
    if samples.size == 0:
        return SegmentPrediction(synthetic_probability=0.5, label="unknown")
    zero_crossings = np.mean(np.abs(np.diff(np.sign(samples))) > 0)
    synthetic_probability = float(np.clip(zero_crossings * 2.0, 0.05, 0.95))
    return SegmentPrediction(
        synthetic_probability=synthetic_probability,
        label="synthetic" if synthetic_probability > 0.5 else "authentic",
        signals={"note": "MOCK MODEL — real classifier failed to load"},
    )


def predict_segment(samples: np.ndarray, sample_rate: int) -> SegmentPrediction:
    """Run the classifier on one audio segment (numpy float32 array)."""
    _load_pipeline()

    if _pipeline is None:
        return _mock_predict(samples, sample_rate)

    try:
        results = _pipeline({"array": samples, "sampling_rate": sample_rate})
        top = max(results, key=lambda r: r["score"])
        spoof_entries = [
            r for r in results
            if r["label"].lower() in ("spoof", "fake", "synthetic", "cloned")
        ]
        synthetic_probability = (
            spoof_entries[0]["score"] if spoof_entries
            else (top["score"] if top["label"].lower() not in ("bona-fide", "real", "authentic") else 1.0 - top["score"])
        )
        return SegmentPrediction(
            synthetic_probability=float(synthetic_probability),
            label=top["label"],
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Audio inference failed on segment, falling back to mock: %s", exc)
        return _mock_predict(samples, sample_rate)


def generate_mel_spectrogram_png(samples: np.ndarray, sample_rate: int) -> str | None:
    """
    Returns a base64-encoded grayscale PNG of the log-Mel spectrogram for
    the frontend's spectrogram viewer panel. Uses torchaudio if available
    (matches the model's own feature extraction), falling back to a plain
    numpy STFT-based spectrogram so this never blocks the pipeline on a
    missing optional dependency.
    """
    try:
        mel_db = _mel_spectrogram_torchaudio(samples, sample_rate)
    except Exception as exc:  # noqa: BLE001
        logger.warning("torchaudio mel-spectrogram unavailable (%s), using numpy fallback.", exc)
        mel_db = _spectrogram_numpy_fallback(samples, sample_rate)

    if mel_db is None or mel_db.size == 0:
        return None

    # Clip to a fixed dB range below the peak (standard spectrogram display
    # convention) instead of raw min-max, otherwise noise-floor variation
    # washes out contrast and the tonal content becomes invisible.
    top_db = 80.0
    peak = mel_db.max()
    mel_db = np.clip(mel_db, peak - top_db, peak)
    normalized = (mel_db - mel_db.min()) / ((mel_db.max() - mel_db.min()) + 1e-6)
    img_array = (normalized * 255).astype(np.uint8)
    # Flip vertically so low frequencies render at the bottom, as is convention.
    img_array = np.flipud(img_array)

    image = Image.fromarray(img_array, mode="L")
    max_width = 1000
    if image.width > max_width:
        scale = max_width / image.width
        image = image.resize((max_width, max(1, int(image.height * scale))))

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _mel_spectrogram_torchaudio(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    import torch
    import torchaudio

    waveform = torch.from_numpy(samples).float().unsqueeze(0)
    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=sample_rate, n_mels=128, n_fft=1024, hop_length=256
    )
    mel = mel_transform(waveform)
    mel_db = torchaudio.transforms.AmplitudeToDB()(mel)
    return mel_db.squeeze(0).numpy()


def _spectrogram_numpy_fallback(samples: np.ndarray, sample_rate: int, n_fft: int = 1024, hop: int = 256) -> np.ndarray:
    if samples.size < n_fft:
        samples = np.pad(samples, (0, n_fft - samples.size))
    window = np.hanning(n_fft)
    n_frames = 1 + (len(samples) - n_fft) // hop
    spec = np.empty((n_fft // 2 + 1, max(n_frames, 1)))
    for i in range(n_frames):
        start = i * hop
        frame = samples[start:start + n_fft] * window
        mag = np.abs(np.fft.rfft(frame))
        spec[:, i] = mag
    return 20 * np.log10(spec + 1e-6)


def model_health() -> dict:
    _load_pipeline()
    return {
        "model_id": settings.AUDIO_MODEL_ID,
        "loaded": _pipeline is not None,
        "fallback_active": _pipeline is None,
        "load_error": _load_failed_reason,
    }
