"""Documented Event Model for ECHO Memorial Architecture.

Extracts verifiable historical milestones from documents, text, transcripts,
and verified user descriptions without inventing ungrounded events.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import EventType, ProvenanceStatus, ConfidenceLevel


class ExtractedEventBase(BaseModel):
    title: str = Field(..., description="Event title (e.g. 'Master of Arts Graduation')")
    description: str = Field(default="", description="Detailed event narrative or description")
    event_type: EventType = Field(default=EventType.OTHER, description="Category of event")
    date: Optional[str] = Field(None, description="ISO or formal date string")
    approximate_date: Optional[str] = Field(None, description="e.g. 'Late Summer 1968'")
    location: Optional[str] = Field(None, description="Geographical or institutional venue")
    people: List[str] = Field(default_factory=list, description="Names of individuals involved")
    source_media_id: Optional[str] = None
    source_memory_id: Optional[str] = None
    provenance_status: ProvenanceStatus = Field(default=ProvenanceStatus.DIRECTLY_OBSERVED)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.VERIFIED)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    extraction_method: str = Field(default="structured_extraction")


class ExtractedEventCreate(ExtractedEventBase):
    pass


class ExtractedEvent(ExtractedEventBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    event_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)

    def model_post_init(self, __context: Any) -> None:
        if not self.event_id:
            self.event_id = self.id
