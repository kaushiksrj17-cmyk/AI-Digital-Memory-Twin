"""Evidence-Grounded Memory DNA Pydantic Models.

Memory DNA is a structured, evidence-grounded representation of documented life information.
It is NOT a personality clone and NEVER contains fabricated assumptions or unverified traits.
Missing information remains UNKNOWN.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from models.enums import (
    MemoryDNACategory,
    ConfidenceLevel,
    ProvenanceStatus,
    VerificationStatus,
)


class MemoryDNAItem(BaseModel):
    """An individual structured fact or insight within Memory DNA."""
    dna_item_id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "default-profile-001"
    category: MemoryDNACategory
    key: str
    value: Any
    description: Optional[str] = None
    source_memory_ids: List[str] = Field(default_factory=list)
    source_media_ids: List[str] = Field(default_factory=list)
    source_evidence_ids: List[str] = Field(default_factory=list)
    provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    confidence_score: float = 1.0
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryDNA(BaseModel):
    """Aggregated Memory DNA document for a memorial profile.
    
    Fields that are unverified or undocumented remain empty or marked as UNKNOWN.
    """
    memory_dna_id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "default-profile-001"
    person_id: Optional[str] = None
    summary: Optional[str] = None
    
    # 22 Categories / Groupings
    life_events: List[Dict[str, Any]] = Field(default_factory=list)
    people: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    places: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    career: List[Dict[str, Any]] = Field(default_factory=list)
    family: List[Dict[str, Any]] = Field(default_factory=list)
    friends: List[Dict[str, Any]] = Field(default_factory=list)
    hobbies: List[Dict[str, Any]] = Field(default_factory=list)
    interests: List[Dict[str, Any]] = Field(default_factory=list)
    important_objects: List[Dict[str, Any]] = Field(default_factory=list)
    important_dates: List[Dict[str, Any]] = Field(default_factory=list)
    documented_preferences: List[Dict[str, Any]] = Field(default_factory=list)
    documented_values: List[Dict[str, Any]] = Field(default_factory=list)
    known_phrases: List[Dict[str, Any]] = Field(default_factory=list)
    frequently_mentioned_topics: List[Dict[str, Any]] = Field(default_factory=list)
    stories: List[Dict[str, Any]] = Field(default_factory=list)
    achievements: List[Dict[str, Any]] = Field(default_factory=list)
    travel: List[Dict[str, Any]] = Field(default_factory=list)
    legacy: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Provenance and Traceability
    source_references: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    provenance: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1


class MemoryDNAVersion(BaseModel):
    """Historical snapshot of Memory DNA for research audit and reproducibility."""
    version_id: str = Field(default_factory=lambda: str(uuid4()))
    memory_dna_id: str
    memorial_profile_id: str
    version: int
    dna_snapshot: Dict[str, Any]
    changed_by: str = "system"
    change_reason: str = "Memory DNA generated from multimodal evidence"
    source_evidence: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
