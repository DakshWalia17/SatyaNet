"""
FFmpeg-based audio extraction.

Handles both audio-only uploads (mp3, m4a, wav, ogg...) and video uploads
(mp4, mov...) by pulling the audio track out with the same command, and
normalizes everything to mono 16kHz WAV — the format expected by most
speech/voice-clone classifiers (wav2vec2-family models included).

Uses the `ffmpeg` binary directly via subprocess rather than a Python
wrapper library, since it's already a required system dependency (declared
in the Dockerfile) for video frame extraction too — one less Python
dependency to manage.
"""
import json
import logging
import subprocess

logger = logging.getLogger("aimd.audio_extraction")

TARGET_SAMPLE_RATE = 16000


class AudioExtractionError(Exception):
    pass


def extract_audio_to_wav(input_path: str, output_path: str) -> None:
    """Extract/convert the audio track of `input_path` into a mono 16kHz
    WAV file at `output_path`. Raises AudioExtractionError if the input
    has no audio track or ffmpeg fails for any other reason."""
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i", input_path,
        "-vn",  # drop video stream if present
        "-ac", "1",  # mono
        "-ar", str(TARGET_SAMPLE_RATE),
        "-f", "wav",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg failed: %s", result.stderr[-2000:])
        raise AudioExtractionError(
            "Could not extract an audio track from the uploaded file. "
            "It may not contain audio, or the format is unsupported."
        )


def probe_duration_seconds(path: str) -> float:
    """Read duration via ffprobe. Returns 0.0 if it can't be determined."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return 0.0
    try:
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError):
        return 0.0
