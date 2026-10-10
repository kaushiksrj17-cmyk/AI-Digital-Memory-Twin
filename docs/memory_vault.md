# ECHO — Secure Multimodal Memory Vault

**Research Title:** Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation  
**Component:** Phase 2 Secure Memory Vault (`/memory-vault`)  
**Storage Root:** `D:\ECHO\storage\`

---

## 1. Vault Overview

The **ECHO Multimodal Memory Vault** provides a secure, privacy-preserving, and tamper-evident preservation enclosure for personal biographical archives. Unlike generic cloud file stores, the Memory Vault anchors every artifact with spatiotemporal metadata, kinship connections, explicit legal consent, and cryptographic fingerprints.

### Core Philosophy
1. **Evidence-Grounded**: Preserves primary archival materials (letters, original audio tapes, photographs, historical documents) rather than fabricating simulated memories.
2. **Strict Distinction**: AI-generated inferences, summaries, and dialogue responses are visibly and programmatically distinguished from original preserved evidence.
3. **USB Sovereignty**: All original files, thumbnails, databases, and metadata remain confined strictly to `D:\ECHO`.

---

## 2. Supported File Modalities & Validation

| Modality | Permitted Extensions | MIME Types | Target Vault Subdirectory |
| :--- | :--- | :--- | :--- |
| **Photographs** | `.jpg`, `.jpeg`, `.png`, `.webp` | `image/jpeg`, `image/png`, `image/webp` | `D:\ECHO\storage\originals\` |
| **Videos** | `.mp4`, `.mov`, `.webm` | `video/mp4`, `video/quicktime`, `video/webm` | `D:\ECHO\storage\originals\` |
| **Audio Tapes** | `.mp3`, `.wav`, `.m4a` | `audio/mpeg`, `audio/wav`, `audio/mp4` | `D:\ECHO\storage\originals\` |
| **Documents** | `.pdf`, `.txt`, `.docx` | `application/pdf`, `text/plain`, `application/vnd.openxml...` | `D:\ECHO\storage\originals\` |

### Validation Safeguards
- **MIME & Extension Enforcement**: Rejects non-conforming extensions and mismatched MIME headers. Executables (`.exe`, `.bat`, `.sh`, `.bin`) are unconditionally blocked.
- **Size Bounds**: Maximum single file limit of 100 MB.
- **Filename Sanitization**: Path traversal sequences (`../`, `..\\`), null bytes (`\0`), and special symbols are stripped.
- **Automatic Thumbnailing**: Pillow generates 300x300 JPEG thumbnails for photographs in `D:\ECHO\storage\thumbnails\`.

---

## 3. Controlled Archival Categories

The vault organizes memories into 11 controlled categories:
1. `CHILDHOOD`: Early years, family origin, school memories.
2. `EDUCATION`: Academic milestones, degrees, ceremonies, teachers.
3. `CAREER`: Professional pursuits, workplaces, achievements.
4. `FAMILY`: Kinship milestones, marriages, reunions, parenting.
5. `FRIENDS`: Lifelong companionships, camaraderie, shared journeys.
6. `TRAVEL`: Voyages, expeditions, holidays, spatiotemporal explorations.
7. `HOBBIES`: Crafts, music, sailing, gardening, artistic expressions.
8. `ACHIEVEMENTS`: Awards, civic recognitions, personal milestones.
9. `SPECIAL_EVENTS`: Anniversaries, commemorations, historic moments.
10. `PERSONAL_STORIES`: Oral reflections, journal excerpts, philosophies.
11. `OTHER`: General preserved artifacts.

---

## 4. Cryptographic Checksums & Duplicate Detection

Every uploaded file is passed through streaming **SHA-256** digest calculation:
- If an uploaded file matches an existing checksum in `D:\ECHO\storage\originals\`, the system **re-references the existing physical asset** without writing duplicate blocks to the USB storage drive.
- The user is notified: *"Duplicate file detected. Existing vault asset referenced."*
- An audit entry records the duplicate reference event.

---

## 5. Memory Lifecycle & States

```mermaid
graph TD
    Upload[1. Upload Raw File] --> Validate[2. Validate MIME & Path]
    Validate --> Hash[3. Calculate SHA-256 Digest]
    Hash --> DupCheck{Duplicate Exists?}
    DupCheck -- Yes --> ReRef[Re-reference Existing File]
    DupCheck -- No --> Store[Write to storage/originals]
    Store --> Thumb[Generate 300x300 Thumbnail]
    Thumb --> CreateMem[Create Memory in Database]
    ReRef --> CreateMem
    CreateMem --> AuditLog[Record UPLOAD Audit Event]
    CreateMem --> Review[Status: PENDING_REVIEW]
    Review --> Verified[Status: VERIFIED (Green)]
    Review --> Rejected[Status: REJECTED (Red)]
    CreateMem --> Archive[Soft Archive: Hidden from active view]
    CreateMem --> Export[Generate JSON Export Bundle]
    CreateMem --> Delete[Soft Delete: deleted_at timestamp]
```

### Tri-State Verification Calibration
- **VERIFIED (Green)**: Corroborated by physical certificates, letters, or primary tape recordings.
- **PENDING_REVIEW / SUPPORTED_INFERENCE (Amber)**: Plausible deduction or pending family corroboration.
- **REJECTED / UNKNOWN (Red)**: Disputed or unsubstantiated claim; explicitly excluded from factual memory representations.

---

## 6. Privacy & Access Control Tiers

1. **`PRIVATE` (Default)**: Restricted to the primary Vault Guardian and author.
2. **`FAMILY`**: Accessible to authorized kinship circle.
3. **`AUTHORIZED_USERS`**: Accessible to accredited researchers, biographers, or family historians.

---

## 7. Memory Export Abstraction

Authorized users can export individual memories via `POST /api/v1/memories/{id}/export`.  
The export bundle contains:
- Complete JSON metadata, spatiotemporal anchors, and people links.
- Cryptographic SHA-256 fingerprint.
- Safe relative storage path (e.g. `originals/...`) — **Internal physical paths (`D:\...`) are never exposed**.
- Provenance records and citation evidence text.
- Mandatory ethical notice: *"ECHO is an AI-generated memorial representation. It does not recreate consciousness, identity, or the actual person."*

---

## 8. Phase 3 Multimodal Processing Integration

The Memory Vault directly interfaces with the Phase 3 Multimodal Processing Pipeline (`processing_orchestrator.py`):
1. **Asynchronous Ingestion**: Media uploaded to `storage/originals/` is enqueued for extraction.
2. **Evidentiary Derivation**: Extracts document text, OCR, timestamped audio transcripts, video keyframes, and normalized metadata.
3. **Atomic Evidence Indexing**: Derived artifacts are stored as immutable `Evidence` records in `database/models.py`.
4. **Vault Explorer UI**: The Memory Vault detail view includes dedicated tabs for:
   - Archival Overview
   - Extracted Evidence (with Provenance badges: `ORIGINAL PRESERVED CONTENT`, `USER-PROVIDED`, `AI-INFERRED`, `UNKNOWN`)
   - Extracted Entities & Documented Life Events
   - Processing Status & Telemetry History
