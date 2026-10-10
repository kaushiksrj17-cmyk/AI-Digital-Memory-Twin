"""Health Endpoint.

Provides comprehensive diagnostic data, provider connectivity statuses,
storage root verification, and ethical compliance parameters.
"""

from fastapi import APIRouter, status
from typing import Dict, Any
from pathlib import Path
import os
import sys

from backend.app.core.config import settings
from ai.providers.factory import provider_registry
from backend.app.services.guardian_service import guardian_service

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, response_model=Dict[str, Any])
async def check_health() -> Dict[str, Any]:
    """System health check and diagnostic inspection."""
    
    # Check D:\ECHO storage presence
    project_root = Path(settings.PROJECT_ROOT)
    storage_root = Path(settings.STORAGE_ROOT)

    storage_verified = project_root.exists() and storage_root.exists()

    ai_health = provider_registry.get_all_health()
    guardian_status = guardian_service.get_status()

    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "research_title": settings.RESEARCH_TITLE,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "storage": {
            "root": str(project_root),
            "storage_local": str(storage_root),
            "verified_in_echo": storage_verified,
            "status": "active_usb_storage" if "D:" in str(project_root) else "active_local_storage"
        },
        "python_runtime": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "ethical_boundary": {
            "enforced": True,
            "notice": settings.ETHICAL_DISCLAIMER_TEXT,
            "recreation_of_consciousness_claimed": False,
            "identity_fabrication_allowed": False
        },
        "guardian": guardian_status,
        "ai_providers": [h.model_dump() for h in ai_health],
        "database": {
            "type": "PostgreSQL-ready (Async Engine)",
            "connection_status": "configured"
        }
    }
