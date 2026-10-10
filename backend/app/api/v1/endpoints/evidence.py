"""Evidence Explorer API Endpoints for ECHO.

Provides endpoints to query, inspect, and retrieve atomic evidentiary artifacts:
- GET /api/v1/evidence
- GET /api/v1/evidence/{id}
"""

from fastapi import APIRouter, HTTPException, Query, Header, status
from typing import List, Optional, Dict, Any

from models.enums import EvidenceType, ProvenanceStatus, ConfidenceLevel
from models.evidence import Evidence
from backend.app.services.processing_orchestrator import processing_orchestrator

router = APIRouter()


@router.get("", response_model=List[Evidence])
async def list_evidence(
    search: Optional[str] = Query(None, description="Keyword search across content and citations"),
    evidence_type: Optional[EvidenceType] = Query(None, description="Filter by evidence type"),
    provenance_status: Optional[ProvenanceStatus] = Query(None, description="Filter by provenance status"),
    confidence: Optional[ConfidenceLevel] = Query(None, description="Filter by confidence level"),
    media_id: Optional[str] = Query(None, description="Filter by source media ID"),
    memory_id: Optional[str] = Query(None, description="Filter by memory ID")
):
    """Retrieve and filter atomic evidence records grounding memories and claims."""
    return processing_orchestrator.list_evidence(
        search=search,
        evidence_type=evidence_type,
        provenance_status=provenance_status,
        confidence=confidence,
        media_id=media_id,
        memory_id=memory_id
    )


@router.get("/{id}", response_model=Evidence)
async def get_evidence_item(id: str):
    """Retrieve an individual atomic evidence record by ID."""
    evidence = processing_orchestrator.get_evidence(id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence artifact '{id}' not found in archive"
        )
    return evidence
