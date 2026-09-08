"""
Authentication & authorization for AIMD backend.

Supports three auth mechanisms, tried in order by `verify_any_auth()`:

1. **Supabase JWT** (Authorization: Bearer <token>)
   - For the Police Dashboard (React). Verifies the JWT signature using
     the Supabase project's JWT secret and extracts the officer's user ID.

2. **API Key** (X-API-KEY: <key>)
   - For trusted automated clients: Telegram Bot backend, Chrome Extension.
     Keys are configured via the EXTENSION_API_KEYS env var.

3. **Legacy shared token** (X-AUTH-TOKEN: <token>) — DEPRECATED
   - The original single shared secret. Kept for backward compatibility
     during the migration period. Logs a deprecation warning on every use.
"""
import logging
from dataclasses import dataclass
from typing import Optional

try:
    import jwt
except ImportError:
    jwt = None

from fastapi import Header, HTTPException, Request, status

from app.config import settings

logger = logging.getLogger("aimd.auth")


# ──────────────────────────────────────────────────────────
# Auth result types
# ──────────────────────────────────────────────────────────

@dataclass
class AuthenticatedUser:
    """Result of successful Supabase JWT verification."""
    user_id: str
    role: str = "authenticated"
    email: Optional[str] = None


@dataclass
class APIKeyClient:
    """Result of successful API key verification."""
    client_type: str = "api_key"


@dataclass
class LegacyTokenClient:
    """Result of successful legacy token verification (deprecated)."""
    client_type: str = "legacy_token"


# ──────────────────────────────────────────────────────────
# Individual auth verifiers
# ──────────────────────────────────────────────────────────

async def verify_supabase_jwt(
    authorization: str = Header(default=""),
) -> AuthenticatedUser:
    """
    Verify a Supabase-issued JWT from the Authorization header.
    Expected format: "Bearer <jwt_token>"
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header. Expected: Bearer <token>",
        )

    token = authorization.removeprefix("Bearer ").strip()

    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server JWT secret is not configured.",
        )

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT has expired.",
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid JWT: {exc}",
        )

    return AuthenticatedUser(
        user_id=payload.get("sub", ""),
        role=payload.get("role", "authenticated"),
        email=payload.get("email"),
    )


async def verify_api_key(
    x_api_key: str = Header(default=""),
) -> APIKeyClient:
    """
    Verify an API key from the X-API-KEY header against the configured
    list of trusted keys.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-KEY header.",
        )
    if not settings.EXTENSION_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No API keys are configured on the server.",
        )
    if x_api_key not in settings.EXTENSION_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return APIKeyClient()


async def verify_auth_token(
    x_auth_token: str = Header(default=""),
) -> LegacyTokenClient:
    """
    DEPRECATED — Legacy shared-secret auth.
    If not configured on the server, permits access in dev/demo mode with a warning.
    """
    if not settings.API_AUTH_TOKEN:
        logger.debug("API_AUTH_TOKEN not set; allowing unauthenticated request in dev/demo mode.")
        return LegacyTokenClient()

    if x_auth_token != settings.API_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-AUTH-TOKEN header.",
        )
    return LegacyTokenClient()


# ──────────────────────────────────────────────────────────
# Unified auth dependency (tries all methods)
# ──────────────────────────────────────────────────────────

async def verify_any_auth(
    request: Request,
    authorization: str = Header(default=""),
    x_api_key: str = Header(default=""),
    x_auth_token: str = Header(default=""),
) -> AuthenticatedUser | APIKeyClient | LegacyTokenClient:
    """
    Unified auth dependency that tries (in order):
      1. Supabase JWT (Authorization: Bearer ...)
      2. API Key (X-API-KEY: ...)
      3. Legacy shared token (X-AUTH-TOKEN: ...)

    Returns the first successful auth result. Raises 401 if all fail.
    """
    errors = []

    # 1. Try Supabase JWT
    if authorization.startswith("Bearer "):
        try:
            return await verify_supabase_jwt(authorization)
        except HTTPException as exc:
            errors.append(f"JWT: {exc.detail}")

    # 2. Try API Key
    if x_api_key:
        try:
            return await verify_api_key(x_api_key)
        except HTTPException as exc:
            errors.append(f"API Key: {exc.detail}")

    # 3. Try legacy token
    if x_auth_token:
        try:
            return await verify_auth_token(x_auth_token)
        except HTTPException as exc:
            errors.append(f"Legacy token: {exc.detail}")

    # Nothing worked
    if errors:
        detail = "Authentication failed: " + "; ".join(errors)
    else:
        detail = (
            "No authentication credentials provided. "
            "Include one of: Authorization (Bearer JWT), X-API-KEY, or X-AUTH-TOKEN header."
        )
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
