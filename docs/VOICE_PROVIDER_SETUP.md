# ECHO — Voice Provider Setup & Configuration Guide

**Research Title:** Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation.

---

## 1. Provider Architecture Overview

ECHO decouples audio processing logic from specific external commercial vendors through an extensible provider interface:

- `ai/providers/stt.py`: Speech-to-Text provider abstraction.
- `ai/providers/tts.py`: Text-to-Speech provider abstraction.
- `backend/app/services/voice_provider.py`: Unified provider registry and format validator.

The system features deterministic, multi-language mock providers that operate fully offline without external API keys, while supporting external AI providers when credentials are configured.

---

## 2. Configuration & Environment Variables

Configure your `.env` file in the project root (`D:\ECHO\.env`):

```bash
# ==============================================================================
# Speech-to-Text (STT) Configuration
# ==============================================================================
STT_PROVIDER="mock"            # Options: "mock", "gemini", "whisper", "deepgram"
ENABLE_STT_MOCK="true"         # Set to "false" to enforce live external provider checks
STT_API_KEY=""                 # Your external provider API key

# ==============================================================================
# Text-to-Speech (TTS) Configuration
# ==============================================================================
TTS_PROVIDER="mock"            # Options: "mock", "elevenlabs", "coqui", "google-tts"
ENABLE_TTS_MOCK="true"         # Set to "false" to enforce live external provider checks
TTS_API_KEY=""                 # Your external provider API key

# ==============================================================================
# Authorized Memorial Custom Voice Provider
# ==============================================================================
CUSTOM_VOICE_PROVIDER="mock"   # Options: "mock", "elevenlabs-voice-clone", "coqui-xtts"
CUSTOM_VOICE_API_KEY=""        # API key for authorized custom voice likeness

# ==============================================================================
# Storage & Retention Boundaries (Strictly inside D:\ECHO)
# ==============================================================================
VOICE_STORAGE_ROOT="D:\ECHO\storage\voice"
VOICE_WATERMARK_TAG="[ECHO-AI-MEMORIAL-VOICE-VERIFIED]"
VOICE_RETENTION_DAYS_TEMP=7
VOICE_RETENTION_DAYS_PERMANENT=365
VOICE_MAX_UPLOAD_SIZE_MB=25
```

---

## 3. Supported Languages & Audio Formats

### Supported Languages
1. **English (`en`)**: Full support for speech recognition, timeline query mapping, and speech synthesis.
2. **Tamil (`ta`)**: Phonetic recognition and Tamil synthesis voice models.
3. **Hindi (`hi`)**: Devanagari speech recognition and Hindi synthesis voice models.

### Audio File Constraints
- **Allowed Formats**: `.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm`.
- **Validation**: Strict verification of file extension, MIME type, and binary magic bytes (e.g., `RIFF....WAVE`, MP3 sync words `0xFF 0xFB`, Ogg `OggS`, WebM `0x1A 0x45 0xDF 0xA3`).
- **Maximum Payload Size**: 25 MB per recording.
- **Safety**: Uploaded files are never executed.

---

## 4. Local Execution & Startup Commands

### Step 1: Initialize Database & Storage Directories (PowerShell)
```powershell
Set-Location -Path "D:\ECHO"
$env:PYTHONPATH = "D:\ECHO"
python database/init_db.py
```

### Step 2: Start Backend Server (FastAPI / Uvicorn)
```powershell
Set-Location -Path "D:\ECHO"
$env:PYTHONPATH = "D:\ECHO"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Backend API Root**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation**: `http://127.0.0.1:8000/docs`
- **Voice Capabilities Endpoint**: `http://127.0.0.1:8000/api/v1/voice/status`

### Step 3: Start Frontend Dev Server (Next.js)
```powershell
Set-Location -Path "D:\ECHO\frontend"
npm run dev
```
*(Uses the local Windows USB/UNC path patch `./usb-patch.cjs` to ensure reliable file resolution).*

- **Frontend Application Root**: `http://localhost:3000`
- **Voice Interaction Page**: `http://localhost:3000/voice`
- **Conversation Interface**: `http://localhost:3000/conversation`
- **Dashboard**: `http://localhost:3000/dashboard`

---

## 5. Running Automated Backend Tests

To execute the complete suite of 143 unit and integration tests across all phases:

```powershell
Set-Location -Path "D:\ECHO"
$env:PYTHONPATH = "D:\ECHO"
python -m pytest tests/backend/ -v
```

To run Phase 6 voice tests specifically:
```powershell
python -m pytest tests/backend/test_phase6_voice.py -v
```

To run the Next.js production build check:
```powershell
Set-Location -Path "D:\ECHO\frontend"
npm run build
```
