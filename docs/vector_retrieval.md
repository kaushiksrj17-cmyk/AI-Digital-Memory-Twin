# ECHO Vector Retrieval & Indexing Architecture

## 1. Overview

The **ECHO Vector Retrieval** layer indexes dense representations of textual evidence extracted from:
- Primary memory titles, descriptions, and narratives
- Document OCR transcriptions
- Audio speech-to-text transcriptions
- Keyframe visual scene descriptions
- Named entity summaries
- Structured Memory DNA items

Compatibility:
- Production target: **Qdrant** vector database (collection-partitioned, filtered HNSW).
- Development fallback: **LocalVectorStore** (in-memory cosine similarity with metadata preservation), enabling zero-dependency local operation.

---

## 2. Evidence Chunking

Long texts, archival documents, and oral transcripts are partitioned via `ChunkingService`:
- Window size: configurable (default 400 characters)
- Overlap: configurable (default 50 characters)
- Boundaries: cleanly aligned to sentence/word margins
- Provenance: preserves exact character offsets (`start_offset`, `end_offset`), `media_id`, `memory_id`, and `evidence_id`.

---

## 3. Vector Traceability & Safety

> [!IMPORTANT]
> **No Anonymous Vectors**:
> Every indexed vector payload strictly contains:
> - `vector_id`: Unique identifier
> - `memory_id`, `media_id`, `evidence_id`, `chunk_id`
> - `content_type`: EVIDENCE / MEMORY_CHUNK
> - `text`: Granular evidence excerpt
> - `provenance_status`: DIRECTLY_OBSERVED / USER_PROVIDED / AI_INFERRED
> - `confidence`: VERIFIED / SUPPORTED_INFERENCE / UNKNOWN_UNSUPPORTED
> - `privacy_level`: PRIVATE / FAMILY / AUTHORIZED_USERS

### Privacy Protection
Sensitive credentials, private system keys, and passwords are automatically sanitized and never embedded.
Private memorial records are strictly gated behind backend authorization before vector retrieval.

---

## 4. Vector Retrieval in Phase 5 Evidence-Grounded RAG
In Phase 5, vector retrieval operates within the multi-source `ContextManager` pipeline:
- Hybrid scoring combines dense vector cosine similarity with exact BM25 keyword matching.
- Vectors from chunks with `UNKNOWN_UNSUPPORTED` confidence or revoked consent are rejected before prompt injection.
- Explainable score components (`semantic_score`, `keyword_score`, `graph_score`, `confidence_bonus`) are exposed in the retrieval drawer.

