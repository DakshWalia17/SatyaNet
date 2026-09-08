FROM python:3.11-slim

# ffmpeg + libgl1 needed by opencv/video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# EXPOSE is documentation only — actual bind port is driven by $PORT below,
# so this same image works unmodified on Render (which injects PORT) and
# on Hugging Face Spaces / local (which don't, hence the 7860 fallback).
EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
