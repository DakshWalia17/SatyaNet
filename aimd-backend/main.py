"""
AIMD Backend — Chandigarh Police Cyber Cell Portal
Primary Application Entrypoint for Render / Railway / Local Deployment

Developer: Daksh Walia, B.Tech AIML
Institution: Chandigarh Police Cyber Crime Investigation Cell
"""
import os
import uvicorn
from app.main import app

# Expose app object directly for ASGI runners:
# - Render: uvicorn main:app --host 0.0.0.0 --port $PORT
# - Railway: uvicorn main:app --host 0.0.0.0 --port $PORT
# - Docker: uvicorn app.main:app --host 0.0.0.0 --port $PORT

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
