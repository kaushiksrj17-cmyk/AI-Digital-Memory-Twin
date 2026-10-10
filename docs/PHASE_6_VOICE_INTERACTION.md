# ECHO — Phase 6: Voice Interaction & Authorized Memorial Voice

**Research Title:** Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation.  
**Project Tagline:** "Preserve the memories. Hear the voice. See the presence. Keep the story alive."

---

## 1. Executive Summary & Research Objective

Phase 6 implements a research-grade, privacy-preserving, and evidence-grounded **Voice Interaction System** for the ECHO Digital Memory Twin architecture. It enables family members and designated guardians to engage in oral history dialogue: speaking a spoken inquiry, transcribing speech to text, retrieving verified documentary proof through the Phase 5 RAG and Knowledge Graph engine, validating the response against the Memory Guardian safety boundary, and playing the approved response using text-to-speech (TTS) with strict ethical watermarking.

### Core Non-Negotiable Invariants

1. **Three Distinct Audio Categories**:
   - `ORIGINAL RECORDING` — authentic oral history audio preserved in the archive (e.g., recorded cassette tapes, vinyl records, dictaphone recordings).
   - `TRANSCRIPTION` — verbatim or corrected text extracted from spoken voice.
   - `AI-GENERATED MEMORIAL VOICE` — synthetic audio synthesized by the system.
   - *Never present synthesized audio as an authentic original recording.*
2. **Mandatory Ethical Disclosure**:
   - Every synthesized response is indelibly labeled:
     > `"AI-GENERATED MEMORIAL VOICE — SYNTHETIC AUDIO, NOT AN ORIGINAL RECORDING."`
   - Never claim the voice possesses consciousness, living sentience, or represents authentic current speech.
3. **Evidence-Grounded Synthesis Gate**:
   - Spoken queries **must** pass through the Phase 5 RAG and Memory Guardian pipeline.
   - Responses blocked by the Memory Guardian are **never synthesized**.
   - If zero documentary evidence exists in the archive, the system explicitly responds that information is not available and refuses to invent personal memories.
4. **Strict Likeness Authorization**:
   - Possession of oral history recordings **never constitutes proof of cloning rights**.
   - Custom voice cloning requires explicit, documented `CUSTOM_VOICE_SYNTHESIS` consent, rechecked immediately before every synthesis request.
   - Missing or revoked consent triggers automatic fallback to a clearly labeled generic synthetic voice.

---

## 2. End-to-End Voice Interaction Pipeline

```
USER AUDIO INPUT (Microphone or File Upload: WAV, MP3, M4A, OGG, WebM)
   │
   ▼
1. AUDIO VALIDATION (Magic bytes, MIME check, extension check, 25MB limit)
   │
   ▼
2. AUTHENTICATION & CONSENT CHECK (VOICE_PROCESSING & AI_PROCESSING scopes)
   │
   ▼
3. SPEECH-TO-TEXT (STT) (Multi-language transcription: en, ta, hi with timestamps)
   │
   ▼
4. TRANSCRIPT REVIEW & EDITING (User may review or edit transcript before RAG)
   │
   ▼
5. PHASE 5 CONVERSATION ENGINE (Intent classification & dialogue routing)
   │
   ▼
6. MEMORY DNA + HYBRID RETRIEVAL + KNOWLEDGE GRAPH (Evidence search)
   │
   ▼
7. GROUNDED RESPONSE GENERATION (Strict anti-fabrication prompt instruction)
   │
   ▼
8. MEMORY GUARDIAN VALIDATION (Pass / Revise / Block boundary verification)
   │
   ├─► IF BLOCKED: Synthesis HALTED; return safe ethical explanation
   │
   ▼ IF APPROVED (PASS / REVISE)
9. CONFIDENCE & PROVENANCE ATTACHMENT (VERIFIED / SUPPORTED_INFERENCE / UNKNOWN)
   │
   ▼
10. TEXT-TO-SPEECH (TTS) (Consent re-checked; PCM WAV generated with watermarks)
   │
   ▼
11. PRIVATE AUDIO DELIVERY (Authenticated endpoint, SHA-256 checksum)
   │
   ▼
12. AUDIT TRAIL & LATENCY TELEMETRY (Tamper-evident logs & latency breakdown)
```

---

## 3. Voice Session State Machine

Every voice interaction session tracks explicit finite state transitions:

```
[ IDLE ] ──► [ RECORDING ] ──► [ UPLOADING ] ──► [ TRANSCRIBING ]
                                                        │
┌───────────────────────────────────────────────────────┘
▼
[ RETRIEVING ] ──► [ GENERATING ] ──► [ VALIDATING ] ──► [ SYNTHESIZING ]
                                                              │
                     ┌────────────────────────────────────────┴─────────┐
                     ▼                                                  ▼
               [ COMPLETED ]                                      [ BLOCKED ]
                                                                        ▲
[ CANCELLED ] (User cancel)                     [ FAILED ] (Error) ─────┘
```

- `IDLE`: Session initialized, microphone or upload ready.
- `RECORDING`: Browser actively streaming audio via `MediaRecorder` API.
- `UPLOADING`: Encrypted transport of binary audio payload to backend.
- `TRANSCRIBING`: Speech recognition engine generating transcript segments.
- `RETRIEVING`: Context Manager querying vector store and knowledge graph.
- `GENERATING`: LLM generating candidate grounded answer.
- `VALIDATING`: Memory Guardian auditing claims against primary evidence.
- `SYNTHESIZING`: TTS engine synthesizing validated answer into watermarked audio.
- `COMPLETED`: Playback asset prepared and ready for client listening.
- `BLOCKED`: Guardian or consent blocked synthesis; safe explanation displayed.
- `FAILED`: Processing failure reported cleanly without unhandled crash.
- `CANCELLED`: User dismissed or cancelled the session.

---

## 4. API Specification & Endpoints

All voice interaction endpoints are served under `/api/v1/voice`:

### 4.1 System Capabilities & Health
- `GET /api/v1/voice/status`
  - Returns configured STT/TTS engine, mock status, supported languages (`en`, `ta`, `hi`), watermarking status, and ethical disclaimers.

### 4.2 Voice Sessions
- `GET /api/v1/voice/sessions`
  - List active voice sessions with latency metrics and state machine status.
- `POST /api/v1/voice/sessions`
  - Initialize a new voice interaction session (`IDLE` state).
- `GET /api/v1/voice/sessions/{session_id}`
  - Retrieve real-time session transcripts, guardian status, and latencies.
- `POST /api/v1/voice/sessions/{session_id}/cancel`
  - Cancel an active voice processing session.

### 4.3 Speech-to-Text Transcription
- `POST /api/v1/voice/transcribe`
  - Accepts multipart audio upload or JSON base64 payload.
  - Returns timestamped transcript segments, language, duration, and labels as `TRANSCRIPTION`.

### 4.4 End-to-End Pipeline
- `POST /api/v1/voice/pipeline` (alias `/api/v1/voice/interact`)
  - Submits spoken question through full STT -> RAG -> Guardian -> TTS pipeline.
- `POST /api/v1/voice/query-transcript`
  - Submits a reviewed or user-edited transcript directly to RAG and TTS.

### 4.5 Speech Synthesis & Private Playback
- `POST /api/v1/voice/synthesize`
  - Directly synthesizes approved response text (blocks if Guardian status is `BLOCK`).
- `GET /api/v1/voice/audio/{audio_id}`
  - Delivers access-controlled private audio bytes.
  - Headers: `X-Audio-Category`, `X-Ethical-Disclosure`, `X-SHA256-Checksum`.
- `DELETE /api/v1/voice/audio/{audio_id}`
  - Securely purges eligible temporary audio assets.

### 4.6 Likeness Profiles & Kinship Consent
- `GET /api/v1/voice/profiles` — List authorized voice likeness profiles.
- `POST /api/v1/voice/profiles` — Register voice profile metadata.
- `POST /api/v1/voice/profiles/{profile_id}/revoke` — Immediately revoke profile likeness.
- `POST /api/v1/voice/profiles/{profile_id}/disable` — Temporarily disable profile.
- `GET /api/v1/voice/consent` — Check required scopes and authorization.
- `POST /api/v1/voice/consent` — Formally grant kinship voice consent.
- `POST /api/v1/voice/consent/revoke` — Revoke voice processing or likeness consent.

### 4.7 Research Telemetry & Auditing
- `GET /api/v1/voice/metrics` — Aggregate latency benchmarks and accuracy rates.
- `GET /api/v1/voice/audit` — Tamper-evident audit trail for voice operations.

---

## 5. Storage Architecture & Privacy Boundaries

All voice assets reside strictly within the dedicated project storage tree:
`D:\ECHO\storage\voice\`

- `D:\ECHO\storage\voice\recordings\` — Authentic original audio preserved by users.
- `D:\ECHO\storage\voice\temp\` — Ephemeral synthesized audio (auto-purged after 7 days).
- `D:\ECHO\storage\voice\profiles\` — Access-controlled profile metadata.

### Security Invariants:
- Absolute filesystem paths are never returned in API payloads.
- Directory traversal attacks (`../`) are detected and rejected with `PermissionError`.
- Private audio is streamed exclusively through authenticated API endpoints; no files are placed in public frontend asset folders.
- Every generated WAV embeds the binary acoustic watermark payload:
  `[ECHO-AI-MEMORIAL-VOICE-VERIFIED]`.
