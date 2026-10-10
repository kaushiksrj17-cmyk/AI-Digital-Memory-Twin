"""Confidence API Endpoint."""

from fastapi import APIRouter
from typing import Dict, Any, List
from models.enums import ConfidenceLevel
from backend.app.services.confidence_service import confidence_service

router = APIRouter()


@router.get("/levels")
async def get_confidence_levels() -> List[Dict[str, Any]]:
    """Retrieve system confidence levels (GREEN, YELLOW, RED) and UX metadata."""
    return [
        confidence_service.get_confidence_metadata(ConfidenceLevel.VERIFIED),
        confidence_service.get_confidence_metadata(ConfidenceLevel.SUPPORTED_INFERENCE),
        confidence_service.get_confidence_metadata(ConfidenceLevel.UNKNOWN_UNSUPPORTED)
    ]
