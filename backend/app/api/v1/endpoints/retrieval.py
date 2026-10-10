"""Evidence Retrieval API Endpoints.

Provides multi-strategy evidence retrieval:
- VECTOR: Dense semantic nearest-neighbor search
- KEYWORD: Exact token and phrase search
- GRAPH: Entity neighborhood and relationship traversal
- HYBRID: Multi-source synthesize with explainable scoring

Strict privacy boundaries and consent rules are enforced before returning results.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional

from models.enums import RetrievalMode, AuditAction, PrivacyLevel, ProvenanceStatus
from models.retrieval import RetrievalQuery, RetrievalResponse
from backend.app.services.retrieval_service import get_retrieval_service
from backend.app.services.audit_service import audit_service

router = APIRouter()


@router.post("/search", response_model=RetrievalResponse)
async def search_evidence(query: RetrievalQuery):
    """Execute evidence search under VECTOR, KEYWORD, GRAPH, or HYBRID mode.
    
    Returns ranked evidence items with provenance status, confidence levels,
    score breakdowns, and 'why_retrieved' explanations.
    """
    if not query.query or not query.query.strip():
        raise HTTPException(status_code=400, detail="Search query text cannot be empty.")

    retrieval_svc = get_retrieval_service()
    response = await retrieval_svc.search(query)

    await audit_service.record_event(
        action=AuditAction.RETRIEVAL_EXECUTED,
        actor=query.user_id or "system",
        resource=f"Retrieval/{query.memorial_profile_id}",
        metadata={
            "query": query.query[:50],
            "mode": query.retrieval_mode.value,
            "returned_count": response.returned_count,
            "latency_ms": response.latency_ms
        }
    )

    return response


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_retrieval_history(limit: int = 50):
    """Return historical retrieval queries and latency benchmarks."""
    retrieval_svc = get_retrieval_service()
    return retrieval_svc.get_logs(limit=limit)
