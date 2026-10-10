"""Evidence Artifact Model for ECHO Memorial Architecture.

Preserves the atomic units of proof grounding all memories and AI interactions.
Phase 3 Multimodal AI Memory Processing model supporting cross-modal grounding,
provenance tracking, confidence scoring, and reproducible extraction metadata.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4
from models.enums import (
    SourceType,
    VerificationStatus,
    ConfidenceLevel,
    ProvenanceStatus,
    EvidenceType
)


class EvidenceBase(BaseModel):
    title: Optional[str] = Field(None, description="e.g., '1945 Handwritten Letter from Paris'")
    memory_id: Optional[str] = Field(None, description="Associated memory ID")
    media_id: Optional[str] = Field(None, description="Direct link to preserved media file")
    evidence_type: EvidenceType = Field(default=EvidenceType.TEXT, description="Modality or artifact category")
    content: str = Field(..., description="Transcript excerpt, scanned OCR text, metadata summary, or observation")
    structured_value: Dict[str, Any] = Field(default_factory=dict, description="Parsed structured data / metrics")
    source_reference: str = Field(default="Primary Archive", description="Page number, timestamp, or folio citation")
    provenance_status: ProvenanceStatus = Field(default=ProvenanceStatus.DIRECTLY_OBSERVED)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.VERIFIED)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    extraction_method: str = Field(default="direct_extraction", description="Processor or library used")
    processor_version: str = Field(default="echo-processor-v1.0")
    
    # Phase 1/2 backward compatibility fields
    source_type: Optional[SourceType] = Field(default=SourceType.DOCUMENT)
    raw_content_excerpt: Optional[str] = None
    source_citation: Optional[str] = None
    verification_status: Optional[VerificationStatus] = Field(default=VerificationStatus.VERIFIED)
    verified_by_user_id: Optional[str] = None
    verification_notes: Optional[str] = None
    extracted_metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceCreate(EvidenceBase):
    memorial_profile_id: Optional[str] = "default-profile-001"


class Evidence(EvidenceBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    evidence_id: Optional[str] = None
    memorial_profile_id: str = "default-profile-001"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)

    def model_post_init(self, __context: Any) -> None:
        if not self.evidence_id:
            self.evidence_id = self.id
        if not self.raw_content_excerpt and self.content:
            self.raw_content_excerpt = self.content
        if not self.source_citation and self.source_reference:
            self.source_citation = self.source_reference
