"""
Comprehensive Verification Test Suite for AIMD Backend
Developer: Daksh Walia, B.Tech AIML
"""
import hashlib
import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    print("\n--- 1. Testing GET /health ---")
    response = client.get("/health")
    print("Status:", response.status_code)
    data = response.json()
    print("Response payload:", data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert data["status"] == "online", f"Expected 'online', got {data['status']}"
    assert data["system"] == "Chandigarh Police Cyber Cell Backend", f"Unexpected system: {data['system']}"
    assert data["mode"] == "production_ready", f"Unexpected mode: {data['mode']}"
    print("  Headers received:")
    print("  X-Developer:", response.headers.get("x-developer"))
    print("  X-System:", response.headers.get("x-system"))
    assert response.headers.get("x-developer") == "Daksh Walia, B.Tech AIML"
    print("  -> PASSED: /health matches exact contract and developer headers.")

def test_root():
    print("\n--- 2. Testing GET / ---")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print("Root data:", data)
    assert "Chandigarh Police" in data["system"]
    assert data["developer"] == "Daksh Walia, B.Tech AIML"
    print("  -> PASSED: Root endpoint active.")

def test_analyze_media():
    print("\n--- 3. Testing POST /api/v1/analyze/media ---")
    sample_content = b"CHANDIGARH_POLICE_CYBER_CELL_EVIDENCE_SAMPLE_BYTES_2026"
    expected_hash = hashlib.sha256(sample_content).hexdigest()
    filename = "suspect_deepfake_evidence.png"

    files = {
        "file": (filename, io.BytesIO(sample_content), "image/png")
    }

    response = client.post("/api/v1/analyze/media", files=files)
    print("Status:", response.status_code)
    data = response.json()
    print("Response payload:")
    for k, v in data.items():
        print(f"  {k}: {v}")

    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["file_name"] == filename
    assert data["sha256_hash"] == expected_hash
    assert data["ai_probability_score"] == 0.94
    assert data["verdict"] == "HIGH RISK: Synthetic Media Detected"
    assert data["suspected_engine"] == "ElevenLabs v2 / Stable Diffusion XL (Mock Origin Trace)"
    assert "timestamp" in data
    assert "job_id" in data
    print("  -> PASSED: POST /api/v1/analyze/media matches exact output specification & computed SHA-256!")
    return data["job_id"]

def test_section_65b_pdf(job_id):
    print("\n--- 4. Testing Section 65B PDF Generation with Job ID ---")
    url = f"/api/v1/cases/FIR-2026-CHD-098/pdf?officer_badge_id=CHD-POL-4412&media_job_id={job_id}&officer_name=Inspector+Rajesh+Kumar"
    response = client.get(url)
    print("PDF Status:", response.status_code)
    print("Content-Type:", response.headers.get("content-type"))
    print("Content-Disposition:", response.headers.get("content-disposition"))
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert response.content.startswith(b"%PDF")
    print(f"  -> Generated {len(response.content)} bytes of Section 65B Electronic Evidence PDF!")
    print("  -> PASSED: Section 65B Court Certificate generated successfully.")

def test_extension_domain_check():
    print("\n--- 5. Testing Chrome Extension Phishing Domain Check ---")
    payload = {"url": "https://fake-chandigarh-police-challan.xyz"}
    response = client.post("/api/v1/extension/check-domain", json=payload)
    print("Status:", response.status_code)
    data = response.json()
    print("Phishing check response:", data)
    assert response.status_code == 200
    assert data["status"] in ("MALICIOUS", "SUSPICIOUS")
    print("  -> PASSED: Extension domain check verified.")

def test_analyze_audio():
    print("\n--- 6. Testing POST /api/v1/analyze/audio ---")
    sample_audio = b"RIFF....WAVEfmt ....data....FAKE_VOICE_SAMPLE_CHANDIGARH"
    files = {"file": ("deepfake_call_recording.wav", io.BytesIO(sample_audio), "audio/wav")}
    response = client.post("/api/v1/analyze/audio", files=files)
    print("Audio Status:", response.status_code)
    data = response.json()
    assert response.status_code == 200
    assert data["status"] == "completed"
    assert data["voice_authenticity"] == "synthetic"
    assert data["confidence_score"] >= 0.90
    print("  -> PASSED: POST /api/v1/analyze/audio successfully identified synthetic voice!")

def test_cors():
    print("\n--- 7. Testing CORS Wildcard Headers ---")
    response = client.options("/health", headers={
        "Origin": "https://aimd-cybercell.vercel.app",
        "Access-Control-Request-Method": "GET"
    })
    print("CORS response headers:")
    print("  access-control-allow-origin:", response.headers.get("access-control-allow-origin"))
    assert response.headers.get("access-control-allow-origin") in ("*", "https://aimd-cybercell.vercel.app")
    assert response.headers.get("access-control-allow-credentials") == "true"
    print("  -> PASSED: Wildcard / reflective CORS with credentials enabled for Vercel, Telegram, Extension.")

if __name__ == "__main__":
    test_health()
    test_root()
    job_id = test_analyze_media()
    test_section_65b_pdf(job_id)
    test_extension_domain_check()
    test_analyze_audio()
    test_cors()
    print("\n=======================================================")
    print(" ALL 7 BACKEND VERIFICATION TESTS PASSED PERFECTLY! ")
    print("=======================================================")
