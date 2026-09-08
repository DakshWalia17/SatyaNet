"""
Central configuration for AIMD backend.
All values are read from environment variables so nothing sensitive
is hardcoded. Copy .env.example to .env and fill in real values.

Uses pydantic-settings for typed, validated configuration with automatic
.env loading.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and/or a .env file.
    pydantic-settings handles type coercion, validation, and .env loading
    automatically — no manual os.getenv() calls needed.
    """

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # --- Security ---
    # Legacy shared-secret token (deprecated — use Supabase JWT or API Key).
    API_AUTH_TOKEN: str = ""

    # Supabase JWT secret for verifying police dashboard JWTs.
    # Typically the same as the Supabase project JWT secret found in
    # Settings → API → JWT Settings in the Supabase dashboard.
    SUPABASE_JWT_SECRET: str = ""

    # Comma-separated API keys for trusted automated clients
    # (Telegram Bot backend, Chrome Extension).
    EXTENSION_API_KEYS: list[str] = Field(default_factory=list)

    # --- Paths & Directories ---
    EXTENSION_ZIP_PATH: str = "static/extension.zip"
    EVIDENCE_UPLOAD_DIR: str = "evidence_uploads"


    # --- Developer & System ---
    DEVELOPER: str = "Daksh Walia, B.Tech AIML"
    SYSTEM_NAME: str = "Chandigarh Police Cyber Cell Backend"

    # --- CORS ---
    # Wildcard enabled for Vercel frontend, Telegram bot, Chrome extension
    ALLOWED_ORIGINS: list[str] = Field(
        default=["*"],
    )

    # --- Supabase ---
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_MEDIA_BUCKET: str = "evidence-files"

    # --- HuggingFace ---
    HF_API_TOKEN: str = ""

    # --- Deepfake Model ---
    # HF model repo id for the deepfake classifier. Swappable without code changes.
    DEEPFAKE_MODEL_ID: str = "prithivMLmods/Deep-Fake-Detector-v2-Model"
    # Run inference on every Nth frame of a video (CPU budget control).
    VIDEO_FRAME_SAMPLE_RATE: int = 10
    # Hard cap on frames analyzed per video, regardless of length.
    MAX_FRAMES_PER_VIDEO: int = 60

    # --- Audio Model ---
    # HF model repo id for the synthetic-speech / voice-clone classifier.
    AUDIO_MODEL_ID: str = "MelodyMachine/Deepfake-audio-detection-V2"
    # Split audio into fixed-length segments for classification (seconds).
    AUDIO_SEGMENT_SECONDS: float = 4.0
    # Hard cap on segments analyzed per file, regardless of length.
    MAX_AUDIO_SEGMENTS: int = 30

    # --- Telegram Bot ---
    TELEGRAM_BOT_TOKEN: str = ""

    # --- External APIs ---
    VIRUSTOTAL_API_KEY: str = ""
    GOOGLE_SAFE_BROWSING_KEY: str = ""

    # --- Misc ---
    ENVIRONMENT: str = "development"
    MAX_UPLOAD_SIZE_MB: int = 100


settings = Settings()
