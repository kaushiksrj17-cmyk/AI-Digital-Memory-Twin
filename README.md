# ECHO — AI Digital Memory Twin

> *“Preserve the memories. Hear the voice. See the presence. Keep the story alive.”*

**Research Title:** *Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation*  
**Storage Root Boundary:** Strictly confined to `D:\ECHO`

---

## 1. Project Overview & Motivation

**ECHO** is a research-grade, multimodal AI system engineered to preserve heterogeneous personal memories (photographs, oral history audio recordings, scanned handwritten letters, vital documents, and family memoirs) and organize them into an interactive digital memorial representation.

Traditional conversational AI avatars often fabricate memories, confabulate historical events, and exploit emotional vulnerabilities by falsely simulating living consciousness or deceased personas. ECHO is built on a fundamentally different foundation: **Evidence-Grounded Preservation**. It strictly refuses to simulate consciousness or claim a living soul, instead functioning as an authentic archival custodian that links every assertion directly to verified physical and digital records.

---

## 2. Problem Statement & Research Objectives

### The Problem
1. **Parametric Hallucination:** Contemporary large language models fabricate plausible-sounding details when queried about personal histories.
2. **Deceptive Psychological Exploitation:** Commercial "griefbots" frequently deceive grieving individuals by asserting *"I am really your loved one speaking from beyond."*
3. **Data Leakage & Privacy Violations:** Cloud-centric memorial apps upload intimate family records and voice likenesses to third-party cloud servers without granular consent.

### Research Objectives
- **Pillar 1:** Ingest and normalize heterogeneous media types (audio, documents, letters, photos).
- **Pillar 2:** Connect memories with people, milestones, and places in a spatio-temporal knowledge graph.
- **Pillar 3:** Retrieve authenticated proof using hybrid vector-keyword retrieval (RAG).
- **Pillar 4:** Express transparent tri-state confidence ratings on every claim:
  - 🟢 **GREEN (VERIFIED EVIDENCE):** Grounded in authenticated primary records.
  - 🟡 **YELLOW (SUPPORTED INFERENCE):** Plausible contextual deduction corroborated by intersecting records.
  - 🔴 **RED (UNKNOWN / UNSUPPORTED):** Unsubstantiated or unrecorded; explicitly acknowledged as unknown with zero fabrication.
- **Pillar 5:** Expose granular source provenance citations with document folio numbers and timestamps.
- **Pillar 6:** Enforce non-deceptive ethical boundaries through the Memory Guardian.
- **Pillar 7:** Guarantee data sovereignty through private local storage volume isolation (`D:\ECHO`).

---

## 3. Primary Research Questions

> **Primary RQ:** *How can a multimodal AI system structure heterogeneous biographical evidence into an interactive digital memorial representation while guaranteeing strict evidence-grounding, verifiable confidence states, and non-deceptive ethical boundaries?*

- **RQ 1 (Cross-Modal Grounding):** How effectively can cross-modal artifacts be indexed without parametric hallucination?
- **RQ 2 (Confidence Calibration):** Can a tri-state confidence calibration framework reliably communicate evidence certainty to family members and researchers?
- **RQ 3 (Ethical Safeguards):** What algorithmic constraints prevent conversational deception under emotional or adversarial probing?
- **RQ 4 (Local Sovereignty):** Can a complete multimodal memory twin operate under strict local storage isolation with zero cloud egress?

---

## 4. System Architecture

The ECHO architecture comprises six decoupled layers:

```
[ Client Layer ] Next.js 14 Responsive UI & 3D Spatial Memory Sanctuary
      │
[ Gateway & Guardian ] FastAPI Gateway + Memory Guardian Boundary Filter
      │
[ Service Layer ] Memory Lifecycle, Provenance Citations, Tri-State Calibration
      │
[ Domain Models ] Pydantic v2 Typed Schemas (Memories, People, Evidence)
      │
[ AI Abstractions ] Pluggable Providers (LLM, Embeddings, STT, TTS, Vision, OCR)
      │
[ Storage Subsystem ] Local Enclosure (D:\ECHO\storage\local) + PostgreSQL / Qdrant
```

---

## 5. Technology Stack

- **Frontend:** Next.js 14 (App Router), React 18, TypeScript 5, Tailwind CSS (Memorial Slate/Indigo/Gold Palette), Lucide Icons, Three.js Spatial Shader abstraction.
- **Backend:** Python 3.11, FastAPI, Pydantic v2, Pydantic-Settings, Uvicorn, WebSockets.
- **Data & Persistence:** SQLAlchemy 2.0 (PostgreSQL-ready with SQLite fallback), Vector DB abstraction (Qdrant & Cosine Mock), Knowledge Graph abstraction (Neo4j & NetworkX).
- **AI Provider Layer:** Pluggable interfaces for LLM, dense embeddings, speech recognition (STT), speech synthesis (TTS), computer vision, and OCR (offline mock providers enabled by default).
- **Deployment:** Docker, Docker Compose (`docker-compose.yml`).

---

## 6. Ethical Boundaries & Safeguards

> ### Canonical Ethical Notice
> **“ECHO is an AI-generated memorial representation. It does not recreate consciousness, identity, or the actual person.”**

1. **Never Simulates Consciousness:** The system will never state *"I am thinking"*, *"I have a soul"*, or *"I feel pain"*.
2. **Never Claims Living Identity:** Prohibits statements claiming *"I am really your mother"* or *"I am speaking from the afterlife"*.
3. **Never Fabricates Memories:** When asked about unrecorded events, ECHO explicitly responds:  
   *“No preserved archival evidence is currently on record regarding this query. ECHO does not fabricate undocumented memories.”*
4. **Mandatory AI Disclosure:** All text and synthesized audio carries explicit digital watermark tags and notices.

---

## 7. Storage Architecture & Vault Organization

All project-specific storage is strictly confined to the USB workspace root `D:\ECHO`:

```
D:\ECHO\storage\
├── originals\     # Cryptographically verified raw primary assets (immutable)
├── processed\     # Normalized media formats (ready for future feature extraction)
├── thumbnails\    # High-performance previews & visual cards (Pillow generated)
├── temporary\     # In-flight chunk buffers & transient upload processing
├── exports\       # Evidence packages, provenance manifests & ZIP archives
└── local\         # Local databases, vectors, and cache subsystems
```

- **MIME & Format Security:** Validated against strict whitelists (Images: JPG, JPEG, PNG, WEBP; Videos: MP4, MOV, WEBM; Audio: MP3, WAV, M4A; Documents: PDF, TXT, DOCX).
- **Filesystem Isolation:** Internal physical paths are never leaked to frontend clients or API responses; safe relative keys and asset IDs are utilized.
- **Cryptographic Deduplication:** SHA-256 checksums are calculated upon receipt. Duplicate files are referenced without redundant physical disk writes.

---

## 8. Phase 2 — Secure Multimodal Memory Vault

The **Memory Vault** provides an authenticated archival environment with rigorous evidence tracking:

### Controlled Categories (11)
- `CHILDHOOD`, `EDUCATION`, `CAREER`, `FAMILY`, `FRIENDS`, `TRAVEL`, `HOBBIES`, `ACHIEVEMENTS`, `SPECIAL_EVENTS`, `PERSONAL_STORIES`, `OTHER`.

### Source Provenance
- `ORIGINAL_PHOTO`, `ORIGINAL_VIDEO`, `ORIGINAL_AUDIO`, `DOCUMENT`, `FAMILY_STORY`, `USER_ENTRY`, `AI_GENERATED`.
- *Mandatory Visual Differentiation:* AI-generated content is clearly distinguished with prominent badges and disclaimers.

### Granular Consent Lifecycle
- Explicit permissions must be recorded per asset:
  - `MEDIA_PROCESSING`
  - `AI_PROCESSING`
  - `VOICE_PROCESSING`
  - `AVATAR_PROCESSING`
  - `FAMILY_ACCESS`
- Consent can be inspected and revoked at any time. ECHO never assumes consent for biometric or generative tasks.

### Tamper-Evident Audit Trails
- Every vault interaction is recorded in a queryable audit log: `UPLOAD`, `VIEW`, `EDIT`, `DELETE`, `ARCHIVE`, `EXPORT`, `VERIFY`, `REJECT`, `CONSENT_GRANTED`, `CONSENT_REVOKED`, `PRIVACY_CHANGED`.

---

## 9. Development Commands & Quickstart

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm

### Starting the Backend (FastAPI)
```powershell
# From D:\ECHO
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
- **API Health Check:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
- **Interactive OpenAPI Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### API Endpoints Overview (v1)
- `POST /api/v1/memories` — Ingest new structured memory record
- `GET /api/v1/memories` — Filter and search memories (category, type, date, verification, privacy)
- `GET /api/v1/memories/{id}` — Retrieve detailed memory profile & provenance
- `PUT /api/v1/memories/{id}` — Update memory metadata
- `DELETE /api/v1/memories/{id}` — Secure soft-deletion
- `POST /api/v1/memories/{id}/archive` — Non-destructive archival
- `POST /api/v1/memories/{id}/verify` — Evidentiary review and verification
- `POST /api/v1/memories/{id}/export` — Export standalone evidence package
- `POST /api/v1/media/upload` — Multi-part secure file upload with SHA-256 deduplication
- `GET /api/v1/media/{id}` — Retrieve media descriptor
- `DELETE /api/v1/media/{id}` — Secure media removal
- `POST /api/v1/consent` & `POST /api/v1/consent/revoke` — Granular consent tracking
- `GET /api/v1/audit` — Tamper-evident audit trail queries
- `GET /api/v1/analytics/stats` — Real-time memory and verification metrics

### Phase 3 Multimodal Processing & Evidence Endpoints (v1)
- `POST /api/v1/processing/{media_id}` — Enqueue media for asynchronous multimodal processing
- `GET /api/v1/processing/{media_id}` — Query processing job status and error diagnostics
- `GET /api/v1/processing` — List active and historical processing jobs
- `POST /api/v1/processing/{media_id}/retry` — Safe idempotent retry of failed/review-required processing
- `POST /api/v1/processing/{media_id}/cancel` — Cancel pending processing job
- `GET /api/v1/evidence` — Query atomic evidence ledger with multi-facet filtering (type, provenance, confidence)
- `GET /api/v1/evidence/{id}` — Retrieve specific evidence artifact and citation chain
- `GET /api/v1/media/{id}/metadata` — Normalized technical and archival metadata
- `GET /api/v1/media/{id}/ocr` — OCR text extraction (English, Tamil, Hindi)
- `GET /api/v1/media/{id}/transcript` — Speech-to-text transcript with timestamped segments
- `GET /api/v1/media/{id}/keyframes` — Adaptive video keyframe extraction
- `GET /api/v1/memories/{id}/entities` — Extracted named entities (Person, Location, Organization, Date)
- `GET /api/v1/memories/{id}/events` — Documented life milestones and celebrations
- `GET /api/v1/analytics/processing` — Research telemetry on latency, evidence count, and confidence distribution

### Phase 4 Memory DNA, Knowledge Graph & Retrieval Endpoints (v1)
- `POST /api/v1/memory-dna/build/{memorial_profile_id}` — Compile validated Memory DNA from multimodal evidence
- `GET /api/v1/memory-dna/{memorial_profile_id}` — Retrieve active Memory DNA structured profile
- `GET /api/v1/memory-dna/{memorial_profile_id}/history` — Query immutable version history (`MemoryDNAVersion`)
- `GET /api/v1/memory-dna/{memorial_profile_id}/items` — Retrieve categorized DNA items with provenance
- `GET /api/v1/memory-dna/items/{item_id}` — Inspect specific Memory DNA item
- `POST /api/v1/memory-dna/items/{item_id}/verify` — Verify DNA item evidentiary grounding
- `POST /api/v1/memory-dna/items/{item_id}/reject` — Reject unsupported DNA item
- `GET /api/v1/graph/nodes` — List and filter Knowledge Graph nodes (Person, Event, Place, Object, etc.)
- `GET /api/v1/graph/nodes/{id}` — Retrieve specific node and connected properties
- `GET /api/v1/graph/nodes/{id}/neighbors` — Explore 1-hop and multi-hop graph neighborhoods
- `GET /api/v1/graph/relationships` — Query validated graph relationship edges with evidence links
- `GET /api/v1/graph/search` — Search graph nodes and relationships by label or attribute
- `POST /api/v1/graph/rebuild/{memorial_profile_id}` — Recompile Knowledge Graph from archival entities and events
- `POST /api/v1/embeddings/index/{memorial_profile_id}` — Segment text into chunks and index in vector store
- `GET /api/v1/embeddings/stats` — Vector store statistics and provider diagnostics
- `DELETE /api/v1/embeddings/{id}` — Remove vector embedding and indexed chunk
- `POST /api/v1/rag/query` — Execute evidence-grounded RAG query with 18-check Guardian audit
- `GET /api/v1/rag/metrics` — Query RAG retrieval, generation, and Guardian latency metrics
- `POST /api/v1/guardian/validate` — Validate candidate responses against all 18 evidentiary and boundary checks
- `GET /api/v1/guardian/status` — Inspect Memory Guardian real-time operational status
- `GET /api/v1/guardian/audit` — Retrieve historical Guardian audit verdicts and violation logs
- `GET /api/v1/conversations/sessions` — List conversation dialogue sessions
- `POST /api/v1/conversations` — Create a new conversational memorial session
- `GET /api/v1/conversations/{id}` — Retrieve full conversation transcript and evidence citations
- `POST /api/v1/conversations/{id}/messages` — Post user query, run RAG, and return grounded response
- `POST /api/v1/conversations/{id}/export` — Export tamper-evident dialogue transcript with provenance

### Phase 6 Voice Interaction Endpoints (v1)
- `GET /api/v1/voice/status` — Voice engine capabilities and supported languages
- `POST /api/v1/voice/sessions` — Initialize oral history dialogue session
- `POST /api/v1/voice/transcribe` — Transcribe speech audio to text with timestamps
- `POST /api/v1/voice/synthesize` — Synthesize approved memorial voice audio with watermarking
- `GET /api/v1/voice/profiles` — List voice profiles and likeness consent states
- `POST /api/v1/voice/consent` — Record and verify kinship consent for custom voice cloning
- `POST /api/v1/voice/consent/revoke` — Revoke likeness consent immediately

### Phase 7 3D Memory Room & Memorial Avatar Endpoints (v1)
- `GET /api/v1/memory-room` — Retrieve complete 3D room composition, spatial transforms, and avatar state
- `GET /api/v1/memory-room/objects/{id}` — Retrieve evidentiary grounding and metadata for a specific 3D room object
- `PUT /api/v1/memory-room/config` — Update room atmosphere (theme, lighting, reduced motion, audio)
- `GET /api/v1/memory-room/metrics` — Retrieve aggregated research instrumentation metrics
- `POST /api/v1/memory-room/metrics` — Record client-side 3D performance and accessibility telemetry
- `GET /api/v1/avatar/status` — Inspect visual presence shader engine status and ethical boundary
- `GET /api/v1/avatar/config` — Inspect memorial avatar pose, model type, and likeness consent status
- `PUT /api/v1/avatar/config` — Update avatar configuration, pose, model type, and display name
- `POST /api/v1/avatar/speak` — Trigger verified avatar speech guided by Memory Guardian and authorized TTS

### Starting the Frontend (Next.js)
```powershell
# From D:\ECHO\frontend
$env:NODE_OPTIONS = "-r D:/ECHO/frontend/usb-patch.cjs"
npm run dev
# Or via PowerShell start script:
powershell -ExecutionPolicy Bypass -File .\scripts\start_frontend.ps1
```
- **Frontend Portal URL:** [http://localhost:3000](http://localhost:3000)
- **3D Interactive Memory Room:** [http://localhost:3000/memory-room](http://localhost:3000/memory-room)
- **Voice Preservation Studio:** [http://localhost:3000/voice](http://localhost:3000/voice)
- **Memorial Dialogue Studio:** [http://localhost:3000/conversation](http://localhost:3000/conversation)
- **Executive Analytics Dashboard:** [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
- **Memory Vault Interface:** [http://localhost:3000/memory-vault](http://localhost:3000/memory-vault)
- **Multimodal Processing Center:** [http://localhost:3000/processing](http://localhost:3000/processing)
- **Evidence Explorer & Grounding Audit:** [http://localhost:3000/evidence](http://localhost:3000/evidence)
- **Memory DNA Intelligence:** [http://localhost:3000/memory-dna](http://localhost:3000/memory-dna)
- **Knowledge Graph Visualizer:** [http://localhost:3000/knowledge-graph](http://localhost:3000/knowledge-graph)
- **Semantic & Hybrid Retrieval Studio:** [http://localhost:3000/retrieval](http://localhost:3000/retrieval)

### Running Backend Tests
```powershell
# From D:\ECHO
python -m pytest tests/backend/ -v
# Or via automated verification runner:
powershell -ExecutionPolicy Bypass -File .\scripts\run_tests.ps1
```

---

## 10. Development Roadmap

- **✅ PHASE 1 — ECHO Foundation and Research-Grade Architecture** (Completed & Verified — 11 Tests Passed)
- **✅ PHASE 2 — Secure Multimodal Memory Vault** (Completed & Verified — 28 Tests Passed)
- **✅ PHASE 3 — Multimodal AI Memory Processing** (Completed & Verified — 30 Tests Passed)
- **✅ PHASE 4 — ECHO Memory DNA + Knowledge Graph + Vector Retrieval Foundation** (Completed & Verified — 27 Tests Passed)
- **✅ PHASE 5 — Conversation Engine + Memory Guardian + Evidence-Grounded RAG** (Completed & Verified — 28 Tests Passed)
- **✅ PHASE 6 — Voice Interaction + Authorized Memorial Voice** (Completed & Verified — 27 Tests Passed)
- **✅ PHASE 7 — 3D Avatar + Interactive Memory Room** (Completed & Verified — 7 Tests Passed)
- **✅ PHASE 8 — Timeline & Relationships + Family Collaboration** (Completed & Verified — 16 Tests Passed)
- **✅ PHASE 9 — Security Hardening, Memory Guardian Evaluation & Research Dashboard** (Completed & Verified — 21 Tests Passed, 188 Total Tests Passed)
- **✅ PHASE 10 — Production Readiness, End-to-End Validation & Operational Hardening** (Completed & Verified — 16 New Integration Tests Passed, 204 Total Tests Passed, 25/25 Frontend Routes Compiled, Operational Backup & Disaster Recovery Validated)



