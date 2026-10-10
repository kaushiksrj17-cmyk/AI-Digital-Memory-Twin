# ECHO — Phase 8: AI Life Timeline & Evidence-Grounded Relationship Graph

**Research Title:** Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation.  
**Project Tagline:** "Preserve the memories. Hear the voice. See the presence. Keep the story alive."

---

## 1. Executive Summary & Research Foundations

Phase 8 expands the ECHO Digital Memory Twin from isolated memory artifacts and 3D spatial anchors into a structured, longitudinal **Life Narrative Timeline** and an interconnected, evidence-grounded **Relationship Graph**.

Rather than treating digital memories as disjointed photos or audio clips, Phase 8 models life history as an authentic, verifiable chronological continuum supported by primary source evidence. Relationships between people, events, places, organizations, and memories are explicitly captured with verifiable provenance, confidence classification, and formal dispute tracking.

### Core Non-Negotiable Invariants

1. **Zero-Fabrication Timeline Construction**:
   - Every life event displayed on `/timeline` must trace back to authenticated memory artifacts in the vault (`evidence_ids`, `source_references`).
   - If an event is inferred by AI (via Phase 5 Memory Guardian integration), it is labeled explicitly as `is_ai_suggested: true` and `verification_status: PENDING_REVIEW`.
   - Never infer birth dates, death dates, marriage dates, or sensitive family connections without primary source corroboration.

2. **Evidentiary Date Precision Model**:
   - Historical records inherently vary in temporal certainty. The system preserves five explicit date precisions:
     - `EXACT`: Known down to the specific calendar day (`YYYY-MM-DD`).
     - `MONTH_YEAR`: Known to a month and year, without calendar day certainty (`YYYY-MM`).
     - `YEAR_ONLY`: Known only to a specific calendar year (`YYYY`).
     - `APPROXIMATE`: Estimated based on context or testimony (`circa 1978`), with `is_approximate: true`.
     - `UNKNOWN`: The date is entirely unrecorded or unresolved.
   - The system **never** silently coerces an approximate date into an exact date to satisfy database formats or UI sorting.

3. **Evidence-Grounded Relationship Modeling**:
   - Relationship edges on `/relationships` connect graph entities (`Person`, `Event`, `Memory`, `Place`, `Organization`, etc.) using strongly typed semantics:
     - `RELATED_TO`, `PARENT_OF`, `CHILD_OF`, `SIBLING_OF`, `SPOUSE_OF`, `FRIEND_OF`
     - `STUDIED_AT`, `WORKED_AT`, `VISITED`, `PARTICIPATED_IN`, `ASSOCIATED_WITH`, `MENTIONED_IN`, `DOCUMENTED_BY`, `OCCURRED_AT`, `CONNECTED_TO_MEMORY`
   - Specific family ties (e.g. `PARENT_OF`, `SPOUSE_OF`) are **never** inferred from surname matches, physical proximity in photos, or unverified LLM guesses. They require verified documentary evidence or explicit authorized testimony.

4. **Multi-Perspective Dispute Preservation**:
   - When historical sources or family members disagree on dates, locations, or participants, the system **never** silently overwrites or averages the conflicting facts.
   - The dispute state is elevated (`verification_status: DISPUTED`), preserving conflicting claims, opposing source records, and reviewer notes for historical fidelity.

---

## 2. Life Narrative Timeline Architecture (`/timeline`)

### 2.1 Domain & Data Model

The timeline backend (`backend/app/services/timeline_service.py` & `models/timeline.py`) stores and indexes life events via `TimelineEventRecord`:

```python
class TimelineEvent(BaseModel):
    id: str
    profile_id: str
    title: str
    description: str
    category: str                   # Childhood, Education, Career, Family, Friends, Travel, Achievements, etc.
    start_date: str                 # ISO date string or year
    end_date: Optional[str]
    date_precision: DatePrecision   # EXACT, MONTH_YEAR, YEAR_ONLY, APPROXIMATE, UNKNOWN
    is_approximate: bool
    confidence: ConfidenceLevel     # HIGH, MEDIUM, LOW
    confidence_score: float
    verification_status: VerificationStatus # VERIFIED, PENDING_REVIEW, DISPUTED, REJECTED
    evidence_ids: List[str]
    source_references: List[str]
    people_involved: List[str]
    places: List[str]
    is_ai_suggested: bool
    ai_suggestion_rationale: Optional[str]
    dispute_records: List[Dict[str, Any]]
```

### 2.2 Event Categories Supported

- **Childhood**: Early life milestones, school beginnings, childhood residences.
- **Education**: Primary, secondary, collegiate, apprenticeship, and academic accomplishments.
- **Career**: Employment milestones, founding organizations, promotions, professional retirement.
- **Family**: Marriages, births, family reunions, ancestral migrations.
- **Friends**: Lifelong friendships, shared journeys, community gatherings.
- **Travel**: Documented voyages, expeditions, relocations, vacations.
- **Achievements**: Awards, publications, civic contributions, major personal projects.
- **Special events**: Anniversaries, commemorations, life celebrations.
- **Hobbies and interests**: Music, gardening, woodworking, athletic pursuits, creative arts.
- **Personal stories**: Documented oral histories, letters, journal reflections.
- **Other documented events**: Miscellaneous corroborated historical facts.

### 2.3 Chronological Ordering and Sorting Engine

The timeline engine normalizes date strings for deterministic chronological and reverse-chronological ordering:
- Sort keys extract numerical 4-digit years, 2-digit months, and 2-digit days.
- Year-only events (`"1974"`) sort cleanly alongside exact dates (`"1974-06-15"`).
- Unknown or unresolved dates sort gracefully at the end of chronological sequences with an `UNKNOWN_DATE` badge.
- Events are grouped by year with expandable visual spines.

### 2.4 Integration with Phase 7 3D Memory Room

Every timeline event linked to a vault memory record displays a direct `"Enter 3D Memory Room"` link (`/memory-room?focus={memory_id}`). When clicked, the 3D spatial room automatically positions the user's camera in front of the corresponding 3D photo frame or document pedestal.

---

## 3. Interactive Relationship Graph (`/relationships`)

### 3.1 Graph Topology & Entity Schema

The relationship graph reuses and extends the Phase 4 Memory DNA knowledge graph (`backend/app/services/relationship_service.py` & `models/relationship.py`):

- **Graph Nodes**:
  - `PERSON`: Subject, family members, colleagues, friends.
  - `MEMORY`: Vault memory artifacts (photographs, voice recordings, documents).
  - `EVENT`: Documented life milestones.
  - `PLACE`: Geographic cities, family homes, universities, travel destinations.
  - `ORGANIZATION`: Universities, employers, civic associations.
  - `DOCUMENT`: Legal certificates, letters, newspaper clippings.
  - `MEDIA`: Audio tapes, video recordings, physical photo prints.

- **Graph Edges**:
  - Strongly typed relationship semantics connecting source and target nodes.
  - Edge verification status (`VERIFIED`, `PENDING_REVIEW`, `DISPUTED`, `REJECTED`).
  - Evidence references, confidence scores, creator attribution, and audit timestamps.

### 3.2 Duplicate Entity Detection & Merge Engine

Historical archives often contain duplicate entries created under varying names (e.g., `"Eleanor Vance"` vs `"Eleanor V."` or `"Grandma Eleanor"`).
The relationship service implements a fuzzy token overlap and abbreviation detector:

```python
# Abbreviation & Token Overlap Detection
norm1 = re.sub(r"[^a-z0-9\s]", "", label1.lower()).split()
norm2 = re.sub(r"[^a-z0-9\s]", "", label2.lower()).split()
# Detects: "eleanor vance" & "eleanor v" -> Score: 0.85
```

When potential duplicates are detected:
1. They are presented on `/relationships` in the **Duplicate Resolution Drawer**.
2. Authorized reviewers (`OWNER` or `FAMILY_ADMIN`) can execute an **Entity Merge**:
   - Re-routes all incoming and outgoing graph edges to the canonical entity.
   - Merges aliases, evidence references, and linked memories.
   - Deletes the redundant entity safely without breaking graph integrity.

### 3.3 Graph Interface & Universal Fallback

- **Interactive SVG Visualizer**:
  - Real-time zoom, pan, and center reset controls.
  - Force-directed layout positioning nodes by entity type with curated aesthetic color-coding.
  - Edge click opens detailed **Relationship Evidence Drawer** showing provenance and confidence.
  - Direct dispute submission modal for contested connections.
- **Accessible Table Fallback**:
  - Users with screen readers or low-bandwidth connections can toggle to the **Relational Table View**, presenting all nodes, types, connected edges, and verification statuses in clean semantic HTML.

---

## 4. API Endpoints Reference

| Route | Method | Roles Permitted | Description |
|---|---|---|---|
| `/api/v1/timeline` | `GET` | All | List life events with category, search, and date filters |
| `/api/v1/timeline` | `POST` | `CONTRIBUTOR`, `ADMIN`, `OWNER` | Create life event (marked PENDING_REVIEW unless ADMIN) |
| `/api/v1/timeline/{id}` | `GET` | All | Retrieve timeline event details with evidence links |
| `/api/v1/timeline/{id}` | `PUT` | `CONTRIBUTOR`, `ADMIN`, `OWNER` | Update life event metadata |
| `/api/v1/timeline/{id}/verify` | `POST` | `FAMILY_ADMIN`, `OWNER` | Approve or reject event verification status |
| `/api/v1/timeline/{id}/dispute` | `POST` | `CONTRIBUTOR`, `ADMIN`, `OWNER` | Submit competing evidence or dispute |
| `/api/v1/timeline/suggestions/generate` | `POST` | `FAMILY_ADMIN`, `OWNER` | Trigger Memory Guardian AI event suggestion pipeline |
| `/api/v1/relationships/graph` | `GET` | All | Retrieve full relationship graph with node/edge details |
| `/api/v1/relationships/edges/{id}` | `GET` | All | Inspect relationship edge evidence and confidence |
| `/api/v1/relationships/edges/{id}/verify`| `POST` | `FAMILY_ADMIN`, `OWNER` | Verify or reject relationship connection |
| `/api/v1/relationships/edges/{id}/dispute`| `POST` | `CONTRIBUTOR`, `ADMIN`, `OWNER` | Record dispute on relationship connection |
| `/api/v1/relationships/duplicates` | `GET` | `FAMILY_ADMIN`, `OWNER` | Discover potential duplicate entity candidates |
| `/api/v1/relationships/merge` | `POST` | `FAMILY_ADMIN`, `OWNER` | Merge duplicate entity into canonical entity |
