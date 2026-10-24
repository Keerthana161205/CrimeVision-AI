# ⚖️ CrimeVision AI: Intelligent Multimodal Forensic Analysis Platform
> **Skill Wallet Capstone Project 2** | Production-Ready Streamlit Application

CrimeVision AI is an enterprise-grade, multimodal forensic intelligence platform built to accelerate digital criminal investigations. It cross-correlates visual scene evidence, witness audio transcripts, and CCTV surveillance video into a single unified ledger, backed by zero-hallucination grounded RAG search and verifiable cryptographic chain-of-custody tracking.

---

## 🌟 Key Features & Architecture

### 🛡️ Core Security & Chain of Custody
- **Dynamic API Key Config:** Support for Groq (Llama-3 Vision), Google Gemini 1.5 Pro, and an automatic offline demo fallback mode.
- **Cryptographic Audit Trail:** Every action (file upload, analysis execution, chat interrogation, PDF generation) generates SHA-256 evidence hashes logged with timestamps and investigator signatures.
- **Zero External DB Dependency:** Designed for immediate, stateless deployment on Streamlit Community Cloud without requiring SQL or vector database overhead.

### 📸 Tab 1 — Crime Scene Visual Evidence Tagger
- **Simulated RT-DETR Detection:** Real-time object detection with bounding box annotations identifying firearms, blood spatter patterns, forced entry points, edged weapons, and suspects.
- **Structured Forensic Output:** Automatic Threat Level classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), Scene Category identification (`Aggravated Burglary`, `Homicide`, etc.), spatial bounding coordinates, and prioritized investigative leads.

### 🎙️ Tab 2 — Witness Audio Transcription & Timeline
- **Whisper API / Speech Diarization:** Transcribes emergency 911/112 calls and witness interrogation tapes.
- **Timestamped Chronological Transcript:** Separates speaker channels (`Dispatcher`, `Caller`, `Suspect`) and extracts key entities (addresses, weapon descriptions, physical traits).

### 🎥 Tab 3 — CCTV Surveillance Video Tracking
- **Trajectory & Velocity Vector Analysis:** Frame sampling tracks suspect and vehicle movement vectors across spatial bounds and time intervals.
- **Penal Category Mapping:** Automatically categorizes recorded actions into criminal legal codes (e.g., *PC 459 - Burglary*, *PC 245(a)(2) - Assault w/ Firearm*).

### 🧩 Tab 4 — Multimodal Fusion & Grounded Evidence RAG
- **Master Forensic Event Ledger:** Unifies visual, acoustic, and spatial timestamps into a single structured master timeline.
- **Grounded Conversational RAG:** Natural language evidence interrogation with zero hallucination guardrails, mandating strict citation of evidence IDs (`[Citation: IMG-001]`, `[Citation: AUD-911]`).

### 📄 Tab 5 — Automated Court-Admissible PDF Export
- **ReportLab Integration:** One-click generation of standardized PDF reports formatted for legal submission.
- **Includes:** Case metadata, evidence matrices, transcript summaries, and cryptographically signed audit logs.

---

## 📂 Project Structure

```text
├── app.py              # Main Streamlit application source code
├── requirements.txt    # Python dependencies for deployment
└── README.md           # Documentation & user guide
