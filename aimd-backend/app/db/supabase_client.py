"""
Supabase client singleton.

Provides a single shared Supabase client instance for the entire application.
Uses the service-role key (not the anon key) so all operations bypass RLS —
this backend is the only actor that talks to Supabase, never the browser
directly.
"""
import logging
from typing import Any

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = Any  # type: ignore

from app.config import settings

logger = logging.getLogger("aimd.db")

_client: Any = None


def get_supabase() -> Any:
    """Return the application-wide Supabase client, creating it on first call."""
    global _client
    if _client is None:
        if not create_client:
            raise RuntimeError("supabase package is not installed.")
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in the "
                "environment. See .env.example."
            )
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        logger.info("Supabase client initialized for %s", settings.SUPABASE_URL)
    return _client


def storage_client():
    """Shortcut to the Supabase Storage client for bucket operations."""
    return get_supabase().storage


async def check_supabase_health() -> dict:
    """
    Lightweight health check called at application startup.
    Attempts a trivial query to verify connectivity.
    """
    try:
        client = get_supabase()
        # A simple select to verify the connection is alive.
        # This will fail if the table doesn't exist yet, which is fine —
        # we catch and report that as a warning, not an error.
        result = client.table("media_jobs").select("job_id").limit(1).execute()
        return {"supabase": "connected", "url": settings.SUPABASE_URL}
    except RuntimeError as exc:
        # Missing credentials — expected in dev if .env isn't filled in yet.
        logger.warning("Supabase not configured: %s", exc)
        return {"supabase": "not_configured", "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        logger.warning("Supabase health check failed: %s", exc)
        return {"supabase": "error", "error": str(exc)}
