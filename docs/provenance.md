# ECHO Provenance & Traceability Architecture

## Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation

---

### 1. Fundamental Provenance Principle
In traditional conversational AI systems, answers are generated from ungrounded parametric model weights, creating convincing hallucinations. In ECHO, every statement, entity, event, and memory twin output must be strictly anchored to an identifiable, tamper-evident archival source.

> **ECHO Axiom**: "An assertion without traceable provenance is not a memory; it is an unverified hypothesis."

---

### 2. Four-Tier Provenance Taxonomy

| Provenance Status | Definition | Source Examples | UI Badge / Label |
|---|---|---|---|
| **`DIRECTLY_OBSERVED`** | Directly extracted from primary physical artifacts (scanned letters, unaltered audio tapes, certificates). | Text extracted from a 1968 graduation folio, raw audio frequencies, EXIF timestamp. | `ORIGINAL PRESERVED CONTENT` (Green) |
| **`USER_PROVIDED`** | Explicitly stated or entered by verified family members during vault ingestion. | Memorial subject birthdate entered by a daughter, home address recalled by a spouse. | `USER-PROVIDED` (Sky Blue) |
| **`AI_INFERRED`** | Derived by a machine learning model, regex heuristic, or semantic parser. | Facial recognition tags, OCR entity extraction, topic modeling classification. | `AI-INFERRED` (Indigo) |
| **`UNKNOWN`** | Absent, ambiguous, or unverifiable from preserved evidence. | Missing date of an undated photograph, unidentifiable persons in a group picture. | `UNKNOWN` (Rose) |

---

### 3. Provenance Citation Schema
Every atomic evidence unit (`models.evidence.Evidence`) stores a complete provenance citation block:

```json
{
  "evidence_id": "ev-trinity-1968",
  "memory_id": "mem-graduation-001",
  "media_id": "media-cert-scan-042",
  "source_reference": "Folio 82, Cambridge Archives Registry Box 1",
  "source_type": "DOCUMENT",
  "provenance_status": "DIRECTLY_OBSERVED",
  "confidence": "VERIFIED",
  "confidence_score": 1.0,
  "extraction_method": "direct_document_text_parser",
  "processor_version": "v3.0.0",
  "created_at": "2026-10-08T18:00:00Z"
}
```

---

### 4. Downstream Grounding in RAG & Memory Guardian
In Phase 4 (Vector RAG) and Phase 5 (Memory Guardian):
1. **Retrieval Grounding**: RAG retrievers retrieve only atomic evidence items whose provenance status and confidence pass user-defined thresholds.
2. **Guardian Verification**: The Memory Guardian inspects LLM generation outputs. If an LLM response makes an assertion that cannot be mapped to a supporting `Evidence` citation, the Guardian intercepts and suppresses the statement, replacing it with:
   > *"This information is not present in the preserved archive."*
3. **No Inference Conversion**: An `UNKNOWN` value can never be converted into an AI inference without explicit evidence backing.

---

### 5. Phase 4 End-to-End Traceability Chains

Phase 4 operationalizes end-to-end auditability across the retrieval and knowledge layers:

```
[ Primary Archival Media (storage/originals/) ]
                       ↓
         [ Atomic Evidence Record ]
                       ↓
        ┌──────────────┴──────────────┐
        ▼                             ▼
[ Evidence Chunk ]           [ Knowledge Graph ]
        ↓                       (Node / Edge)
[ Embedding Vector Record ]           ↓
        ↓                     [ Memory DNA Item ]
[ Retrieval Result Item ]
```

1. **Vector-to-Evidence Traceability**: Every vector stored in `VectorStore` (Qdrant or Local) contains a metadata payload linking `vector_id` -> `evidence_id` -> `chunk_id` -> `memory_id` -> `media_id` -> original physical file checksum. Anonymous vectors without source citations are strictly rejected.
2. **Graph-to-Evidence Traceability**: Every relationship edge in `KnowledgeGraphService` contains `source_evidence_ids`. Edges cannot be established by simple proximity or text co-occurrence.
3. **Memory DNA Provenance Inheritance**: Each `MemoryDNAItem` records `source_memory_ids`, `source_media_ids`, and `source_evidence_ids`. A verified DNA fact must trace back to `DIRECTLY_OBSERVED` or `USER_PROVIDED` primary sources.
4. **Explainable Retrieval Scoring**: Every search result item contains a structured `score_breakdown` (`vector_score`, `keyword_score`, `graph_score`, `confidence_bonus`) and an explicit human-readable `why_retrieved` rationale (e.g., *"Matched vector semantic similarity (0.87) and exact keyword match"*).
5. **Conversational Provenance Citations (Phase 5)**: Every generated turn in the conversation engine carries structured `ResponseSource` records. The UI exposes clickable citations that open the Evidence Drawer with source titles, confidence ratings, and excerpt quotes, while strictly obfuscating local server filesystem paths (`D:\ECHO\...`).

