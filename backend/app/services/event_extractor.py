"""Event Extraction Service for ECHO.

Extracts grounded milestones and life events from documented archives, transcripts, and verified memory records:
- Event types: BIRTH, CHILDHOOD, EDUCATION, CAREER, FAMILY, FRIENDSHIP, TRAVEL,
  ACHIEVEMENT, CELEBRATION, IMPORTANT_EVENT, PERSONAL_STORY, OTHER
- Strict evidence boundary: does not fabricate events or assume dates that were not recorded.
"""

from typing import List, Dict, Any, Optional
import re
from uuid import uuid4
from datetime import datetime, timezone

from models.enums import EventType, ProvenanceStatus, ConfidenceLevel
from models.event import ExtractedEvent


class EventExtractor:
    """Specialized historical event extraction engine."""

    # Keywords mapping to specific event categories
    CATEGORY_CUES = {
        EventType.EDUCATION: ["graduation", "degree", "university", "college", "school", "alumni", "commencement", "thesis", "exam"],
        EventType.CAREER: ["promoted", "hired", "retirement", "office", "company", "career", "work", "appointment", "director"],
        EventType.TRAVEL: ["journey", "trip", "travel", "sailed", "voyage", "holiday", "visited", "tour", "expedition"],
        EventType.ACHIEVEMENT: ["award", "honor", "medal", "prize", "recognition", "victory", "first place", "distinction"],
        EventType.CELEBRATION: ["anniversary", "birthday", "celebration", "jubilee", "party", "wedding", "reception"],
        EventType.BIRTH: ["born", "birth", "infant", "childbirth"],
        EventType.FAMILY: ["family reunion", "parents", "children", "household", "homecoming"],
    }

    def __init__(self):
        self.processor_name = "EventExtractor"
        self.processor_version = "echo-event-v1.0"
        self._event_store: Dict[str, List[ExtractedEvent]] = {}  # memory_id -> list of events

    def extract_events_from_memory(
        self,
        memory_id: str,
        title: str,
        description: str,
        date: Optional[str] = None,
        approximate_date: Optional[str] = None,
        location: Optional[str] = None,
        people: Optional[List[str]] = None,
        source_media_id: Optional[str] = None,
        provenance_status: ProvenanceStatus = ProvenanceStatus.USER_PROVIDED
    ) -> List[ExtractedEvent]:
        """Extract a structured milestone from a memory's verified narrative."""
        events: List[ExtractedEvent] = []
        full_text = f"{title} {description}".lower()

        # Classify event type based on narrative cues
        inferred_type = EventType.OTHER
        for event_type, cues in self.CATEGORY_CUES.items():
            if any(cue in full_text for cue in cues):
                inferred_type = event_type
                break

        # Create structured event record grounded in the primary memory
        event = ExtractedEvent(
            id=str(uuid4()),
            event_id=str(uuid4()),
            title=title,
            description=description,
            event_type=inferred_type,
            date=date,
            approximate_date=approximate_date,
            location=location,
            people=people or [],
            source_media_id=source_media_id,
            source_memory_id=memory_id,
            provenance_status=provenance_status,
            confidence=ConfidenceLevel.VERIFIED if date else ConfidenceLevel.SUPPORTED_INFERENCE,
            confidence_score=1.0 if date else 0.85,
            extraction_method="narrative_event_classifier"
        )
        events.append(event)

        if memory_id not in self._event_store:
            self._event_store[memory_id] = []
        self._event_store[memory_id].extend(events)

        return events

    def get_events_for_memory(self, memory_id: str) -> List[ExtractedEvent]:
        """Retrieve indexed events linked to a memory."""
        return self._event_store.get(memory_id, [])


event_extractor = EventExtractor()
