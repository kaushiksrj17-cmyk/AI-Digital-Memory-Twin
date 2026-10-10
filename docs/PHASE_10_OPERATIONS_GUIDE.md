# ECHO — Phase 10 Operations & Deployment Guide

**Target System:** ECHO AI Digital Memory Twin Platform  
**Operational Root:** `D:\ECHO`  
**Storage Root:** `D:\ECHO\storage`  
**Frontend Root:** `D:\ECHO\frontend`  
**Status:** Validated for Controlled Deployment  

---

## 1. System Architecture Overview

ECHO operates as a decoupled, privacy-first memorial preservation architecture:
- **Backend API:** FastAPI running on Python 3.11 with asynchronous ASGI handling on port `8000`.
- **Frontend Client:** Next.js 14 (React 18 + Three.js) web application on port `3000`.
- **Data Persistence:** Local SQLite database at `D:\ECHO\storage\local\echo_dev.db` with thread-safe connection pooling, fallback vector index, and knowledge graph persistence.
- **Vault Storage:** Strict local containment in `D:\ECHO\storage` with path traversal rejection, extension whitelisting, and cryptographic SHA-256 deduplication.

---

## 2. Startup Instructions

### Backend Service (FastAPI)

Launch from the project root in Windows PowerShell:

```powershell
Set-Location -Path "D:\ECHO"
$env:PYTHONPATH = "D:\ECHO"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Or execute the operational startup script:

```powershell
powershell -ExecutionPolicy Bypass -File D:\ECHO\scripts\start_backend.ps1
```

- **Backend Base URL:** `http://127.0.0.1:8000`
- **Interactive OpenAPI Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

### Frontend Client (Next.js)

Launch from the frontend directory:

```powershell
Set-Location -Path "D:\ECHO\frontend"
$env:NODE_OPTIONS = "-r D:/ECHO/frontend/usb-patch.cjs"
npm.cmd run dev
```

Or execute the operational startup script:

```powershell
powershell -ExecutionPolicy Bypass -File D:\ECHO\scripts\start_frontend.ps1
```

- **Frontend Application URL:** `http://localhost:3000`

---

## 3. Environment Variable Configuration

All environment variables must be defined in `D:\ECHO\.env`. Values shown below are **safe non-secret placeholders**. Never commit active production keys to Git.

```ini
# Core Application Environment
ENVIRONMENT=production
DEBUG=False
PROJECT_ROOT=D:\ECHO
STORAGE_ROOT=D:\ECHO\storage

# Security & JWT Authentication
JWT_SECRET_KEY=YOUR_SECURE_RANDOM_SECRET_KEY_HERE_MIN_32_CHARS
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Database Configuration (Defaults to offline SQLite)
DATABASE_URL=sqlite+aiosqlite:///D:/ECHO/storage/local/echo_dev.db
DATABASE_ECHO=False

# AI & Processing Provider Mode
DEFAULT_LLM_PROVIDER=mock
DEFAULT_STT_PROVIDER=mock
DEFAULT_TTS_PROVIDER=mock
OFFLINE_MODE=True

# Optional External Cloud Provider Keys (Leave blank for full local offline operation)
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
ELEVENLABS_API_KEY=
WHISPER_API_KEY=

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 4. Verified Health Check Endpoints

Verify system readiness using HTTP GET requests:

| Endpoint | Method | Expected Status | Purpose |
|---|---|---|---|
| `/api/v1/health` | GET | `200 OK` | Verifies FastAPI application, active version, uptime, and database connectivity. |
| `/api/v1/providers/health` | GET | `200 OK` | Verifies status of multimodal processing, LLM, STT, and TTS engines. |
| `/api/v1/research/status` | GET | `200 OK` | Verifies Research Evaluation telemetry and benchmark status. |

Sample verification command via PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" | ConvertTo-Json
```

Expected JSON response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "platform": "ECHO Digital Memory Twin",
  "storage_bound": "D:\\ECHO\\storage",
  "timestamp": "2026-10-10T..."
}
```

---

## 5. Automated Verification & Test Commands

Execute the verified regression suites across both backend and frontend layers:

### Backend Python Suite (204 Tests)

```powershell
Set-Location -Path "D:\ECHO"
$env:PYTHONPATH = "D:\ECHO"
python -m pytest tests/ -v
```

Expected result: **204 passed in ~10 seconds**.

### Frontend TypeScript Validation

```powershell
Set-Location -Path "D:\ECHO\frontend"
npx tsc --noEmit
```

Expected result: **Exited with code 0 (zero type errors)**.

### Frontend Production Build

```powershell
Set-Location -Path "D:\ECHO\frontend"
npm run build
```

Expected result: **25 of 25 routes compiled and prerendered with zero errors**.

---

## 6. Storage Layout & Boundary Enforcement

The entire persistence layer is confined to `D:\ECHO\storage`:

```
D:\ECHO\storage/
├── local/
│   └── echo_dev.db          # Active SQLite relational database
├── originals/               # Primary user-uploaded photographs, audio, documents
├── processed/               # Extracted features, STT transcripts, OCR text
├── thumbnails/              # Generated Pillow image thumbnails
├── temporary/               # Isolated transient files (cleaned after jobs)
└── exports/                 # User data exports and disaster recovery archives
```

**Security Boundary Policy:**
- Any path containing `..` or null bytes `\0` is rejected with `MaliciousPathError`.
- No absolute paths are returned across API responses; only safe relative identifiers are transmitted to client applications.

---

## 7. Disaster Recovery & Backup Procedure

ECHO includes an operational backup and recovery tool: `D:\ECHO\scripts\backup_vault.py`.

### Creating a Snapshot Backup

```powershell
Set-Location -Path "D:\ECHO"
python scripts/backup_vault.py --backup
```

This generates a timestamped, compressed archive in `D:\ECHO\storage\exports\echo_vault_backup_YYYYMMDD_HHMMSS.zip` containing:
- Complete database file (`echo_dev.db`)
- Original and processed vault assets
- Cryptographic SHA-256 manifest (`manifest.json`)

To simulate a backup without writing files to disk:
```powershell
python scripts/backup_vault.py --backup --dry-run
```

### Verifying Archive Integrity

```powershell
python scripts/backup_vault.py --verify "D:\ECHO\storage\exports\echo_vault_backup_YYYYMMDD_HHMMSS.zip"
```

The verification tool validates every file against its recorded SHA-256 hash to confirm that no corruption or tampering has occurred.

### Safe Restoration Procedure

Restorations require an explicit `--target-dir` argument to prevent accidental destruction of active data:

```powershell
python scripts/backup_vault.py --restore "D:\ECHO\storage\exports\echo_vault_backup_YYYYMMDD_HHMMSS.zip" --target-dir "D:\ECHO\storage\recovered"
```

---

## 8. Log Locations & Safe Troubleshooting

- **Server Access Logs:** Streamed to stdout/stderr with timestamp, HTTP method, route, and status code.
- **Audit Logs:** Tamper-evident records stored in SQLite and queryable via `/api/v1/audit/`.
- **Sensitive Data Redaction:** All passwords, JWT tokens, Bearer headers, and confidential memory descriptions are scrubbed from log statements via `backend/app/core/security.py`.
- **Stack Trace Suppression:** In production (`DEBUG=False`), 500 errors return sanitized error envelopes (`{"detail": "Internal server error"}`) without leaking internal tracebacks.

---

## 9. External Provider Behavior & Offline Guarantees

- **Default State:** Offline-first. When `OFFLINE_MODE=True` (or when cloud API keys are empty), all operations run through local deterministic mock providers:
  - `MockLLMProvider`: Produces evidence-grounded answers citing only retrieved context.
  - `MockSTTProvider`: Emulates Whisper transcription with simulated word confidence.
  - `MockTTSProvider`: Synthesizes valid WAV audio containing audible watermark disclosure.
- **Cloud Egress Verification:** The system initiates zero external network egress unless explicit cloud provider API keys (`GEMINI_API_KEY`, `ELEVENLABS_API_KEY`) are intentionally configured in `.env` and `OFFLINE_MODE` is disabled.

---

## 10. Safe Shutdown Instructions

1. **FastAPI Backend:** Send `SIGINT` (Ctrl+C). The ASGI server will complete in-flight transactions, flush SQLite WAL journals, and exit cleanly.
2. **Next.js Frontend:** Send `SIGINT` (Ctrl+C). The Node.js dev process terminates gracefully.

---

## 11. Post-Reboot Verification Checklist

After a system reboot, execute the following steps to verify full operational readiness:

1. Open PowerShell and navigate to `D:\ECHO`.
2. Run backend regression: `python -m pytest tests/ -v` (confirm 204 tests pass).
3. Start the backend: `powershell scripts/start_backend.ps1`.
4. In a separate terminal, start the frontend: `powershell scripts/start_frontend.ps1`.
5. Open browser at `http://localhost:3000` and confirm dashboard displays with authentic archive records.
