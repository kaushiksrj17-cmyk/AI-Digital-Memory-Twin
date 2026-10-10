# ECHO Evidence Record Model & Data Architecture

## Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation

---

### 1. Evidence Record Concept
In ECHO, memories are composite entities composed of atomic, immutable **Evidence Records**. An evidence record represents a discrete extracted fact, media derivative, segment transcript, or technical observation produced during Phase 3 processing.

---

### 2. Evidence Types (14 Modality Archetypes)

| Evidence Type | Description | Source Modality |
|---|---|---|
| `TEXT` | Raw extracted body text from verified text documents or memoirs. | TXT, DOCX, Text PDF |
| `OCR_TEXT` | Optical character recognition text extracted from scanned images. | Scanned PNG, JPG, PDF |
| `TRANSCRIPT` | Spoken language transcript with start/end millisecond timestamps. | MP3, WAV, M4A, Video Audio |
| `IMAGE_METADATA` | Physical image dimensions, color profiles, camera EXIF tags. | JPG, PNG, WEBP |
| `VISUAL_OBJECT` | Identified inanimate or biological objects in visual frames. | Images, Video Keyframes |
| `VISUAL_SCENE` | Environmental scene description (e.g., "mountain path", "study"). | Images, Video Keyframes |
| `VIDEO_KEYFRAME` | Representative video frame stored as derivative image. | MP4, MOV, WEBM |
| `ENTITY` | Extracted named individual, location, date, or organization. | Any text or transcript |
| `EVENT` | Documented life milestone with categorical tagging. | Narratives, Documents |
| `LOCATION` | Spatiotemporal geographic anchor with coordinates or names. | EXIF GPS, Document text |
| `DATE` | Temporal timestamp or approximate historical era anchor. | EXIF, Document dates |
| `AUDIO_METADATA` | Acoustic metrics: sample rate, duration, channel configuration. | MP3, WAV, M4A |
| `VIDEO_METADATA` | Stream metrics: resolution, framerate, total frames, codecs. | MP4, MOV, WEBM |
| `DOCUMENT_METADATA`| Document metadata: page count, headings, author, title. | PDF, DOCX |

---

### 3. Entity & Event Data Models

#### 3.1 Named Entity Model (`Entity`)
- `id`: Unique identifier (`ent-...`).
- `entity_type`: `PERSON`, `LOCATION`, `ORGANIZATION`, `OBJECT`, `DATE`, `EVENT`, `DOCUMENT`, `MEDIA`.
- `value`: Normalized string representation (e.g., "Cambridge University", "June 1968").
- `source_media_id`, `source_memory_id`: Provenance linkage.
- `provenance_status`: Typically `AI_INFERRED` or `DIRECTLY_OBSERVED`.
- `confidence`: Tri-state rating (`VERIFIED`, `SUPPORTED_INFERENCE`, `UNKNOWN_UNSUPPORTED`).
- `extraction_method`: Specific regex heuristic or NLP pipeline.

#### 3.2 Documented Life Event Model (`ExtractedEvent`)
- `id`: Unique identifier (`evt-...`).
- `title`: Event headline (e.g., "Graduation from Cambridge University").
- `description`: Narrative context from primary text.
- `event_type`: Milestone category:
  - `BIRTH`, `CHILDHOOD`, `EDUCATION`, `CAREER`, `FAMILY`, `FRIENDSHIP`
  - `TRAVEL`, `ACHIEVEMENT`, `CELEBRATION`, `IMPORTANT_EVENT`, `PERSONAL_STORY`, `OTHER`
- `date`, `approximate_date`: Temporal anchors.
- `location`: Geographic anchor.
- `people`: Associated individuals mentioned in the source context.

---

### 4. Database Schema & Indexing Strategy
Implemented across SQLAlchemy models in `database/models.py` compatible with SQLite (local development) and PostgreSQL (production):
- **Indexed Fields**:
  - `memory_id` (B-Tree index for sub-millisecond retrieval of all evidence per memory)
  - `media_id` (B-Tree index for media-to-evidence lookups)
  - `evidence_type` (Categorical filtering)
  - `provenance_status` (Grounding filtering)
  - `confidence` (Tri-state rating queries)
  - `created_at` (Timeline ordering)

These indexes guarantee instantaneous lookups during Phase 4 Knowledge Graph ingestion and vector embedding chunking.

---

### 5. Phase 4 Intelligence Foundation Models

In Phase 4, atomic Evidence Records are organized into higher-level retrieval and structural primitives:

#### 5.1 Evidence Chunks (`evidence_chunks`)
- `chunk_id`: Unique chunk identifier (`chk-...`).
- `memory_id`, `media_id`, `evidence_id`: Complete provenance chain.
- `chunk_index`: Zero-based sequential offset within document/transcript.
- `text`: Discrete text segment (typically 500 chars, 50 char overlap).
- `start_char`, `end_char`: Exact character offsets in parent text.
- `source_reference`, `provenance_status`, `confidence`: Immutable provenance block.

#### 5.2 Embedding Records (`embedding_records`)
- `record_id`: Unique embedding record ID (`emb-...`).
- `vector_id`: Corresponding ID in the vector database index.
- `evidence_id`, `chunk_id`, `memory_id`, `memorial_profile_id`: Traceability back to source.
- `content_type`: Category of embedded text (`EVIDENCE_CHUNK`, `MEMORY_DNA_ITEM`, `EVENT`, etc.).
- `model_name`, `dimension`: Embedding model identifier and vector dimensionality.
- `is_mock`: Boolean flag explicitly indicating mock development vectors (`DEVELOPMENT / MOCK EMBEDDING`).

#### 5.3 Knowledge Graph (`graph_nodes` & `graph_relationships`)
- **Nodes**: 10 node archetypes (`PERSON`, `MEMORY`, `EVENT`, `PLACE`, `OBJECT`, `DOCUMENT`, `MEDIA`, `ORGANIZATION`, `DATE`, `TOPIC`).
- **Edges**: 17 relationship types (`RELATED_TO`, `APPEARED_IN`, `PARTICIPATED_IN`, `ASSOCIATED_WITH`, `OWNED`, `DOCUMENTS`, `CONTAINS`, `PROVIDES_EVIDENCE_FOR`, `OCCURRED_AT`, `INVOLVES`, `OCCURRED_ON`, `STUDIED_AT`, `WORKED_AT`, `INTERESTED_IN`, `ABOUT`, `APPEARS_IN`, `OTHER`).
- **Edge Metadata**: `relationship_id`, `source_evidence_ids`, `confidence`, `provenance_status`, timestamps.

#### 5.4 Memory DNA Structure (`memory_dna` & `memory_dna_items`)
- **Categories**: 22 life information categories (`IDENTITY`, `FAMILY`, `RELATIONSHIPS`, `CHILDHOOD`, `EDUCATION`, `CAREER`, `FRIENDS`, `HOBBIES`, `INTERESTS`, `TRAVEL`, `ACHIEVEMENTS`, `IMPORTANT_EVENTS`, `PLACES`, `IMPORTANT_OBJECTS`, `DOCUMENTED_PREFERENCES`, `DOCUMENTED_VALUES`, `KNOWN_PHRASES`, `FREQUENT_TOPICS`, `PERSONAL_STORIES`, `LEGACY`, `UNKNOWN`, `OTHER`).
- **Item Fields**: `dna_item_id`, `category`, `key`, `value`, `description`, `source_memory_ids`, `source_media_ids`, `source_evidence_ids`, `provenance_status`, `confidence`, `confidence_score`.
- **Versioning**: Preserves immutable snapshots across revisions in `memory_dna_versions`.

#### 5.5 Contradiction Records (`contradictions`)
- `contradiction_id`, `subject`, `claim_a`, `claim_b`, `source_a`, `source_b`, `confidence_a`, `confidence_b`, `status` (`OPEN`, `UNDER_REVIEW`, `RESOLVED`, `UNRESOLVED`).

#### 5.6 Conversational Evidence Entities (Phase 5)
- **`ResponseClaim` (`response_claims`)**: Discrete assertion parsed from conversational responses mapped to `supporting_evidence_ids` with `ClaimStatus` (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, `CONTRADICTED`, `UNKNOWN`).
- **`ResponseSource` (`response_sources`)**: Verified, clickable source citation backing generated text without leaking local storage paths.
- **`GuardianResult` (`guardian_results`)**: 18-check validation record (`PASS`, `REVISE`, `BLOCK`, `UNKNOWN`) linked to conversation turn.
- **`ConversationMetricRecord` (`conversation_metrics`)**: Telemetry record logging retrieval latency, generation latency, evidence count, and claim support breakdown.

