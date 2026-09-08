"""
AIMD Backend Engine — Chandigarh Police Cyber Cell Portal
AI Media Detection, Origin Tracing & Section 65B Certificate Generation Platform

Developer: Daksh Walia, B.Tech AIML
Institution: Chandigarh Police Cyber Crime Cell
Structured for Render & Railway Production Deployment
"""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import analyze, cases, extension

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("aimd.main")

app = FastAPI(
    title="AIMD — Chandigarh Police Cyber Cell Portal",
    description=(
        "AI Media Investigation, Detection & Origin Tracing Platform backend engine. "
        "Engineered for deepfake forensics, synthetic voice detection, "
        "cryptographic SHA-256 chain of custody, and Section 65B Indian Evidence Act certification."
    ),
    version="1.0.0",
    contact={
        "name": "Daksh Walia, B.Tech AIML",
        "url": "https://github.com",
    },
)

# ──────────────────────────────────────────────────────────
# CORS Configuration (Fully enabled for Vercel, Extension, Telegram)
# ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────
# Developer & Context Headers Middleware
# ──────────────────────────────────────────────────────────
@app.middleware("http")
async def add_developer_and_security_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Developer context and system branding
    response.headers["X-Developer"] = "Daksh Walia, B.Tech AIML"
    response.headers["X-System"] = "Chandigarh Police Cyber Cell Backend"
    response.headers["X-Platform"] = "AIMD Forensics & Origin Tracing"
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response


# ──────────────────────────────────────────────────────────
# Routers
# ──────────────────────────────────────────────────────────
app.include_router(analyze.router)
app.include_router(cases.router)
app.include_router(extension.router)
# Include the new evidence router
from app.routers import evidence
app.include_router(evidence.router)

# Create evidence upload directory on startup
@app.on_event("startup")
async def create_evidence_dir():
    import os
    os.makedirs(settings.EVIDENCE_UPLOAD_DIR, exist_ok=True)
    # Ensure directory is writable initially; files will be set read‑only after save



# ──────────────────────────────────────────────────────────
# Core Endpoints
# ──────────────────────────────────────────────────────────
@app.get(
    "/health",
    summary="Health Check Endpoint",
    description="Returns official health and operational readiness status for Chandigarh Police Cyber Cell backend.",
)
async def health():
    """
    Health Check Endpoint returning exact production readiness status.
    """
    return {
        "status": "online",
        "system": "Chandigarh Police Cyber Cell Backend",
        "mode": "production_ready",
    }


@app.get(
    "/",
    summary="Root Service Index",
    description="Index endpoint providing portal status, developer attribution, and documentation references.",
)
async def root():
    return {
        "status": "online",
        "system": "Chandigarh Police Cyber Cell Backend",
        "portal": "AIMD — AI Media Detection & Origin Tracing Platform",
        "developer": "Daksh Walia, B.Tech AIML",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "version": "1.0.0",
    }
