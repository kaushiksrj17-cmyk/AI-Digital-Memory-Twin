# ECHO Multimodal Processing Security & Consent Architecture

## Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation

---

### 1. Security Philosophy
The ingestion and processing of deeply personal memorial assets requires military-grade privacy and defensive isolation. The processing subsystem enforces strict zero-trust principles across all processing stages.

---

### 2. File & Storage Isolation Controls

#### 2.1 Storage Root Containment (`D:\ECHO\storage`)
- All processing activity occurs strictly within `D:\ECHO\storage`.
- Ingress paths are checked via `Path.resolve()` against `VaultStorageManager.root`.
- Path traversal tokens (`..`, null bytes, control sequences) trigger `MaliciousPathError` and are audited immediately.

#### 2.2 Filename Sanitization
- Incoming filenames are stripped of non-alphanumeric characters (except safe `_` and `-`).
- Basenames are limited to 100 characters and prepended with a 64-character SHA-256 hash.

#### 2.3 Strict Format & MIME Whitelist
- Only supported extensions and verified MIME types are permitted:
  - **Images**: `.jpg`, `.jpeg`, `.png`, `.webp`
  - **Videos**: `.mp4`, `.mov`, `.webm`
  - **Audio**: `.mp3`, `.wav`, `.m4a`
  - **Documents**: `.pdf`, `.txt`, `.docx`
- Executable files, shell scripts, or macro-enabled documents are rejected at validation.

#### 2.4 File Size Ceiling
- Strict 100 MB per-file limit enforced before buffering into memory or writing to disk.

#### 2.5 Original File Immutability
- Files in `storage/originals/` are strictly read-only after cryptographic checksumming.
- Derived outputs (thumbnails, keyframes, OCR text) are stored exclusively in `storage/thumbnails/` and `storage/processed/`. No processor ever overwrites or modifies an original file.

---

### 3. Consent Enforcement Engine (`consent_service.py`)

#### 3.1 Granular Consent Requirements
Before any media file enters the processing pipeline, the `ProcessingOrchestrator` verifies explicit consent:
- `MEDIA_PROCESSING`: Required for thumbnail generation, keyframe extraction, audio duration checks.
- `AI_PROCESSING`: Required for OCR, STT transcription, visual entity extraction.

#### 3.2 Consent Revocation Behavior
- If consent is revoked by a family guardian for a memory or media asset:
  1. The processing pipeline halts immediately.
  2. The job transitions to `REVIEW_REQUIRED`.
  3. An audit log event (`PROCESSING_FAILED` / `BLOCKED_BY_CONSENT`) is recorded.
  4. No subsequent AI extraction or derived evidence generation occurs.

---

### 4. Privacy & Authorization Controls
- **Zero Physical Path Exposure**: Responses from `/api/v1/processing`, `/api/v1/evidence`, and `/api/v1/media` contain only safe relative storage references (`originals/...`, `thumbnails/...`). Physical paths (`D:\ECHO\...`) are never exposed in JSON responses.
- **Privacy Boundaries**: Memories marked `PRIVATE` or `FAMILY` enforce authorization headers before evidence or transcripts can be queried.
- **Derived Content Sanitization**: All extracted text, OCR results, and model responses are treated as untrusted strings and sanitized to prevent XSS attacks before rendering in the Next.js UI.
