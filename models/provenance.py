"""Provenance and Evidence Citations.

Every AI response and memory representation must carry provenance
demonstrating: 'Based on preserved evidence' rather than hallucinations.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.enums import ConfidenceLevel, SourceType


class ProvenanceRecord(BaseModel):
    """Granular provenance record tying claims directly to source evidence."""
    source_id: str = Field(..., description="Unique ID of preserved media or document")
    source_type: SourceType = Field(..., description="Media or record type")
    source_title: str = Field(..., description="Human-readable title of the evidence artifact")
    source_reference: str = Field(..., description="Document page, timestamp, or audio index")
    evidence_text: str = Field(..., description="Direct excerpt or transcript verifying the claim")
    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.VERIFIED,
        description="Confidence status of this grounding link"
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Calculated verification confidence score"
    )
    provenance_status: str = Field(
        default="AUTHENTICATED_PRIMARY_SOURCE",
        description="Status description (e.g., PRIMARY_SOURCE, CORROBORATED, ORAL_HISTORY)"
    )
    citation_label: str = Field(
        default="Based on preserved evidence",
        description="Public citation banner to display alongside statements"
    )


class GroundedClaim(BaseModel):
    """An individual factual claim paired with evidence citations and confidence."""
    claim_text: str
    confidence: ConfidenceLevel
    provenance: List[ProvenanceRecord] = Field(default_factory=list)
    is_supported: bool = True
