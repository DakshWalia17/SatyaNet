# 🛡️ SatyaNET — AI Forensic & Tamper-Proof Evidence Ecosystem

> **Empowering Cyber Law Enforcement with Instant Deepfake Detection, Cryptographic Chain of Custody, and BNSS Section 63 Compliance.**

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React%2FVercel-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Container-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![IPFS](https://img.shields.io/badge/Storage-IPFS%20%2F%20Pinata-65C2CB?style=for-the-badge&logo=ipfs&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## 📌 Problem Statement & Solution

With the rapid rise of synthetic media, AI voice clones, and deepfakes, cyber cells face a critical challenge in establishing the **authenticity and chain of custody** for digital evidence.

**SatyaNET** provides an end-to-end legal-forensic pipeline that ingests media from multiple touchpoints (Web Dashboard, Chrome Extension, Telegram Bot), runs multi-modal synthetic analysis, generates SHA-256 forensic fingerprints, pins tamper-proof evidence to IPFS, and generates **BNSS Section 63 compliant electronic certificates**.

---

## 🌟 Key Features

- **🔬 Dynamic Multi-Modal AI Forensics** — Analyzes images, audio, and video to calculate AI probability scores and identify generative engines (ElevenLabs, Midjourney, SDXL, Sora, etc.).
- **📜 Legal Compliance (BNSS 2023 Sec 63)** — Automatically extracts EXIF/media metadata, calculates SHA-256 cryptographic hashes, and logs audit trails for court admissibility.
- **🔗 Immutable IPFS Evidence Vault** — Decentralized pinning via Pinata ensures evidence cannot be modified, deleted, or falsified post-collection.
- **📱 On-Field Telegram Bot** (`@satyanet_forensic_bot`) — Enables field officers to instantly verify photos and documents on mobile phones in real-time.
- **🧩 Inspector Chrome Extension** (Manifest V3) — Allows investigators to audit web-hosted media and deepfakes with a single click while browsing.
- **📊 Central Forensic Web Dashboard** — Provides real-time threat scores, case logs, CID verifications, and downloadable compliance certificates.

---

## 🏗️ System Architecture

```
              [ Field Officer / Investigator ]
                    │        │         │
                    ▼        ▼         ▼
                 Web App  Chrome Ext.  Telegram Bot
                (Vercel)  (Manifest V3) (pyTelegramBotAPI)
                    │        │         │
                    └────────┼─────────┘
                             ▼
                 [ SatyaNET FastAPI Backend ]
                       (Render / Docker)
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
      [ AI Forensic Engine ]   [ Cryptographic Hashing ]
      (Synthetic Analysis)      (SHA-256 & Metadata)
                └────────────┬────────────┘
                             ▼
                   [ Pinata IPFS Vault ]
                  (Immutable Evidence CID)
```

---

## 🛠️ Tech Stack

| Domain | Technology / Tools |
|---|---|
| **Backend** | Python 3.12, FastAPI, Uvicorn, Docker |
| **Frontend** | React, Next.js, Tailwind CSS (deployed on Vercel) |
| **Bot & Extension** | `pyTelegramBotAPI`, Chrome Extension API (Manifest V3) |
| **Storage & Hashing** | IPFS (Pinata pinning service), SHA-256 |
| **Hosting** | Render (backend API), Vercel (web dashboard) |

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.12+
- Node.js & npm (for frontend)
- Docker (optional)

### 1. Backend Setup

```bash
# Clone repository
git clone https://github.com/DakshWalia17/SatyaNet.git
cd SatyaNet

# Install backend dependencies
pip install -r requirements.txt

# Start local server
uvicorn app.main:app --reload --port 7860
```

### 2. Run Telegram Bot (Local Service)

```bash
python bot.py
```

### 3. Load Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (top-right toggle).
3. Click **Load unpacked** and select the `satyanet-extension` folder.

---

## 🔌 Core API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check & system diagnostic |
| `POST` | `/evidence/upload` | Upload media, generate SHA-256, run AI analysis, & pin to IPFS |
| `GET` | `/download-extension` | Downloads the official Chrome Extension ZIP |
| `GET` | `/evidence/file/{job_id}/{filename}` | Retrieves processed evidence artifacts |

---

## 📜 Legal & Compliance

SatyaNET adheres strictly to the evidentiary standards mandated under **Section 63 of the Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023** (formerly Section 65B of the Indian Evidence Act) for the admissibility of electronic records in Indian courts:

- **Hash Verification** — Guarantees data integrity from capture to trial.
- **Device & Audit Logging** — Captures timestamp, device identity, user ID, and source IP.
- **Decentralized Preservation** — IPFS Content Identifiers (CIDs) prevent single-point-of-failure tampering.

---

## 👤 Author & Maintainer

**Daksh Walia**
Student at CGC University Mohali (B.Tech AIML)
GitHub: [@DakshWalia17](https://github.com/DakshWalia17)

*Developed for Police Cyber Cell Forensics & Hackathon Submission.*
