"""Timeline Domain Model for Chronological Life Journey in ECHO.

Encapsulates:
- Evidence-grounded life milestones with multi-criteria filtering
- Evidentiary date precision (EXACT, MONTH_YEAR, YEAR_ONLY, APPROXIMATE, UNKNOWN)
- Confidence classification (GREEN / YELLOW / RED)
- Disputed dates and conflicting evidence tracking
- AI-inferred suggestions vs authorized verified events
- Direct link to 3D Memory Room focal objects
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import uuid4

from models.enums import (
    ConfidenceLevel,
    VerificationStatus,
    DatePrecision,
    MemoryCategory,
    SourceType,
    ProvenanceStatus,
)


class TimelineEventBase(BaseModel):
    title: str = Field(..., description="Documented title of life event, e.g. 'Conferred MA at Cambridge'")
    description: Optional[str] = Field(None, description="Detailed archival account of event")
    category: str = Field(default="OTHER", description="Childhood, Education, Career, Family, Travel, etc.")
    
    # Chronological specifications
    event_date: Optional[date] = Field(None, description="Primary event date if known")
    date_end: Optional[date] = Field(None, description="End date for epoch/interval events")
    date_description: Optional[str] = Field(None, description="Human readable date e.g. 'Autumn 1964'")
    date_precision: DatePrecision = Field(
        default=DatePrecision.EXACT,
        description="Exactness of date record: EXACT, MONTH_YEAR, YEAR_ONLY, APPROXIMATE, UNKNOWN"
    )
    
    # Spatial & Social
    location_name: Optional[str] = Field(None, description="Preserved geographic place name")
    associated_people: List[str] = Field(default_factory=list, description="Names of connected individuals")
    associated_people_ids: List[str] = Field(default_factory=list, description="IDs of linked person entities")
    
    # Evidentiary Grounding
    linked_memory_ids: List[str] = Field(default_factory=list, description="IDs of primary memories documenting event")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of specific evidence records")
    source_type: SourceType = Field(default=SourceType.DOCUMENT, description="Primary source medium")
    
    # Confidence and Integrity
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.VERIFIED, description="GREEN / YELLOW / RED")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    verification_status: VerificationStatus = Field(default=VerificationStatus.VERIFIED)
    provenance_status: ProvenanceStatus = Field(default=ProvenanceStatus.DIRECTLY_OBSERVED)
    
    # AI vs Human Attribution
    is_ai_suggested: bool = Field(default=False, description="True if inferred by multimodal pipeline; requires review")
    
    # Dispute and Conflict Tracking
    is_disputed: bool = Field(default=False, description="True if competing accounts/dates exist in archives")
    dispute_notes: Optional[str] = Field(None, description="Summary of competing accounts preserving both sources")
    competing_evidence_ids: List[str] = Field(default_factory=list, description="Alternative sources supporting competing dates")
    
    # 3D Memory Room Integration
    memory_room_object_id: Optional[str] = Field(None, description="Linked 3D object anchor in Memory Room if any")
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineEventCreate(TimelineEventBase):
    memorial_profile_id: str = "demo-profile-001"


class TimelineEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    event_date: Optional[date] = None
    date_end: Optional[date] = None
    date_description: Optional[str] = None
    date_precision: Optional[DatePrecision] = None
    location_name: Optional[str] = None
    associated_people: Optional[List[str]] = None
    linked_memory_ids: Optional[List[str]] = None
    evidence_ids: Optional[List[str]] = None
    confidence: Optional[ConfidenceLevel] = None
    verification_status: Optional[VerificationStatus] = None
    is_disputed: Optional[bool] = None
    dispute_notes: Optional[str] = None
    competing_evidence_ids: Optional[List[str]] = None
    memory_room_object_id: Optional[str] = None


class TimelineEvent(TimelineEventBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "demo-profile-001"
    created_by_user_id: str = "demo-user-001"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class TimelineDisputeRequest(BaseModel):
    dispute_reason: str = Field(..., description="Explanation of why the date or details are contested")
    competing_date: Optional[str] = Field(None, description="Proposed alternate date according to family/source")
    competing_evidence_id: Optional[str] = Field(None, description="Evidence ID backing the alternative claim")
    notes: Optional[str] = None


class TimelineVerifyRequest(BaseModel):
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    verification_notes: Optional[str] = None


class TimelineSuggestionRequest(BaseModel):
    memorial_profile_id: str = "demo-profile-001"
    memory_id: Optional[str] = Field(None, description="Specific memory to extract candidate events from")
    max_suggestions: int = Field(default=3, ge=1, le=10)


class TimelineFilterParams(BaseModel):
    memorial_profile_id: str = "demo-profile-001"
    category: Optional[str] = None
    source_type: Optional[SourceType] = None
    person: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    search_query: Optional[str] = None
    confidence: Optional[ConfidenceLevel] = None
    verification_status: Optional[VerificationStatus] = None
    include_ai_suggested: bool = True
    include_disputed: bool = True
    reverse_chronological: bool = False
    skip: int = 0
    limit: int = 50


class TimelineResponse(BaseModel):
    total_events: int
    events: List[TimelineEvent]
    categories_present: List[str]
    years_present: List[int]
    disputed_count: int
    unreviewed_count: int
