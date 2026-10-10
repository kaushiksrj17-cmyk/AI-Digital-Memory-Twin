"""Provenance API Endpoint."""

from fastapi import APIRouter
from typing import List
from models.provenance import ProvenanceRecord
from models.enums import SourceType, ConfidenceLevel

router = APIRouter()


@router.get("/citations", response_model=List[ProvenanceRecord])
async def list_sample_citations():
    """Retrieve sample provenance citations verifying grounded memories."""
    return [
        ProvenanceRecord(
            source_id="demo-doc-001",
            source_type=SourceType.DOCUMENT,
            source_title="University Degree Registry Record",
            source_reference="Folio 82, Cambridge Archives",
            evidence_text="Conferred Degree of Master of Arts on June 22, 1968.",
            confidence=ConfidenceLevel.VERIFIED,
            citation_label="Based on preserved evidence"
        ),
        ProvenanceRecord(
            source_id="demo-media-002",
            source_type=SourceType.AUDIO_RECORDING,
            source_title="Family Oral History Audio Tape",
            source_reference="Side A, 14m:22s",
            evidence_text="Narrating story of first car journey to the Scottish Highlands.",
            confidence=ConfidenceLevel.VERIFIED,
            citation_label="Based on preserved evidence"
        )
    ]
