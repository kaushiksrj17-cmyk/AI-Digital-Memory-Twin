# ECHO Memory DNA — Architecture & Specification

## 1. Executive Summary

**Memory DNA** is an evidence-grounded, structured representation of documented life facts, milestones, relationships, and verified experiences.

> [!IMPORTANT]
> **Ethical Boundary**: Memory DNA is **NOT** a personality simulator, a psychological diagnosis, a consciousness model, or a claim of resurrection. It never fabricates personality traits, unrecorded dialogue, or imaginary memories. Missing information strictly remains **UNKNOWN**.

---

## 2. Controlled Category Schema

Memory DNA organizes personal knowledge into 22 controlled categories:

1. `IDENTITY`: Documented name, legal identity, birth year, documented citizenship.
2. `FAMILY`: Documented parents, children, siblings, kinship records.
3. `RELATIONSHIPS`: Mentors, colleagues, documented life companions.
4. `CHILDHOOD`: Primary schools, places lived, family home recollections.
5. `EDUCATION`: Verified degrees, diplomas, institutions, academic honors.
6. `CAREER`: Documented employers, positions held, industry contributions.
7. `FRIENDS`: Documented acquaintances, comrades, correspondences.
8. `HOBBIES`: Documented leisure activities (e.g., sailing, gardening, chess).
9. `INTERESTS`: Documented academic, cultural, or artistic pursuits.
10. `TRAVEL`: Verified journeys, voyages, geographic visits.
11. `ACHIEVEMENTS`: Awards, patents, publications, recognitions.
12. `IMPORTANT_EVENTS`: Milestones, celebrations, graduations, weddings.
13. `PLACES`: Specific cities, residences, workplaces, libraries.
14. `IMPORTANT_OBJECTS`: Family heirlooms, diaries, keepsakes, musical instruments.
15. `DOCUMENTED_PREFERENCES`: Explicitly stated likes, dislikes, habits (never inferred).
16. `DOCUMENTED_VALUES`: Documented life philosophies, mottos, writings.
17. `KNOWN_PHRASES`: Repeated spoken phrases or quotes found in audio transcripts.
18. `FREQUENT_TOPICS`: Topics recurring across multiple preserved documents.
19. `PERSONAL_STORIES`: Long-form narratives told by the memorial subject or family.
20. `LEGACY`: Memorial endowments, scholarship funds, commemorative works.
21. `UNKNOWN`: Explicitly acknowledged unrecorded or disputed aspects.

---

## 3. Data Structure

```json
{
  "dna_item_id": "uuid",
  "memorial_profile_id": "default-profile-001",
  "category": "EDUCATION",
  "key": "degree",
  "value": "Natural Sciences Tripos",
  "description": "Graduated from Cambridge University in 1972",
  "source_memory_ids": ["mem-001"],
  "source_evidence_ids": ["ev-cert-001"],
  "provenance_status": "DIRECTLY_OBSERVED",
  "confidence": "VERIFIED",
  "confidence_score": 1.0,
  "verification_status": "VERIFIED",
  "created_at": "2026-10-08T10:00:00Z",
  "updated_at": "2026-10-08T10:00:00Z"
}
```

---

## 4. Versioning and Reproducibility

Memory DNA is versioned deterministically (`MemoryDNAVersion`). When new evidence changes or enriches a documented fact:
- The previous state is preserved in historical snapshots (`dna_snapshot`).
- Change reason and actor are audited (`changed_by`, `change_reason`).
- No silent overwrites occur, ensuring scientific reproducibility.

---

## 5. Integration into Phase 5 Conversational Engine
In Phase 5, verified Memory DNA attributes serve as Tier 1 conversational grounding context. When a user asks questions regarding core identity, education, career, or verified tastes (e.g., *"What were his main interests?"*), `ContextManager` extracts matching `MemoryDNAItem` records and injects them into the bounded system prompt. Unrecorded or `UNKNOWN` items are strictly excluded from factual premises.

