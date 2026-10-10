"""Timeline API Endpoints for ECHO.

Provides chronological life journey querying, multi-criteria filtering,
date precision handling, dispute registration, and Memory Guardian AI event suggestions.
"""

from fastapi import APIRouter, HTTPException, Query, status, Header
from typing import List, Optional
from datetime import date

from models.timeline import (
    TimelineEvent,
    TimelineEventCreate,
    TimelineEventUpdate,
    TimelineFilterParams,
    TimelineResponse,
    TimelineDisputeRequest,
    TimelineVerifyRequest,
    TimelineSuggestionRequest,
)
from models.enums import (
    ConfidenceLevel,
    VerificationStatus,
    SourceType,
)
from backend.app.services.timeline_service import timeline_service

router = APIRouter()


@router.get("/", response_model=TimelineResponse)
async def get_timeline(
    memorial_profile_id: str = "demo-profile-001",
    category: Optional[str] = None,
    source_type: Optional[SourceType] = None,
    person: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    search_query: Optional[str] = None,
    confidence: Optional[ConfidenceLevel] = None,
    verification_status: Optional[VerificationStatus] = None,
    include_ai_suggested: bool = True,
    include_disputed: bool = True,
    reverse_chronological: bool = False,
    skip: int = 0,
    limit: int = 50,
):
    """Retrieve chronological life journey events grounded in archival evidence with multi-criteria filtering."""
    params = TimelineFilterParams(
        memorial_profile_id=memorial_profile_id,
        category=category,
        source_type=source_type,
        person=person,
        year_from=year_from,
        year_to=year_to,
        search_query=search_query,
        confidence=confidence,
        verification_status=verification_status,
        include_ai_suggested=include_ai_suggested,
        include_disputed=include_disputed,
        reverse_chronological=reverse_chronological,
        skip=skip,
        limit=limit,
    )
    res, _latency = await timeline_service.get_timeline(params)
    return res


@router.get("/raw-list", response_model=List[TimelineEvent])
async def get_timeline_raw_list(
    memorial_profile_id: str = "demo-profile-001",
):
    """Backward compatibility endpoint returning a flat list of life events."""
    params = TimelineFilterParams(memorial_profile_id=memorial_profile_id)
    res, _ = await timeline_service.get_timeline(params)
    return res.events


@router.get("/{event_id}", response_model=TimelineEvent)
async def get_timeline_event(event_id: str):
    """Retrieve specific timeline event with archival evidence links."""
    event = await timeline_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    return event


@router.post("/", response_model=TimelineEvent, status_code=status.HTTP_201_CREATED)
async def create_timeline_event(
    event_in: TimelineEventCreate,
    x_user_id: str = Header(default="demo-user-001"),
    x_user_role: str = Header(default="CONTRIBUTOR"),
):
    """Create a documented timeline event. Contributors create as PENDING_REVIEW."""
    try:
        return await timeline_service.create_event(
            event_in,
            actor_id=x_user_id,
            actor_role=x_user_role
        )
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))


@router.put("/{event_id}", response_model=TimelineEvent)
async def update_timeline_event(
    event_id: str,
    event_update: TimelineEventUpdate,
    x_user_id: str = Header(default="demo-user-001"),
    x_user_role: str = Header(default="FAMILY_ADMIN"),
):
    """Update event details and preserve date precision."""
    try:
        updated = await timeline_service.update_event(
            event_id,
            event_update,
            actor_id=x_user_id,
            actor_role=x_user_role
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Timeline event not found")
        return updated
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))


@router.post("/{event_id}/verify", response_model=TimelineEvent)
async def verify_timeline_event(
    event_id: str,
    verify_req: TimelineVerifyRequest,
    x_user_id: str = Header(default="demo-user-001"),
    x_user_role: str = Header(default="FAMILY_ADMIN"),
):
    """Officially verify or reject a timeline event (FAMILY_ADMIN or OWNER only)."""
    if x_user_role not in ["FAMILY_ADMIN", "OWNER", "vault_owner", "admin"]:
        raise HTTPException(status_code=403, detail="Verification requires FAMILY_ADMIN or OWNER clearance")
    
    verified = await timeline_service.verify_event(
        event_id,
        verify_req,
        actor_id=x_user_id,
        actor_role=x_user_role
    )
    if not verified:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    return verified


@router.post("/{event_id}/dispute", response_model=TimelineEvent)
async def dispute_timeline_event(
    event_id: str,
    dispute_req: TimelineDisputeRequest,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Record a date or narrative dispute while preserving both competing sources."""
    disputed = await timeline_service.dispute_event(
        event_id,
        dispute_req,
        actor_id=x_user_id
    )
    if not disputed:
        raise HTTPException(status_code=404, detail="Timeline event not found")
    return disputed


@router.post("/suggest", response_model=List[TimelineEvent])
async def suggest_timeline_events(
    sugg_req: TimelineSuggestionRequest,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Generate AI event suggestions validated against Phase 5 Memory Guardian.
    
    Suggestions are tagged with is_ai_suggested=True and status=PENDING_REVIEW.
    """
    suggestions = await timeline_service.generate_ai_suggestions(
        memorial_profile_id=sugg_req.memorial_profile_id,
        memory_id=sugg_req.memory_id,
        max_suggestions=sugg_req.max_suggestions,
        actor_id=x_user_id
    )
    return suggestions
