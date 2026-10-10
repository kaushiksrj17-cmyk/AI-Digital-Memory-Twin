"""Memory Domain Model and Schemas.

Extended for Phase 2 Secure Multimodal Memory Vault with support for:
- Granular Categories & Source Types
- Checksum & Duplicate Detection
- Relative Safe Storage & Thumbnail paths (Zero Absolute FS Paths exposed)
- Privacy, Consent & Verification lifecycles
- Soft Archive & Deletion Tracking
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import (
    ConfidenceLevel,
    MemoryCategory,
    VerificationStatus,
    PrivacyLevel,
    SourceType,
    ConsentStatus,
    ProcessingStatus
)
from models.provenance import ProvenanceRecord


class MemoryBase(BaseModel):
    title: str = Field(..., max_length=255, description="Descriptive title of the preserved memory")
    description: str = Field(default="", description="Full textual story, excerpt, or archival description")
    narrative: Optional[str] = Field(None, description="Phase 1 alias for narrative description")
    summary: Optional[str] = Field(None, description="Concise summary for timelines and search cards")
    
    # Categorization and Provenance
    category: MemoryCategory = Field(default=MemoryCategory.OTHER, description="Controlled archival category")
    source_type: SourceType = Field(default=SourceType.FAMILY_STORY, description="Source origin")
    
    # Confidence and Verification
    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.VERIFIED,
        description="GREEN = VERIFIED, YELLOW = SUPPORTED_INFERENCE, RED = UNKNOWN/UNSUPPORTED"
    )
    verification_status: VerificationStatus = Field(default=VerificationStatus.PENDING_REVIEW)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Privacy & Consent (Default strictly PRIVATE)
    privacy_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    consent_status: ConsentStatus = Field(default=ConsentStatus.PENDING)
    consent_id: Optional[str] = Field(None, description="Associated consent record granting preservation")
    
    # Spatiotemporal Anchoring
    date: Optional[str] = Field(None, description="Preserved ISO date or exact date (e.g., '1968-06-22')")
    approximate_date: Optional[str] = Field(None, description="Descriptive period (e.g., 'Summer 1974')")
    location: Optional[str] = Field(None, description="Geographical anchor or location name")
    location_name: Optional[str] = Field(None, description="Phase 1 alias for location")
    event_timestamp: Optional[datetime] = None
    location_id: Optional[str] = None
    
    # Social Graph Anchors
    people: List[str] = Field(default_factory=list, description="Names or IDs of individuals associated with memory")
    people_ids: List[str] = Field(default_factory=list, description="Phase 1 alias for people IDs")
    relationship_ids: List[str] = Field(default_factory=list, description="IDs of relationships referenced")
    media_ids: List[str] = Field(default_factory=list, description="Associated photograph, audio, or document IDs")
    
    # Vault Storage & Media (Relative safe paths only)
    original_filename: Optional[str] = Field(None, description="Original uploaded filename sanitized")
    mime_type: Optional[str] = Field(None, description="Validated MIME type")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    storage_path: Optional[str] = Field(None, description="Relative safe path in storage, e.g. originals/...")
    thumbnail_path: Optional[str] = Field(None, description="Relative safe path in storage, e.g. thumbnails/...")
    checksum: Optional[str] = Field(None, description="Cryptographic SHA-256 digest")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.COMPLETED)
    
    # Lifecycle & Soft State
    archived: bool = Field(default=False, description="True if archived (hidden from standard views)")
    deleted_at: Optional[datetime] = Field(None, description="Timestamp of soft deletion")
    uploaded_by: Optional[str] = Field(None, description="User ID or identifier of uploader")
    
    # Evidence & Provenance
    provenance_records: List[ProvenanceRecord] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode='before')
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Sync narrative <-> description
            if not data.get("description") and data.get("narrative"):
                data["description"] = data["narrative"]
            elif not data.get("narrative") and data.get("description"):
                data["narrative"] = data["description"]
            # Sync location <-> location_name
            if not data.get("location") and data.get("location_name"):
                data["location"] = data["location_name"]
            elif not data.get("location_name") and data.get("location"):
                data["location_name"] = data["location"]
            # Sync people <-> people_ids
            if not data.get("people") and data.get("people_ids"):
                data["people"] = list(data["people_ids"])
            elif not data.get("people_ids") and data.get("people"):
                data["people_ids"] = list(data["people"])
            # Map memory_id to id if given
            if "memory_id" in data and "id" not in data:
                data["id"] = data["memory_id"]
        return data


class MemoryCreate(MemoryBase):
    memorial_profile_id: str = Field(default="default-profile-001")


class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    narrative: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[MemoryCategory] = None
    source_type: Optional[SourceType] = None
    confidence: Optional[ConfidenceLevel] = None
    verification_status: Optional[VerificationStatus] = None
    privacy_level: Optional[PrivacyLevel] = None
    consent_status: Optional[ConsentStatus] = None
    date: Optional[str] = None
    approximate_date: Optional[str] = None
    location: Optional[str] = None
    location_name: Optional[str] = None
    people: Optional[List[str]] = None
    people_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    archived: Optional[bool] = None
    processing_status: Optional[ProcessingStatus] = None


class Memory(MemoryBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    memory_id: Optional[str] = None
    memorial_profile_id: str = Field(default="default-profile-001")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by_user_id: Optional[str] = None

    @model_validator(mode='after')
    def set_memory_id(self) -> 'Memory':
        if not self.memory_id:
            self.memory_id = self.id
        return self

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
