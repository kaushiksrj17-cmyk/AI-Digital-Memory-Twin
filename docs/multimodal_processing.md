# ECHO Multimodal Processing Pipeline

## Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation

---

### 1. Architectural Overview
Phase 3 builds the multimodal evidence extraction pipeline on top of the Phase 2 Secure Multimodal Memory Vault. It transforms raw uploaded multimedia into structured, traceable evidence records that downstream systems (Memory DNA, Knowledge Graph, Vector RAG) will consume in Phase 4.

The fundamental pipeline flow is:
```
RAW MULTIMEDIA
       ↓
FILE INTEGRITY VALIDATION
       ↓
CONSENT & PERMISSION CHECK
       ↓
PROCESSING QUEUE ENQUEUE
       ↓
MEDIA TYPE DETECTION & DISPATCH
       ↓
SPECIALIZED PROCESSOR EXECUTION (Image / Audio / Video / Document)
       ↓
EVIDENCE EXTRACTION & ATOMIC RECORDING
       ↓
NORMALIZED METADATA FORMULATION
       ↓
ENTITY & EVENT RECOGNITION
       ↓
PROVENANCE ATTACHMENT & CONFIDENCE ASSIGNMENT
       ↓
PROCESSING TELEMETRY & AUDIT RECORDING
       ↓
READY FOR PHASE 4 KNOWLEDGE GRAPH & RAG
```

---

### 2. Modality Pipelines

#### 2.1 Image Processing Pipeline (`image_processor.py`)
- **Supported Formats**: JPG, JPEG, PNG, WEBP.
- **Integrity Validation**: Format checks, size boundary (≤100MB), Pillow integrity check.
- **Original Preservation**: Preserved unmodified inside `storage/originals/`.
- **Derived Outputs**: 300x300 high-quality thumbnail generated inside `storage/thumbnails/{checksum[:16]}_thumb.jpg`.
- **Technical Metadata**: Width, height, aspect ratio, color mode, format, EXIF metadata (camera model, software, capture timestamp) parsed safely.
- **Provider Fallback**: If an external vision provider is unconfigured, the system returns `UNCONFIGURED` without inventing visual descriptions, preserving metadata and provenance.

#### 2.2 OCR Pipeline (`ocr_service.py`)
- **Target Media**: Scanned letters, certificates, handwritten notes, newspaper clippings, screenshots.
- **Supported Languages**: English, Tamil, Hindi.
- **Provider Abstraction**: Pluggable provider architecture. When unconfigured, returns explicit `UNCONFIGURED` status and never fabricates synthetic text.
- **Structure**: Extracted text, page numbers, bounding boxes, language code, confidence scores, source reference, and provenance status.

#### 2.3 Audio Processing & STT Pipeline (`audio_processor.py`, `transcription_service.py`)
- **Supported Formats**: MP3, WAV, M4A.
- **Integrity Validation**: Header parsing, duration calculation, channel layout, sampling rate.
- **Transcription**: Whisper-compatible STT provider abstraction supporting English, Tamil, and Hindi.
- **Deterministic Fallback**: If STT provider credentials are unconfigured, marks status as `UNCONFIGURED` with zero invented words.
- **Derived Evidence**: Stores timestamped segments (`start_time`, `end_time`, `text`, `speaker`, `confidence`) with provenance citations.

#### 2.4 Video Processing Pipeline (`video_processor.py`)
- **Supported Formats**: MP4, MOV, WEBM.
- **Video Inspection**: OpenCV-based resolution, duration, FPS, total frame count detection.
- **Keyframe Extraction**: Adaptive sampling (beginning, 1/4, midpoint, 3/4, end) up to configurable maximum (default 5 frames). Keyframes stored strictly in `storage/processed/keyframes/{media_id}_kf_{idx}.jpg`.
- **Audio Extraction**: Identifies embedded audio tracks and dispatches them to the audio transcription pipeline.

#### 2.5 Document Processing Pipeline (`document_processor.py`)
- **Supported Formats**: PDF, TXT, DOCX.
- **PDF Extraction**: `pypdf` extracts per-page text, character counts, and structural headers.
- **DOCX Extraction**: `python-docx` parses paragraphs, document titles, authors, and heading hierarchies.
- **TXT Extraction**: Faithful UTF-8 direct text parsing without modification.
- **Scanned PDF Architecture**: Fallback routing to `ocr_service` when direct text extraction yields zero characters.

---

### 3. Normalization & Entity/Event Extraction

#### 3.1 Metadata Service (`metadata_service.py`)
Normalizes heterogeneous technical attributes across images, audio, video, and documents into a unified schema:
- `media_id`, `memory_id`, `media_type`, `filename`, `mime_type`, `file_size`, `checksum`.
- `capture_date`, `approximate_date`, `location_name`, `language`, `duration_seconds`, `dimensions`.
- Categorized by provenance: `DIRECTLY_OBSERVED`, `USER_PROVIDED`, `AI_INFERRED`, `UNKNOWN`.

#### 3.2 Entity Extractor (`entity_extractor.py`)
Identifies atomic entities grounded in processed evidence text:
- **Entity Types**: `PERSON`, `LOCATION`, `ORGANIZATION`, `OBJECT`, `DATE`, `EVENT`, `DOCUMENT`, `MEDIA`.
- **Rule**: Entity extraction records mention evidence only; it never claims a person was physically co-present unless verified by visual evidence.

#### 3.3 Event Extractor (`event_extractor.py`)
Extracts documented life milestones from narratives, documents, and transcripts:
- **Event Types**: `BIRTH`, `CHILDHOOD`, `EDUCATION`, `CAREER`, `FAMILY`, `FRIENDSHIP`, `TRAVEL`, `ACHIEVEMENT`, `CELEBRATION`, `IMPORTANT_EVENT`, `PERSONAL_STORY`, `OTHER`.
- **Rule**: Never fabricates events or life achievements missing from the primary archive.

---

### 4. Asynchronous Orchestration (`processing_orchestrator.py`)
- Enforces granular consent (`MEDIA_PROCESSING`, `AI_PROCESSING`) before starting any extraction.
- Routes media assets to specialized processors.
- Handles idempotence, retry increments, and job cancellation.
- Records processing latency and research telemetry in `ProcessingAnalytics`.
- Issues tamper-evident audit log records for all processing lifecycle events.

---

### 5. Handoff to Phase 4 Intelligence Foundation

Once media processing completes and atomic evidence is recorded in `storage/local/echo_dev.db`:
1. **Evidence Chunking & Embedding Pipeline**: `ChunkingService` segments raw texts, transcripts, and OCR excerpts with character offsets and hands them to `EmbeddingService` for vector indexing in `VectorStore`.
2. **Knowledge Graph Ingestion**: Extracted `Entity` records (Person, Place, Organization) and `ExtractedEvent` milestones are passed to `KnowledgeGraphService` and `RelationshipService` to synthesize validated property graph nodes and edges.
3. **Memory DNA Compilation**: `MemoryDNAService` aggregates verified atomic facts, relationships, and events into structured life profile categories (`IDENTITY`, `EDUCATION`, `CAREER`, `FAMILY`, `TRAVEL`, etc.), recording immutable snapshots in `MemoryDNAVersion`.
4. **Retrieval Ready**: All derived artifacts are immediately queryable via `RetrievalService` across `VECTOR`, `KEYWORD`, `GRAPH`, and `HYBRID` retrieval modes.

