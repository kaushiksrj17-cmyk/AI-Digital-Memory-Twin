"""Timeline Service for Chronological AI Life Journey in ECHO.

Orchestrates Phase 8 Life Timeline:
- Chronological and reverse-chronological event querying
- Evidentiary
 date precision preserving exactness (EXACT, MONTH_YEAR, YEAR_ONLY, APPROXIMATE, UNKNOWN)
- Multi-criteria filtering by category, person, source type, and date interval
- Conflict and dispute tracking without erasing competing evidence
- AI event suggestion generation strictly validated by Phase 5 Memory Guardian
- Integration with Phase 7 3D Memory Room anchors
- Audit trail recording and research metrics calculation
"""

import time
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timezone
from uuid import uuid4

from models.timeline import (
    TimelineEvent,
    TimelineEventCreate,
    TimelineEventUpdate,
    TimelineFilterParams,
    TimelineResponse,
    TimelineDisputeRequest,
    TimelineVerifyRequest,
)
from models.enums import (
    ConfidenceLevel,
    VerificationStatus,
    DatePrecision,
    SourceType,
    ProvenanceStatus,
    AuditAction,
    GuardianDecision,
)
from backend.app.services.audit_service import audit_service
from backend.app.services.memory_service import memory_service
from backend.app.services.memory_guardian import MemoryGuardian


class TimelineService:
    """Manages life timeline events, disputes, and Memory Guardian suggestions."""

    def __init__(self):
        self._events: Dict[str, TimelineEvent] = {}
        self._init_foundation_events()

    def _init_foundation_events(self):
        """Seed representative verified, approximate, and disputed life events."""
        event_1 = TimelineEvent(
            id="event-001",
            memorial_profile_id="demo-profile-001",
            title="Birth in Edinburgh",
            description="Born at Royal Infirmary; verified by Scottish General Register Office archival extract.",
            category="Childhood",
            event_date=date(1946, 3, 14),
            date_description="March 14, 1946",
            date_precision=DatePrecision.EXACT,
            location_name="Edinburgh, Scotland",
            associated_people=["Eleanor Vance"],
            associated_people_ids=["demo-person-001"],
            linked_memory_ids=[],
            evidence_ids=["demo-doc-001"],
            source_type=SourceType.DOCUMENT,
            confidence=ConfidenceLevel.VERIFIED,
            confidence_score=1.0,
            verification_status=VerificationStatus.VERIFIED,
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            is_ai_suggested=False,
            is_disputed=False,
            memory_room_object_id=None,
            created_by_user_id="demo-user-001"
        )

        event_2 = TimelineEvent(
            id="event-002",
            memorial_profile_id="demo-profile-001",
            title="University Matriculation at Cambridge",
            description="Entered Trinity College to study Modern Literature. Archival ledger registration.",
            category="Education",
            event_date=date(1964, 10, 1),
            date_description="October 1964",
            date_precision=DatePrecision.MONTH_YEAR,
            location_name="Cambridge, UK",
            associated_people=["Prof. Harold Davies"],
            associated_people_ids=["demo-person-003"],
            linked_memory_ids=[],
            evidence_ids=["demo-doc-002"],
            source_type=SourceType.DOCUMENT,
            confidence=ConfidenceLevel.VERIFIED,
            confidence_score=0.95,
            verification_status=VerificationStatus.VERIFIED,
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            is_ai_suggested=False,
            is_disputed=False,
            memory_room_object_id=None,
            created_by_user_id="demo-user-001"
        )

        event_3 = TimelineEvent(
            id="event-003",
            memorial_profile_id="demo-profile-001",
            title="Conferred Master of Arts in Literature",
            description="Conferred MA in Literature at Wren Library courtyard ceremony; commemorated by family photographs.",
            category="Education",
            event_date=date(1968, 6, 22),
            date_description="June 22, 1968",
            date_precision=DatePrecision.EXACT,
            location_name="Cambridge, UK",
            associated_people=["Eleanor Vance", "Arthur Vance"],
            associated_people_ids=["demo-person-001", "demo-person-002"],
            linked_memory_ids=["demo-mem-001"],
            evidence_ids=["demo-doc-001"],
            source_type=SourceType.ORIGINAL_PHOTO,
            confidence=ConfidenceLevel.VERIFIED,
            confidence_score=0.98,
            verification_status=VerificationStatus.VERIFIED,
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            is_ai_suggested=False,
            is_disputed=False,
            memory_room_object_id="desk_graduation_portrait_1968",
            created_by_user_id="demo-user-001"
        )

        event_4 = TimelineEvent(
            id="event-004",
            memorial_profile_id="demo-profile-001",
            title="Wedding Ceremony in Oxford",
            description="Solemnized marriage in Oxford; commemorated with handwritten service order and guestbook.",
            category="Family",
            event_date=date(1970, 7, 18),
            date_description="July 18, 1970",
            date_precision=DatePrecision.EXACT,
            location_name="Oxford, UK",
            associated_people=["Arthur Vance"],
            associated_people_ids=["demo-person-002"],
            linked_memory_ids=["demo-mem-001"],
            evidence_ids=["demo-doc-001"],
            source_type=SourceType.DOCUMENT,
            confidence=ConfidenceLevel.VERIFIED,
            confidence_score=0.99,
            verification_status=VerificationStatus.VERIFIED,
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            is_ai_suggested=False,
            is_disputed=False,
            memory_room_object_id=None,
            created_by_user_id="demo-user-001"
        )

        event_5 = TimelineEvent(
            id="event-005",
            memorial_profile_id="demo-profile-001",
            title="Summer Sailing on Lake Windermere",
            description="Family holiday sailing excursion aboard wooden dinghy. Recorded in personal travel journal.",
            category="Travel",
            event_date=date(1974, 8, 14),
            date_description="circa Mid-August 1974",
            date_precision=DatePrecision.APPROXIMATE,
            location_name="Lake District, England",
            associated_people=["Arthur Vance"],
            associated_people_ids=["demo-person-002"],
            linked_memory_ids=["demo-mem-002"],
            evidence_ids=["demo-doc-002"],
            source_type=SourceType.DOCUMENT,
            confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
            confidence_score=0.82,
            verification_status=VerificationStatus.PENDING_REVIEW,
            provenance_status=ProvenanceStatus.USER_PROVIDED,
            is_ai_suggested=False,
            is_disputed=False,
            memory_room_object_id="bookshelf_travel_journal_windermere",
            created_by_user_id="demo-user-001"
        )

        event_6 = TimelineEvent(
            id="event-006",
            memorial_profile_id="demo-profile-001",
            title="Scottish Highlands Exploration (Disputed Date)",
            description="Extended trek across Cairngorms. Contradictory archival dates documented between journal entry and album caption.",
            category="Travel",
            event_date=date(1982, 8, 10),
            date_description="Disputed: August 1982 vs July 1981",
            date_precision=DatePrecision.APPROXIMATE,
            location_name="Highlands, Scotland",
            associated_people=["Arthur Vance"],
            associated_people_ids=["demo-person-002"],
            linked_memory_ids=[],
            evidence_ids=["demo-doc-001"],
            source_type=SourceType.DOCUMENT,
            confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
            confidence_score=0.70,
            verification_status=VerificationStatus.PENDING_REVIEW,
            provenance_status=ProvenanceStatus.USER_PROVIDED,
            is_ai_suggested=False,
            is_disputed=True,
            dispute_notes="Letter correspondence dates excursion to August 1982; family photo album handwritten caption notes July 1981. Both preserved.",
            competing_evidence_ids=["demo-doc-001", "demo-doc-002"],
            created_by_user_id="demo-user-001"
        )

        for ev in [event_1, event_2, event_3, event_4, event_5, event_6]:
            self._events[ev.id] = ev

    async def get_timeline(self, params: TimelineFilterParams) -> Tuple[TimelineResponse, float]:
        """Retrieve filtered, ordered timeline events with retrieval latency tracking."""
        start_time = time.perf_counter()
        
        events = list(self._events.values())
        
        # Profile filter
        events = [e for e in events if e.memorial_profile_id == params.memorial_profile_id]

        # Category filter
        if params.category:
            cat_norm = params.category.strip().lower()
            events = [e for e in events if e.category.lower() == cat_norm]

        # Source type filter
        if params.source_type:
            events = [e for e in events if e.source_type == params.source_type]

        # Person filter
        if params.person:
            p_query = params.person.lower()
            events = [
                e for e in events
                if any(p_query in p.lower() for p in e.associated_people) or
                   any(p_query in pid.lower() for pid in e.associated_people_ids)
            ]

        # Year range filter
        if params.year_from:
            events = [e for e in events if e.event_date and e.event_date.year >= params.year_from]
        if params.year_to:
            events = [e for e in events if e.event_date and e.event_date.year <= params.year_to]

        # Confidence filter
        if params.confidence:
            events = [e for e in events if e.confidence == params.confidence]

        # Verification status filter
        if params.verification_status:
            events = [e for e in events if e.verification_status == params.verification_status]

        # AI suggestions toggle
        if not params.include_ai_suggested:
            events = [e for e in events if not e.is_ai_suggested]

        # Disputed toggle
        if not params.include_disputed:
            events = [e for e in events if not e.is_disputed]

        # Text search
        if params.search_query:
            sq = params.search_query.lower()
            events = [
                e for e in events
                if sq in e.title.lower() or
                   sq in (e.description or "").lower() or
                   sq in (e.location_name or "").lower() or
                   any(sq in p.lower() for p in e.associated_people)
            ]

        # Sort order: Exact / dated items sorted by event_date, unknown dates placed predictably
        def _sort_key(ev: TimelineEvent):
            if ev.event_date:
                return (0, ev.event_date)
            return (1, date(9999, 12, 31))

        events.sort(key=_sort_key, reverse=params.reverse_chronological)

        total_count = len(events)
        categories = sorted(list(set(e.category for e in events)))
        years = sorted(list(set(e.event_date.year for e in events if e.event_date)))
        disputed_count = sum(1 for e in events if e.is_disputed)
        unreviewed_count = sum(1 for e in events if e.verification_status == VerificationStatus.PENDING_REVIEW)

        paginated_events = events[params.skip : params.skip + params.limit]
        
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return TimelineResponse(
            total_events=total_count,
            events=paginated_events,
            categories_present=categories,
            years_present=years,
            disputed_count=disputed_count,
            unreviewed_count=unreviewed_count,
        ), latency_ms

    async def get_event(self, event_id: str) -> Optional[TimelineEvent]:
        """Retrieve single event by ID."""
        return self._events.get(event_id)

    async def create_event(
        self,
        event_in: TimelineEventCreate,
        actor_id: str = "demo-user-001",
        actor_role: str = "CONTRIBUTOR"
    ) -> TimelineEvent:
        """Create a documented timeline event with provenance auditing."""
        # Contributors may propose events, but only ADMIN/OWNER may immediately verify
        initial_status = event_in.verification_status
        if actor_role == "CONTRIBUTOR" and initial_status == VerificationStatus.VERIFIED:
            initial_status = VerificationStatus.PENDING_REVIEW

        ev_dict = event_in.model_dump()
        ev_dict["verification_status"] = initial_status
        ev_dict["created_by_user_id"] = actor_id
        ev_dict["id"] = str(uuid4())
        ev_dict["created_at"] = datetime.now(timezone.utc)
        ev_dict["updated_at"] = datetime.now(timezone.utc)

        event = TimelineEvent(**ev_dict)
        self._events[event.id] = event

        await audit_service.record_event(
            action=AuditAction.TIMELINE_EVENT_CREATED,
            actor=actor_id,
            resource=f"TimelineEvent:{event.id}",
            result="SUCCESS",
            metadata={"title": event.title, "precision": event.date_precision.value}
        )
        return event

    async def update_event(
        self,
        event_id: str,
        event_update: TimelineEventUpdate,
        actor_id: str = "demo-user-001",
        actor_role: str = "FAMILY_ADMIN"
    ) -> Optional[TimelineEvent]:
        """Update timeline event details."""
        ev = self._events.get(event_id)
        if not ev:
            return None

        update_dict = event_update.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(ev, field, value)
        
        ev.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.TIMELINE_EVENT_UPDATED,
            actor=actor_id,
            resource=f"TimelineEvent:{event_id}",
            result="SUCCESS",
            metadata={"updated_fields": list(update_dict.keys())}
        )
        return ev

    async def verify_event(
        self,
        event_id: str,
        verify_req: TimelineVerifyRequest,
        actor_id: str = "demo-user-001",
        actor_role: str = "FAMILY_ADMIN"
    ) -> Optional[TimelineEvent]:
        """Authorized review action changing verification status."""
        ev = self._events.get(event_id)
        if not ev:
            return None

        ev.verification_status = verify_req.verification_status
        if verify_req.verification_status == VerificationStatus.VERIFIED:
            ev.confidence = ConfidenceLevel.VERIFIED
            ev.confidence_score = 1.0
            ev.is_ai_suggested = False  # Officially verified by human custodian
        elif verify_req.verification_status == VerificationStatus.REJECTED:
            ev.confidence = ConfidenceLevel.UNKNOWN_UNSUPPORTED
            ev.confidence_score = 0.0

        ev.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.TIMELINE_EVENT_VERIFIED,
            actor=actor_id,
            resource=f"TimelineEvent:{event_id}",
            result="SUCCESS",
            metadata={
                "status": verify_req.verification_status.value,
                "notes": verify_req.verification_notes
            }
        )
        return ev

    async def dispute_event(
        self,
        event_id: str,
        dispute_req: TimelineDisputeRequest,
        actor_id: str = "demo-user-001"
    ) -> Optional[TimelineEvent]:
        """Register conflicting dates or accounts while preserving both sources."""
        ev = self._events.get(event_id)
        if not ev:
            return None

        ev.is_disputed = True
        notes = f"Dispute: {dispute_req.dispute_reason}"
        if dispute_req.competing_date:
            notes += f" | Competing proposed date: {dispute_req.competing_date}"
        if dispute_req.notes:
            notes += f" | Additional context: {dispute_req.notes}"
        ev.dispute_notes = notes

        if dispute_req.competing_evidence_id and dispute_req.competing_evidence_id not in ev.competing_evidence_ids:
            ev.competing_evidence_ids.append(dispute_req.competing_evidence_id)

        ev.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.TIMELINE_EVENT_DISPUTED,
            actor=actor_id,
            resource=f"TimelineEvent:{event_id}",
            result="SUCCESS",
            metadata={"dispute_reason": dispute_req.dispute_reason}
        )
        return ev

    async def generate_ai_suggestions(
        self,
        memorial_profile_id: str = "demo-profile-001",
        memory_id: Optional[str] = None,
        max_suggestions: int = 3,
        actor_id: str = "demo-user-001"
    ) -> List[TimelineEvent]:
        """Generate timeline suggestions strictly validated against Phase 5 Memory Guardian.
        
        SAFETY RULES:
        1. Retrieves only authorized, existing preserved memories.
        2. Proposes events with attached provenance and confidence.
        3. Validates against Memory Guardian boundary & hallucination checks.
        4. Tags output as is_ai_suggested=True and verification_status=PENDING_REVIEW.
        5. Never overwrites or automatically verifies any event.
        """
        suggestions: List[TimelineEvent] = []
        
        # Retrieve memories
        memories = await memory_service.list_memories(
            profile_id=memorial_profile_id,
            user_id=actor_id,
            role="vault_owner",
            limit=10
        )

        if memory_id:
            memories = [m for m in memories if m.id == memory_id or m.memory_id == memory_id]

        guardian = MemoryGuardian()

        for mem in memories:
            if len(suggestions) >= max_suggestions:
                break
            
            # Check if an event already links to this memory
            already_linked = any(mem.id in e.linked_memory_ids for e in self._events.values())
            if already_linked and not memory_id:
                continue

            # Parse candidate date if present
            candidate_date = None
            date_precision = DatePrecision.UNKNOWN
            if mem.date:
                try:
                    parts = [int(p) for p in mem.date.split("-")]
                    if len(parts) == 3:
                        candidate_date = date(parts[0], parts[1], parts[2])
                        date_precision = DatePrecision.EXACT
                    elif len(parts) == 2:
                        candidate_date = date(parts[0], parts[1], 1)
                        date_precision = DatePrecision.MONTH_YEAR
                    elif len(parts) == 1:
                        candidate_date = date(parts[0], 1, 1)
                        date_precision = DatePrecision.YEAR_ONLY
                except Exception:
                    candidate_date = None
            
            if not candidate_date and mem.approximate_date:
                date_precision = DatePrecision.APPROXIMATE

            # Construct proposed candidate narrative
            proposed_title = f"Archival Event: {mem.title}"
            proposed_desc = mem.summary or mem.description or "Documented in preserved memorial records."

            # Run through Memory Guardian safety verification
            evidence_items = [
                {
                    "source_id": p.source_id,
                    "evidence_text": p.evidence_text,
                    "confidence": p.confidence.value
                }
                for p in mem.provenance_records
            ]

            guardian_res = guardian.validate_response(
                response_text=f"{proposed_title}. {proposed_desc}",
                evidence_items=evidence_items,
                claims=[],
                privacy_authorized=True,
                consent_authorized=True
            )

            # AI suggestion is rejected if blocked by Guardian
            if guardian_res.guardian_status == GuardianDecision.BLOCK:
                continue

            suggested_event = TimelineEvent(
                id=str(uuid4()),
                memorial_profile_id=memorial_profile_id,
                title=proposed_title,
                description=proposed_desc,
                category=mem.category.value if hasattr(mem.category, "value") else str(mem.category),
                event_date=candidate_date,
                date_description=mem.approximate_date or (str(candidate_date) if candidate_date else "Date undetermined"),
                date_precision=date_precision,
                location_name=mem.location or mem.location_name,
                associated_people=mem.people or [],
                associated_people_ids=mem.people_ids or [],
                linked_memory_ids=[mem.id],
                evidence_ids=[p.source_id for p in mem.provenance_records],
                source_type=mem.source_type,
                confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
                confidence_score=0.85,
                verification_status=VerificationStatus.PENDING_REVIEW,
                provenance_status=ProvenanceStatus.AI_INFERRED,
                is_ai_suggested=True,
                is_disputed=False,
                created_by_user_id="ai-memorial-processor",
                metadata={"guardian_result_id": guardian_res.result_id}
            )

            # Store as pending suggestion
            self._events[suggested_event.id] = suggested_event
            suggestions.append(suggested_event)

        return suggestions


# Singleton instance
timeline_service = TimelineService()
