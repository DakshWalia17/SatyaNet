# AIMD Backend (`apps/api`)

FastAPI backend for the AI Media Investigation, Detection & Origin Tracing
Platform — the **detection engine** only. Covers `/analyze/media`,
`/analyze/audio`, and the Section 65B certificate generator
(`/cases/{id}/pdf`). Live RTSP monitoring was deliberately dropped from
this build (see "Why RTSP was dropped" below) to keep the service a clean
one-shot request/response API, which matters for the deployment target.

## What's implemented

- **Auth:** shared-secret `X-AUTH-TOKEN` header, checked on every `/api/v1/*` route.
- **CORS:** configurable allow-list for the frontend origin.
- **`POST /api/v1/analyze/media`**: image/video upload -> SHA-256 hash ->
  frame-sampled deepfake classification -> background job, poll
  `GET /api/v1/analyze/media/{job_id}` for the result.
- **`POST /api/v1/analyze/audio`**: audio OR video upload (audio track
  extracted via FFmpeg either way) -> segmented synthetic-voice
  classification -> background job, poll
  `GET /api/v1/analyze/audio/{job_id}` for the result + a Mel-spectrogram
  PNG for the frontend's inspector panel.
- **`GET /api/v1/cases/{case_id}/pdf`**: generates a Section 65B DRAFT
  certificate PDF (ReportLab) for one or both of a completed media/audio
  job, with a real chain-of-custody re-hash check at generation time.
- **Swappable models**: `app/ml/deepfake_model.py` and
  `app/ml/audio_model.py` are the only places that know which HF
  checkpoint is loaded (`DEEPFAKE_MODEL_ID` / `AUDIO_MODEL_ID` env vars) —
  everything else calls `predict_frame()` / `predict_segment()`.
- **Graceful degradation**: if a real model fails to load, the API falls
  back to a clearly-labeled mock inference path instead of crashing.
  `/health` reports `fallback_active` per model — check this after every
  deploy.

## Why RTSP was dropped

Live camera monitoring needs a persistent background process holding an
open connection indefinitely. That's fundamentally incompatible with
Render's free tier, which spins the container down after 15 minutes of no
incoming HTTP traffic — it has no way to know your RTSP thread is still
working, since it only watches for requests. Rather than ship a feature
that silently dies in your actual deployment environment, it's cut from
this build. It can come back later against a plan/host that supports
always-on processes (Render's paid tier, or a small VM), as a genuinely
separate service — the frontend/extension work already done doesn't
depend on it.

## Project layout

```
app/
  main.py              # FastAPI app, CORS, router wiring, /health
  config.py            # env-var driven settings
  auth.py              # X-AUTH-TOKEN dependency
  models/schemas.py    # Pydantic request/response models
  routers/
    analyze.py         # /analyze/media + /analyze/audio
    cases.py           # /cases/{id}/pdf — Section 65B certificate
  services/
    job_store.py          # in-memory async job store for media jobs
    audio_job_store.py     # in-memory async job store for audio jobs
    upload_store.py         # shared: where uploaded evidence files live + how to find them
    hashing.py              # SHA-256 utilities
    media_pipeline.py       # orchestrates hash -> extract -> infer -> aggregate (video/image)
    audio_extraction.py     # FFmpeg wrapper: any file -> mono 16kHz WAV
    audio_pipeline.py       # orchestrates hash -> extract -> segment -> infer -> aggregate (audio)
    certificate.py           # ReportLab Section 65B certificate builder
  ml/
    deepfake_model.py    # media model loading + inference + (stubbed) Grad-CAM
    audio_model.py        # audio model loading + inference + Mel-spectrogram PNG generation
```

## Running locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in API_AUTH_TOKEN at minimum
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive Swagger UI. Every
`/api/v1/*` request needs an `X-AUTH-TOKEN` header matching
`API_AUTH_TOKEN` in `.env`. `/health` is unauthenticated (needed for
Render's health checks).

## Deploying to Render

1. Push this `apps/api` directory to a GitHub repo.
2. In the Render dashboard: **New +** -> **Blueprint**, point it at the
   repo. Render reads `render.yaml` (included) and provisions the service
   automatically.
3. On first deploy, Render will prompt for the secrets marked
   `sync: false` in `render.yaml`: `API_AUTH_TOKEN` (generate with
   `openssl rand -hex 32`), `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`.
4. Once live, update `ALLOWED_ORIGINS` in the Render dashboard to your
   real frontend URL and redeploy.
5. `curl https://<your-service>.onrender.com/health` — confirm
   `fallback_active: false` for both models.

**Free-tier reality check:** the service sleeps after 15 minutes of no
requests and takes 30-60s to wake up on the next one. That's fine for a
demo, a college submission, or low-traffic real use — annoying but not
broken. If Chandigarh Police actually puts this into daily operational
use, upgrade to Render's Starter plan ($7/mo) for always-on, no cold
starts.

## Certificate framing (please read before deploying this module)

Section 65B of the Indian Evidence Act requires a human declarant — the
certifying officer — to personally attest to the matters in the
certificate. This system generates a **draft** populated with real
chain-of-custody data (hashes, timestamps, model version, analysis
results), but:

- It is not legal advice, and the exact certificate language required can
  vary by court/proceeding — check with your department's legal cell.
- The PDF includes an explicit disclaimer paragraph and a signature block;
  it has no evidentiary standing until the named officer reviews it for
  accuracy and signs it.
- `case_id` is currently an officer-supplied string (e.g. an FIR number),
  not looked up from a database — see `app/routers/cases.py` for why.

## Known gaps / next steps (intentional, not oversights)

1. **Grad-CAM heatmaps (media) are stubbed.** `_grad_cam_heatmap()` returns
   `None` until a `target_layer` is picked for whichever model checkpoint
   you settle on — this is architecture-specific and shouldn't be faked.
2. **Job stores are in-memory** (one for media jobs, one for audio jobs).
   Fine for a single Render instance; move both to Supabase tables before
   running multiple instances or needing persistence across restarts/deploys
   (Render's free tier disk is ephemeral — a redeploy wipes it).
3. **Mock inference fallback must not ship silently to production.**
   `/health` reports `fallback_active: true/false` for both models — wire
   an alert or a startup check that refuses to serve traffic if either
   real model failed to load, before this touches real case data.
4. **No per-officer auth yet** — current auth is a single shared token
   suitable for trusted internal clients (extension, bot, frontend server).
   Add Supabase Auth / JWT verification before this touches real
   investigations.
5. **Audio segment length is fixed** (`AUDIO_SEGMENT_SECONDS`, default 4s)
   rather than adaptive to the model's ideal input window.
6. **Evidence files live on ephemeral disk**, same caveat as #2 — migrate
   uploads to a Supabase Storage bucket before relying on the
   chain-of-custody re-hash check across a redeploy.
7. **RTSP live monitoring was cut** — see "Why RTSP was dropped" above.

## Testing notes

The full pipeline (upload → hash → background job → status poll) was
exercised end-to-end with FastAPI's `TestClient` for both media and audio,
including auth rejection and failure paths. The certificate generator was
tested by running real jobs to completion, generating a combined
certificate PDF, and verifying it with `pypdf`/`pdf2image` — confirming
the SHA-256 integrity check matches, forensic signal tables render
correctly, and the missing-evidence-file path reports "UNAVAILABLE" rather
than crashing or fabricating a match.

Model-specific inference (the actual HF classifiers) hasn't been exercised
against real weights in this build environment (no outbound access to
Hugging Face) — the code path is correct and covered by the mock-fallback
tests, but confirm `fallback_active: false` on `/health` immediately after
your first real deploy.
