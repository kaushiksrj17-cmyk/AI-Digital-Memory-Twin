"""Consent API Endpoints.

Allows creating, tracking, verifying, and revoking granular consent records
for media processing, AI processing, voice cloning, and avatar generation.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from models.consent import ConsentRecord, ConsentRecordCreate
from models.enums import ConsentType
from backend.app.services.consent_service import consent_service

router = APIRouter()


@router.post("/", response_model=ConsentRecord, status_code=status.HTTP_201_CREATED)
async def grant_consent(consent_in: ConsentRecordCreate):
    """Grant explicit consent authorization."""
    return await consent_service.grant_consent(consent_in)


@router.get("/", response_model=List[ConsentRecord])
async def list_consents(
    memory_id: Optional[str] = None,
    media_id: Optional[str] = None,
    consent_type: Optional[ConsentType] = None
):
    """Query active or historical consent records."""
    return await consent_service.list_consents(
        memory_id=memory_id,
        media_id=media_id,
        consent_type=consent_type
    )


@router.post("/{consent_id}/revoke", response_model=ConsentRecord)
async def revoke_consent(consent_id: str):
    """Revoke a previously granted consent."""
    revoked = await consent_service.revoke_consent(consent_id)
    if not revoked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent record not found")
    return revoked
