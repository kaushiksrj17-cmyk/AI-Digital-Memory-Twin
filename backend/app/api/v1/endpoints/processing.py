"""Processing Pipeline API Endpoints for ECHO.

Provides endpoints to trigger, monitor, retry, and cancel multimodal evidence extraction:
- POST /api/v1/processing/{media_id}
- GET /api/v1/processing/{media_id}
- GET /api/v1/processing
- POST /api/v1/processing/{media_id}/retry
- POST /api/v1/processing/{media_id}/cancel
"""

from fastapi import APIRouter, HTTPException, Query, Header, status
from typing import List, Optional, Dict, Any

from models.enums import ProcessingStatus
from models.processing import ProcessingJob
from backend.app.services.processing_orchestrator import processing_orchestrator
from backend.app.api.v1.endpoints.media import media_registry

router = APIRouter()


@router.post("/{media_id}", response_model=ProcessingJob, status_code=status.HTTP_202_ACCEPTED)
async def trigger_processing(
    media_id: str,
    memory_id: Optional[str] = Query(None),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    """Trigger or enqueue asynchronous multimodal evidence processing for an uploaded media asset."""
    media = media_registry.get(media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media asset '{media_id}' not found in vault registry"
        )

    actor_id = x_user_id or "authenticated_user"
    job = await processing_orchestrator.enqueue_media_processing(
        media_id=media_id,
        relative_path=media.relative_storage_path,
        memory_id=memory_id,
        actor_id=actor_id
    )
    return job


@router.get("/{media_id}", response_model=ProcessingJob)
async def get_processing_status(media_id: str):
    """Retrieve processing status and execution summary for a media asset."""
    job = processing_orchestrator.get_job(media_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No processing job found for media '{media_id}'"
        )
    return job


@router.get("", response_model=List[ProcessingJob])
async def list_processing_jobs(
    status: Optional[ProcessingStatus] = Query(None, description="Filter by status")
):
    """List all processing jobs across the vault with optional status filtering."""
    return processing_orchestrator.list_jobs(status_filter=status)


@router.post("/{media_id}/retry", response_model=ProcessingJob)
async def retry_processing(
    media_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    """Retry a failed or interrupted processing job."""
    media = media_registry.get(media_id)
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Media asset '{media_id}' not found in vault registry"
        )

    actor_id = x_user_id or "authenticated_user"
    return await processing_orchestrator.retry_processing(
        media_id=media_id,
        relative_path=media.relative_storage_path,
        actor_id=actor_id
    )


@router.post("/{media_id}/cancel", response_model=ProcessingJob)
async def cancel_processing(
    media_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id")
):
    """Cancel a pending or processing operation."""
    job = await processing_orchestrator.cancel_processing(
        media_id=media_id,
        actor_id=x_user_id or "authenticated_user"
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active job found for media '{media_id}' to cancel"
        )
    return job
