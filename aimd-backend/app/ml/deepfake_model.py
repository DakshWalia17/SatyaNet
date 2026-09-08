"""
Deepfake / manipulated-media classifier wrapper.

Design goal: every other module (routers, services) talks to this file
through `predict_frame()` only. Swapping the underlying model — a different
HF checkpoint, a custom-trained Xception/EfficientNet, or eventually a
proper video-native model — never requires touching the API layer.

Model choice rationale (CPU-only HF Spaces free tier):
  - Full 3D-CNN / video-transformer deepfake models are too slow on CPU.
  - Instead we run a lightweight image classifier per sampled frame
    (see config.VIDEO_FRAME_SAMPLE_RATE) and aggregate scores.
  - Default model: prithivMLmods/Deep-Fake-Detector-v2-Model (ViT-based,
    binary real/fake classification, HF `transformers` compatible).
    Swap via the DEEPFAKE_MODEL_ID env var.
"""
import logging
import threading
from dataclasses import dataclass, field
from typing import Any

try:
    import numpy as np
except ImportError:
    class _MockNp:
        ndarray = Any  # type: ignore
    np = _MockNp()  # type: ignore
from PIL import Image

from app.config import settings

logger = logging.getLogger("aimd.ml")

_model_lock = threading.Lock()
_pipeline = None
_load_failed_reason: str | None = None


@dataclass
class FramePrediction:
    fake_probability: float  # 0.0 (authentic) - 1.0 (deepfake)
    label: str
    heatmap: np.ndarray | None = None  # HxW float array, 0-1, or None if unavailable
    signals: dict = field(default_factory=dict)


def _load_pipeline():
    """Lazily load the HF image-classification pipeline (heavy import)."""
    global _pipeline, _load_failed_reason
    with _model_lock:
        if _pipeline is not None or _load_failed_reason is not None:
            return
        try:
            from transformers import pipeline  # local import: heavy dependency

            _pipeline = pipeline(
                "image-classification",
                model=settings.DEEPFAKE_MODEL_ID,
                device=-1,  # CPU
            )
            logger.info("Loaded deepfake model: %s", settings.DEEPFAKE_MODEL_ID)
        except Exception as exc:  # noqa: BLE001 - we want to degrade, not crash
            _load_failed_reason = str(exc)
            logger.error(
                "Failed to load model %s: %s. Falling back to mock inference "
                "so the API stays usable during development.",
                settings.DEEPFAKE_MODEL_ID,
                exc,
            )


def _mock_predict(image: Image.Image) -> FramePrediction:
    """
    Deterministic-ish placeholder used only when the real model cannot be
    loaded (e.g. no internet access in a dev sandbox). Never ship this as
    the actual production inference path — it exists purely so the rest of
    the pipeline (hashing, job store, PDF, endpoints) can be built and
    tested before the model is wired up in the real deployment environment.
    """
    arr = np.asarray(image.convert("L"), dtype=np.float32) / 255.0
    fake_probability = float(np.clip(arr.std() * 1.5, 0.05, 0.95))
    heatmap = np.abs(arr - arr.mean())
    heatmap_range = heatmap.max() - heatmap.min()
    heatmap = (heatmap - heatmap.min()) / (heatmap_range + 1e-6)
    return FramePrediction(
        fake_probability=fake_probability,
        label="fake" if fake_probability > 0.5 else "real",
        heatmap=heatmap,
        signals={
            "compression_fft_noise": round(float(arr.std()), 3),
            "note": "MOCK MODEL — real classifier failed to load",
        },
    )


def predict_frame(image: Image.Image) -> FramePrediction:
    """Run the classifier on a single PIL image frame."""
    _load_pipeline()

    if _pipeline is None:
        return _mock_predict(image)

    try:
        results = _pipeline(image)  # [{"label": "fake"/"real", "score": float}, ...]
        top = max(results, key=lambda r: r["score"])
        fake_entries = [r for r in results if r["label"].lower() in ("fake", "deepfake", "manipulated")]
        fake_probability = fake_entries[0]["score"] if fake_entries else (
            top["score"] if top["label"].lower() != "real" else 1.0 - top["score"]
        )
        heatmap = _grad_cam_heatmap(image)
        return FramePrediction(
            fake_probability=float(fake_probability),
            label=top["label"],
            heatmap=heatmap,
            signals={},
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Inference failed on frame, falling back to mock: %s", exc)
        return _mock_predict(image)


def _grad_cam_heatmap(image: Image.Image) -> np.ndarray | None:
    """
    Best-effort Grad-CAM heatmap for the Grad-CAM Heatmap Inspector panel.

    NOTE: pytorch-grad-cam needs a concrete target_layer for the loaded
    architecture, which varies per checkpoint. This is a placeholder that
    returns None (frontend should hide the heatmap overlay in that case)
    until a target_layer is wired up for whichever model_id is actually
    deployed. Left as an explicit TODO rather than silently faking data
    that would be shown to an investigating officer.
    """
    # TODO: implement with pytorch-grad-cam once DEEPFAKE_MODEL_ID's
    # architecture (and its final conv/attention layer) is finalized.
    return None


def model_health() -> dict:
    _load_pipeline()
    return {
        "model_id": settings.DEEPFAKE_MODEL_ID,
        "loaded": _pipeline is not None,
        "fallback_active": _pipeline is None,
        "load_error": _load_failed_reason,
    }
