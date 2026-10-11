"""Memories API Endpoints.

Complete Phase 2 CRUD, search, filter, verification, archive, and export endpoints.
Versioned under /api/v1/memories.
"""

from fastapi import APIRouter, HTTPException, Query, status, Body, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from models.memory import Memory, MemoryCreate, MemoryUpdate
from models.enums import (
    ConfidenceLevel,
    MemoryCategory,
    SourceType,
    VerificationStatus,
    PrivacyLevel
)
from backend.app.services.memory_service import (
    memory_service,
    UnauthorizedMemoryAccessError
)
from backend.app.core.security import get_current_user, get_current_user_or_visitor

router = APIRouter()


class VerifyRequest(BaseModel):
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


@router.get("/", response_model=List[Memory])
async def list_memories(
    profile_id: Optional[str] = None,
    confidence: Optional[ConfidenceLevel] = None,
    category: Optional[MemoryCategory] = None,
    source_type: Optional[SourceType] = None,
    verification_status: Optional[VerificationStatus] = None,
    privacy_level: Optional[PrivacyLevel] = None,
    search: Optional[str] = None,
    person: Optional[str] = None,
    location: Optional[str] = None,
    include_archived: bool = Query(False, description="Include archived memories"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user_or_visitor)
):
    """List preserved memories with multi-attribute search and filtering."""
    return await memory_service.list_memories(
        profile_id=profile_id,
        confidence=confidence,
        category=category,
        source_type=source_type,
        verification_status=verification_status,
        privacy_level=privacy_level,
        search_query=search,
        person=person,
        location=location,
        include_archived=include_archived,
        user_id=current_user.get("id"),
        role=current_user.get("role", "visitor"),
        skip=skip,
        limit=limit
    )


@router.get("/{memory_id}", response_model=Memory)
async def get_memory(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user_or_visitor)
):
    """Retrieve an individual preserved memory with provenance citations."""
    try:
        mem = await memory_service.get_memory(
            memory_id,
            user_id=current_user.get("id"),
            role=current_user.get("role", "visitor")
        )
        if not mem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found in vault")
        return mem
    except UnauthorizedMemoryAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/", response_model=Memory, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory_in: MemoryCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Ingest a new memory into the vault with duplicate detection."""
    return await memory_service.create_memory(
        memory_in,
        user_id=current_user.get("id"),
        role=current_user.get("role", "visitor")
    )


@router.put("/{memory_id}", response_model=Memory)
async def update_memory(
    memory_id: str,
    memory_update: MemoryUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update metadata or privacy settings of an existing memory."""
    try:
        updated = await memory_service.update_memory(
            memory_id,
            memory_update,
            user_id=current_user.get("id"),
            role=current_user.get("role", "visitor")
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found in vault")
        return updated
    except UnauthorizedMemoryAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/{memory_id}", status_code=status.HTTP_200_OK)
async def delete_memory(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Securely soft-delete a memory and record audit trail."""
    try:
        success = await memory_service.delete_memory(
            memory_id,
            user_id=current_user.get("id"),
            role=current_user.get("role", "visitor")
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found in vault")
        return {"status": "success", "message": f"Memory {memory_id} successfully deleted from active vault"}
    except UnauthorizedMemoryAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{memory_id}/archive", response_model=Memory)
async def archive_memory(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Archive a memory without deleting the original evidence."""
    try:
        archived = await memory_service.archive_memory(
            memory_id,
            user_id=current_user.get("id"),
            role=current_user.get("role", "visitor")
        )
        if not archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found in vault")
        return archived
    except UnauthorizedMemoryAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{memory_id}/verify", response_model=Memory)
async def verify_memory(
    memory_id: str,
    request: VerifyRequest = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update verification status (VERIFIED, PENDING_REVIEW, REJECTED) with audit logging."""
    try:
        verified = await memory_service.verify_memory(
            memory_id,
            request.verification_status,
            user_id=current_user.get("id"),
            role=current_user.get("role", "visitor")
        )
        if not verified:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found in vault")
        return verified
    except UnauthorizedMemoryAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{memory_id}/export")
async def export_memory(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Export a memory bundle with metadata, provenance, and safe media links."""
    try:
        return await memory_service.export_memory(
            memory_id,
            user_id=current_user.get("id"),
            role=current_user.get("role", "visitor")
        )
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found for export")
    except UnauthorizedMemoryAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{memory_id}/entities")
async def get_memory_entities(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve structured entities (people, locations, organizations, dates) extracted for a memory."""
    from backend.app.services.entity_extractor import entity_extractor
    try:
        memory = await memory_service.get_memory(
            memory_id,
            user_id=current_user.get("id"),
            role=current_user.get("role", "visitor")
        )
        if not memory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found in vault")
    except UnauthorizedMemoryAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    
    entities = entity_extractor.get_entities_for_memory(memory_id)
    if not entities and (memory.people or memory.location):
        # Register user-provided entities if not already indexed
        entities = entity_extractor.register_user_provided_entities(
            memory_id=memory_id,
            people=memory.people,
            location=memory.location
        )
    return entities


@router.get("/{memory_id}/events")
async def get_memory_events(
    memory_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve historical milestones and life events extracted for a memory."""
    from backend.app.services.event_extractor import event_extractor
    try:
        memory = await memory_service.get_memory(
            memory_id,
            user_id=current_user.get("id"),
            role=current_user.get("role", "visitor")
        )
        if not memory:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found in vault")
    except UnauthorizedMemoryAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    
    events = event_extractor.get_events_for_memory(memory_id)
    if not events:
        events = event_extractor.extract_events_from_memory(
            memory_id=memory_id,
            title=memory.title,
            description=memory.description,
            date=memory.date,
            approximate_date=memory.approximate_date,
            location=memory.location,
            people=memory.people
        )
    return events
