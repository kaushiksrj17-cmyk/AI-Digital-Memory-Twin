# Contradiction Handling & Archival Conflict Transparency

## Overview
Biographical memory archives frequently contain contradictory evidence (e.g., family oral history claiming a subject lived in London in 1968, while a passport or employment record indicates Oxford). Rather than silently picking one source or hallucinating a compromise, ECHO enforces **Archival Conflict Transparency**.

---

## Conflict Detection & Representation
Contradiction records are managed through `backend/app/services/contradiction_service.py` (established in Phase 4 and fully integrated into RAG in Phase 5).

### Example Contradiction Record:
- **Entity**: `Arthur Pendelton`
- **Field / Subject**: `Employer (1975)`
- **Claim A**: `Worked at Acme Engineering` (Source: Family Memoir, Confidence: `MEDIUM`)
- **Claim B**: `Worked at Pacific Marine Co.` (Source: Payroll Receipt, Confidence: `HIGH`)

---

## System Behavior Under Conflict

1. **Anti-Authoritative Stance**:
   The LLM is strictly prohibited from asserting either claim as an unquestioned fact.
   - **Disallowed**: *"Arthur worked at Acme Engineering in 1975."*
   - **Mandatory Archival Phrasing**:
     > *"The preserved archive contains conflicting records regarding his employment in 1975. A family memoir lists Acme Engineering, while an official payroll receipt records Pacific Marine Co."*

2. **UI Contradiction Banner**:
   When conflicting sources back a generated response, the conversation UI displays a prominent amber warning:
   `CONFLICTING SOURCES DETECTED`

3. **Confidence Deduction**:
   The **Confidence Engine** automatically applies an explainable 20% contradiction penalty, preventing contradictory responses from being assigned a `VERIFIED` status without explicit resolution.
