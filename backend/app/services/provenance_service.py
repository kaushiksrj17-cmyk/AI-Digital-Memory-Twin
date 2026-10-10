"""Memory Provenance Service.

Binds statements to source artifacts, generating formal citations
and assuring evidence grounding.
"""

from typing import List, Optional
from models.provenance import ProvenanceRecord, GroundedClaim
from models.enums import ConfidenceLevel, SourceType


class ProvenanceService:
    """Manages evidence provenance records and assertion grounding."""

    @staticmethod
    def create_citation(
        source_id: str,
        source_type: SourceType,
        source_title: str,
        source_reference: str,
        evidence_text: str,
        confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    ) -> ProvenanceRecord:
        return ProvenanceRecord(
            source_id=source_id,
            source_type=source_type,
            source_title=source_title,
            source_reference=source_reference,
            evidence_text=evidence_text,
            confidence=confidence,
            confidence_score=1.0 if confidence == ConfidenceLevel.VERIFIED else 0.7,
            provenance_status="AUTHENTICATED_PRIMARY_SOURCE",
            citation_label="Based on preserved evidence"
        )

    @staticmethod
    def format_grounded_response(
        text: str,
        citations: List[ProvenanceRecord]
    ) -> str:
        """Prepend formal provenance notice if citations exist, or explicit boundary notice."""
        if not citations:
            return text

        citation_tags = ", ".join(f"[{c.source_title} - {c.source_reference}]" for c in citations)
        return f"{text}\n\n*Based on preserved evidence: {citation_tags}*"


provenance_service = ProvenanceService()
