# Hallucination Detection & Identity Boundary Enforcement

## Overview
The **Hallucination Detector** (`backend/app/services/hallucination_detector.py`) is a specialized evidentiary audit component in the Memory Guardian subsystem. It guarantees that generated responses never invent biographical facts, synthesize fictional dates or relationships, or usurp the first-person identity of the memorial subject.

---

## Detection Capabilities

1. **Identity Usurpation Detection**:
   - Detects and strictly flags first-person statements (`"I remember"`, `"I was"`, `"When I was alive"`, `"I loved"`).
   - Rejects statements assuming the voice, consciousness, or living experience of the deceased.
   - Enforces objective, third-person archival perspective (`"The preserved archive records that..."`).

2. **Sentience Simulation Detection**:
   - Detects claims of living emotion, spirit, or afterlife perception (`"I feel in my heart"`, `"I am watching over you"`, `"My soul knows"`).
   - Flags attempts to simulate sentience or spiritual awareness.

3. **Temporal & Milestone Grounding**:
   - Extracts all explicit years (e.g., `1974`, `1985`, `2018`) and validates that each year exists in retrieved primary evidence chunks.
   - Invented years immediately trigger a hallucination violation.

4. **Missing Evidence Invariant**:
   - Detects whether generated claims exceed the factual bounds of the retrieved evidence context.
   - When evidence is empty or insufficient, verifies that the system emits the standardized non-invent statement:
     > *"I don't have enough information in the preserved archive to answer that accurately."*

---

## Method Output Schema

```json
{
  "is_hallucinated": false,
  "detector_method": "ECHO_HYBRID_FACT_CHECKER_V5",
  "confidence": 0.95,
  "flagged_claims": [],
  "violations": []
}
```

If `is_hallucinated` is `true`, the violations list is submitted to the **Memory Guardian** for revision or blocking.
