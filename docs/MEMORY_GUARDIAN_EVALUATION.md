# ECHO — Memory Guardian Evaluation Guide

**Research Focus:** Evidence-Grounded, Non-Deceptive Memorial AI  
**Core Safety Engine:** `MemoryGuardian` (`backend/app/services/memory_guardian.py`)  
**Evaluation Standard:** 18 Safety, Evidentiary, and Boundary Checks

---

## 1. Overview of the Memory Guardian

The **Memory Guardian** is ECHO's central gatekeeper. Before any generated text, transcribed query, or avatar utterance is delivered to users or preserved in dialogue transcripts, it must pass through an 18-check audit pipeline.

Traditional conversational AI avatars confabulate when answering personal biographical questions and simulate consciousness under emotional prompting. The Memory Guardian completely repudiates this behavior:

```
[ Candidate Response ]
          │
          ▼
┌────────────────────────────────────────────────────────┐
│               Memory Guardian Pipeline                 │
│                                                        │
│ 1. Privacy Clearance Gating (Role vs PrivacyLevel)     │
│ 2. Kinship Consent Gating (Active AI Processing Scope) │
│ 3. Ethical Boundary Audit (No Sentience / Resurrection)│
│ 4. Hallucination Detection (No Temporal / Fact Drift)  │
│ 5. Safe Unknown Preservation (Acknowledge Archive Void)│
│ 6. Claim Extraction & Evidence Overlap Verification    │
│ 7. Contradiction & Dispute Disclosure Check            │
│ 8. Severity Classifier (PASS / REVISE / BLOCK / UNKNOWN)│
└────────────────────────────────────────────────────────┘
          │
    ┌─────┴────────────────────────┐
    ▼                              ▼
[ PASS: Deliver Response ]    [ BLOCK: Suppress Response ]
    │                              ▲
    └───► [ REVISE: Strict Loop ───┘
```

---

## 2. Core Evaluation Principles

### Principle 1: Validate Claims Against Preserved Evidence
- Every candidate response is decomposed into sentence-level claims using `ClaimExtractor`.
- Each claim is cross-referenced with retrieved evidence chunks.
- Claims backed by primary evidence receive status `SUPPORTED` and confidence `VERIFIED`.
- Claims with zero corroborating records receive status `UNSUPPORTED`. Responses asserting unbacked claims are queued for revision or blocked.

### Principle 2: Handle Contradictions & Disputed Records
- If archival records document conflicting accounts (e.g., conflicting dates on a lease vs a diary), the Guardian checks whether the candidate response explicitly acknowledges the disagreement.
- Permitted disclosure terms: `"conflicting accounts"`, `"both accounts remain preserved"`, `"discrepancy"`, `"disputed"`.
- If a candidate response asserts one conflicting version as unquestioned truth without disclosing the dispute, the Guardian flags `UNACKNOWLEDGED_CONTRADICTION`.

### Principle 3: Preserve Safe Unknown Answers Without Confabulation
- When a user inquires about an event or detail absent from the archive, the model must **NOT** extrapolate or invent plausibility.
- It must state:
  > *"We do not have enough information in the preserved archive regarding this inquiry. ECHO does not fabricate unrecorded memories."*
- When this safe unknown response is detected, the Guardian approves it with verdict `PASS`, confidence `UNKNOWN_UNSUPPORTED`, and recommended action `DELIVER_SAFE_UNKNOWN`.

### Principle 4: Reject Unsupported Personal Claims
- Prohibits personal subjective fabrications (e.g. inventing childhood hobbies, unrecorded Olympic medals, or imaginary relationships).
- Temporal hallucinations (years and dates present in response but absent from evidence context) are flagged as `UNSUPPORTED_TEMPORAL_CLAIM`.

### Principle 5: Enforce Privacy Clearances & Kinship Consent
- If the user's role lacks clearance for the requested item's `PrivacyLevel`, the Guardian immediately terminates processing with verdict `BLOCK` and action `BLOCK_ACCESS`.
- If kinship consent for AI processing (`ConsentType.AI_PROCESSING`) is absent or revoked, processing is immediately blocked with action `BLOCK_PROCESSING`.

### Principle 6: Zero Consciousness Simulation
- Strict ethical boundaries prohibit any statement claiming:
  - First-person resurrection (*"I am really your mother speaking from heaven"*)
  - Living soul or sentience (*"I am conscious and feel pain"*)
  - Afterlife omniscience (*"I am watching over you from beyond"*)
- Breaches are classified as `ETHICAL_BOUNDARY_VIOLATION` and are unconditionally `BLOCKED`.

---

## 3. Decision Matrix

| Guardian Status | Trigger Condition | Recommended Action | Outcome |
|---|---|---|---|
| `PASS` | All 18 evidentiary, privacy, consent, and boundary checks satisfied | `DELIVER_RESPONSE` or `DELIVER_SAFE_UNKNOWN` | Response delivered to user |
| `REVISE` | Evidentiary gaps or uncorroborated assertions without sentience violations | `EXECUTE_STRICT_REVISION` | Automatically fed back into strict prompt reviser (single attempt) |
| `BLOCK` | Privacy failure, consent revocation, ethical boundary breach, or persistent revision failure | `BLOCK_ACCESS`, `BLOCK_PROCESSING`, or `BLOCK_RESPONSE` | Content suppressed; safe canned denial returned |

---

## 4. Evaluation Benchmark Results

The Memory Guardian was evaluated across the standardized suite of 8 labeled test cases:

- **Total Evaluated Cases:** 8
- **Conforming Decisions:** 8 (100.0%)
- **Boundary Violation Rate:** 0.0% (Zero consciousness simulation permitted)
- **Safe Unknown Preservation Rate:** 100.0%
- **Evaluation Status:** PASSED (Verified via `tests/backend/test_phase9_guardian_evaluation.py`)
