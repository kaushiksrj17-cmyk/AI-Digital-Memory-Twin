# ECHO — Memory Contribution Review, Disputes & Version History

**Research Title:** Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation.  
**Project Tagline:** "Preserve the memories. Hear the voice. See the presence. Keep the story alive."

---

## 1. Overview & Research Principles

In historical digital memory preservation, family contributors may have divergent recollections, differing dates for significant life events, or alternative interpretations of photographs and letters.

The ECHO platform treats contributions not as competitive edits that erase prior text, but as **evidence-grounded contributions** managed through a rigorous, auditable review workflow.

### Core Guiding Principles

1. **Non-Destructive Version Preservation**:
   - Original preserved artifacts are never silently overwritten or discarded.
   - Every approved change records prior states in `version_history`.
2. **Mandatory Independent Review (No Self-Approval)**:
   - A contributor cannot approve their own submission (`SelfApprovalViolationError`). Even if a user is an `OWNER` or `FAMILY_ADMIN`, submissions authored by them require approval from another authorized administrator.
3. **Multi-Perspective Dispute Retention**:
   - When contributors provide conflicting evidence, the system refuses to "majority-vote" the truth.
   - Competing dates and accounts are marked `DISPUTED` and preserved side-by-side with full source citations.
4. **Transparent Provenance**:
   - Contributor testimony is clearly distinguished from primary documentary evidence and AI-generated suggestions.

---

## 2. Contribution Lifecycle State Machine

```
                   ┌──────────────┐
                   │    DRAFT     │
                   └──────┬───────┘
                          │ (Submit)
                          ▼
                   ┌──────────────┐
       ┌───────────│  SUBMITTED   │◄──────────────┐
       │           └──────┬───────┘               │
       │ (Withdraw)       │ (Begin Review)        │ (Re-submit after changes)
       ▼                  ▼                       │
┌──────────────┐   ┌──────────────┐               │
│  WITHDRAWN   │   │ UNDER_REVIEW │               │
└──────────────┘   └──┬───┬───┬───┘               │
                      │   │   │                   │
         ┌────────────┘   │   └─────────────┐     │
         ▼                ▼                 ▼     │
  ┌──────────────┐ ┌──────────────┐  ┌──────────────┐
  │   APPROVED   │ │   REJECTED   │  │NEEDS_CHANGES ├──┘
  └──────────────┘ └──────────────┘  └──────────────┘
         │
         ▼ (Contested by competing evidence)
  ┌──────────────┐
  │   DISPUTED   │
  └──────────────┘
```

### Lifecycle States

| State | Definition | Permitted Actions |
|---|---|---|
| `DRAFT` | Initial composition by contributor. Visible only to author. | Edit, Delete, Submit |
| `SUBMITTED` | Formally queued for family review. Read-only for contributor. | Withdraw, Review |
| `UNDER_REVIEW` | Reviewer has claimed the submission and is validating evidence. | Approve, Reject, Request Changes, Mark Disputed |
| `NEEDS_CHANGES` | Reviewer requested corrections or additional evidence. | Contributor edits and re-submits |
| `APPROVED` | Verified by authorized reviewer. Changes applied to timeline/vault/graph. | Dispute, View, Version History |
| `REJECTED` | Proposed addition rejected with reviewer notes explaining reason. | View Reason |
| `DISPUTED` | Retained as contested claim alongside conflicting accounts. | Resolve, View Evidence |
| `WITHDRAWN` | Contributor voluntarily canceled submission prior to decision. | Closed |

---

## 3. Contribution Types Supported

1. **`NEW_MEMORY`**: Proposed new photograph, letter, audio tape, or story with evidentiary context.
2. **`CORRECTION`**: Proposed correction to existing memory descriptions, dates, or transcripts.
3. **`TIMELINE_EVENT`**: Proposed life milestone to be incorporated into the chronological narrative.
4. **`RELATIONSHIP`**: Proposed connection between entities with supporting documentary evidence.
5. **`ALTERNATIVE_DATE`**: Competing calendar date supported by oral testimony or conflicting documentation.
6. **`SUPPORTING_DOCUMENT`**: Additional corroborating artifacts attached to an existing memory record.

---

## 4. The Self-Approval Invariant

To ensure institutional credibility and research validity, self-approval is blocked at the core service level:

```python
# In FamilyService.review_contribution:
if actor_user_id == contrib.contributor_id:
    raise SelfApprovalViolationError(
        "Contributors cannot approve their own submissions. "
        "Independent review is required."
    )
```

This prevents accidental confirmation bias or unilateral modifications, even when the contributor is the archive owner.

---

## 5. Competing Evidence & Dispute Preservation

When two sources claim contradictory facts (for example, whether the subject moved to Chicago in 1968 or 1970):
1. Both timeline events or metadata records are linked in the `dispute_records` array:
   ```json
   {
     "disputed_by": "user-contributor-002",
     "reason": "Family letter dated May 1968 confirms arrival in Chicago two years earlier.",
     "competing_evidence_ids": ["mem-doc-letter-1968"],
     "timestamp": "2026-10-10T08:30:00Z"
   }
   ```
2. The UI renders a distinct amber `DISPUTED` badge.
3. Expanding the event displays both the primary claim and all competing accounts with their respective supporting documents.
4. Neither record is erased; both historical perspectives remain intact for future generations.

---

## 6. Review Workflow UI (`/family/contributions`)

The Contribution Review page (`frontend/src/app/family/contributions/page.tsx`) offers:
- **Queue Filters**: Filter by status (`ALL`, `SUBMITTED`, `UNDER_REVIEW`, `APPROVED`, `DISPUTED`, `REJECTED`).
- **Side-by-Side Comparison**:
  - Original Existing Value vs Proposed Contributed Value.
  - Highlighted evidentiary differences.
- **Evidence & Provenance Inspector**: Displays linked primary source IDs, contributor notes, and AI suggestion tags.
- **Review Decision Console**:
  - `Approve`: Commits the verified record and logs audit trail.
  - `Needs Changes`: Returns to contributor with structured feedback.
  - `Mark Disputed`: Records conflicting evidence without discarding either.
  - `Reject`: Declines the contribution with mandatory review rationale.
- **Immutable Version History Drawer**: Displays complete timeline of prior submissions, reviews, and modifications.
