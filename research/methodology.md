# Research Methodology

## Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation

### 1. Mixed-Methods Design
This research adopts an engineering design science methodology paired with quantitative benchmarking of evidence retrieval and qualitative evaluation of ethical boundaries and user experience.

```
       [ Archival Ingestion & OCR/STT Extraction ]
                          │
                          ▼
            [ Spatiotemporal Graph Grounding ]
                          │
                          ▼
             [ Vector Indexing & Tri-State Tagging ]
                          │
                          ▼
             [ Dual-Pass Guardian Verification ]
                          │
                          ▼
          [ Evidence-Grounded Interactive Interface ]
```

---

### 2. Experimental Stages

#### Phase 1: Foundation & Architectural Proof-of-Concept (Completed)
- Establish modular client-server framework strictly bounded to local storage volume (`D:\ECHO`).
- Implement Pydantic data schemas, repository abstractions, and confidence enums.
- Formulate baseline Memory Guardian safeguards preventing consciousness claims.

#### Phase 2: Secure Multimodal Ingestion (Completed)
- Ingest heterogeneous family memories across 11 life categories with SHA-256 deduplication and AES-256 encrypted storage.
- Granular consent lifecycle management (`MEDIA_PROCESSING`, `AI_PROCESSING`, `VOICE_PROCESSING`, `AVATAR_PROCESSING`, `FAMILY_ACCESS`).
- Tamper-evident queryable audit trails.

#### Phase 3: Multimodal AI Memory Processing (Completed)
- Specialized local media extractors: Image metadata, OCR, Audio STT, Video Keyframes, Document parsing.
- Atomic evidence extraction, named entity recognition (`PERSON`, `LOCATION`, `ORGANIZATION`), and milestone event extraction.
- Granular provenance attachment and tri-state confidence calibration.

#### Phase 4: Memory DNA, Knowledge Graph & Hybrid Retrieval (Completed)
- Structured 22-category Memory DNA synthesis with immutable versioning (`MemoryDNAVersion`).
- Spatiotemporal Knowledge Graph (10 node types, 17 relationship types, duplicate detection, contradiction tracking).
- Configurable text chunking with exact character offsets and deterministic/dense vector embedding index.
- Explainable Hybrid Retrieval combining dense vector similarity ($w_{\text{vec}}=0.5$), keyword matching ($w_{\text{kw}}=0.3$), and graph expansion ($w_{\text{graph}}=0.2$).
- Formal Benchmark Schema definition (`research/benchmark_schema.json`) for quantitative retrieval evaluation.

#### Phase 5: Conversation Engine & Memory Guardian (Completed)
- Conversational RAG response generation strictly grounded in retrieved Phase 4 evidence.
- Dual-pass Memory Guardian validating 100% of generated claims against cited evidence IDs across 18 distinct safety and evidentiary checks.
- Zero-evidence fallback guaranteeing no hallucination when evidence is absent.
- Transparent contradiction disclosure acknowledging historical discrepancies.
- Evaluation hooks for grounded response rate, unsupported claim rate, and latency telemetry.

#### Phase 6: Voice Interaction & Authorized Memorial Voice (Upcoming)
- STT, text-to-speech synthesis with watermarked voice artifacts and strict consent verification.

