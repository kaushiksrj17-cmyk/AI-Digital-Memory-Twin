# Contradiction Detection & Tracking Model

## 1. Context & Motivation

Heterogeneous personal archives frequently contain contradictory evidence:
- A handwritten diary states a milestone occurred in 1952.
- An official employment registry lists the date as 1953.
- Oral histories may describe conflicting locations for the same event.

In conventional RAG systems, the model arbitrarily picks one claim or hallucinates a blend. In ECHO:
- **Neither claim is silently discarded.**
- A structured `ContradictionRecord` is created.
- Both claims preserve their respective sources and confidence scores.

---

## 2. Contradiction Schema

```json
{
  "contradiction_id": "uuid",
  "memorial_profile_id": "default-profile-001",
  "subject": "Employment in 1985",
  "claim_a": "Employed at Shell Oil in Aberdeen",
  "claim_b": "Employed at British Petroleum in London",
  "source_a": "Resume document 1988",
  "source_b": "Letter from cousin 1985",
  "confidence_a": 0.90,
  "confidence_b": 0.80,
  "status": "OPEN",
  "notes": "Requires trustee corroboration",
  "created_at": "2026-10-08T10:00:00Z",
  "resolved_at": null
}
```

---

## 3. Lifecycle States

1. `OPEN`: Contradiction detected during evidence processing.
2. `UNDER_REVIEW`: Flagged for family guardian or trustee inspection.
3. `RESOLVED`: Reconciled through primary corroborating document or authorized decision.
4. `UNRESOLVED`: Irreconcilable historical ambiguity documented as permanent archive note.
