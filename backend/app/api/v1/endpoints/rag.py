"""Retrieval-Augmented Generation (RAG) Architecture Endpoints for ECHO.

Executes evidence-grounded query answering, context construction, Memory Guardian verification,
and research telemetry tracking.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional

from models.conversation import RAGQueryRequest, RAGQueryResponse
from backend.app.services.rag_service import get_rag_service

router = APIRouter()


@router.post("/query", response_model=RAGQueryResponse)
async def query_evidence_rag(request: RAGQueryRequest) -> RAGQueryResponse:
    """Execute evidence-grounded RAG inquiry with Memory Guardian validation."""
    rag_service = get_rag_service()
    try:
        response = await rag_service.query(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG execution failure: {str(e)}"
        )


@router.get("/metrics")
async def get_rag_metrics() -> List[Dict[str, Any]]:
    """Retrieve research telemetry for conversational grounding and latencies."""
    rag_service = get_rag_service()
    return rag_service.get_metrics()
