"""Interactive 3D Memory Room API Endpoints.

Research Title: Evidence-Grounded, Privacy-Preserving Multimodal AI for
                Interactive Digital Memory Preservation.

CRITICAL ETHICAL REQUIREMENTS:
- Every 3D room object maps directly to an authenticated real memory record.
- No fabricated memories or artificial spiritual artifacts.
- Visual avatars carry mandatory prominent ethical disclosure:
  "AI-GENERATED MEMORIAL REPRESENTATION — NOT THE ACTUAL PERSON."
- Strict privacy level and kinship consent checks on all media links.
"""

from fastapi import APIRouter, HTTPException, Query, status, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from models.enums import RoomTheme, MemoryCategory
from models.memory_room import (
    MemoryRoomResponse,
    RoomObject,
    RoomConfiguration,
    RoomConfigUpdate,
    MemoryRoomMetrics,
)
from backend.app.services.memory_room_service import memory_room_service

router = APIRouter()


class MetricRecordRequest(BaseModel):
    init_time_ms: float = Field(default=0.0, ge=0.0)
    visible_objects_count: int = Field(default=0, ge=0)
    webgl_available: bool = True
    fallback_mode_active: bool = False
    avatar_loaded: bool = False
    asset_failures: int = Field(default=0, ge=0)


@router.get("", response_model=MemoryRoomResponse)
@router.get("/", response_model=MemoryRoomResponse)
async def get_memory_room(
    profile_id: str = Query("default-profile-001", description="Memorial subject profile ID"),
    user_id: str = Query("demo-user-001", description="Current requesting user ID"),
    category: Optional[MemoryCategory] = Query(None, description="Optional category filter"),
    search: Optional[str] = Query(None, description="Optional search query keyword")
):
    """Retrieve complete 3D room composition, spatial objects, and memorial avatar state."""
    return await memory_room_service.get_room_composition(
        memorial_profile_id=profile_id,
        user_id=user_id,
        category_filter=category,
        search_query=search
    )


@router.get("/objects/{object_id}", response_model=RoomObject)
async def get_room_object(
    object_id: str,
    profile_id: str = Query("default-profile-001", description="Memorial subject profile ID"),
    user_id: str = Query("demo-user-001", description="Current requesting user ID")
):
    """Retrieve detailed evidence and metadata for a specific 3D room object."""
    obj = await memory_room_service.get_room_object_detail(
        object_id=object_id,
        memorial_profile_id=profile_id,
        user_id=user_id
    )
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room object '{object_id}' not found or access denied."
        )
    return obj


@router.put("/config", response_model=RoomConfiguration)
async def update_room_configuration(
    config_update: RoomConfigUpdate = Body(...),
    profile_id: str = Query("default-profile-001", description="Memorial profile ID"),
    user_id: str = Query("demo-user-001", description="Authenticated user ID")
):
    """Update ambient lighting, room theme, and reduced-motion preferences."""
    return await memory_room_service.update_room_config(
        memorial_profile_id=profile_id,
        update=config_update,
        user_id=user_id
    )


@router.get("/metrics", response_model=MemoryRoomMetrics)
async def get_room_telemetry_metrics():
    """Retrieve research instrumentation metrics for 3D room initialization and accessibility."""
    return memory_room_service.get_metrics()


@router.post("/metrics")
async def record_room_telemetry(
    metric: MetricRecordRequest,
    profile_id: str = Query("default-profile-001", description="Memorial profile ID")
):
    """Record client-side 3D performance and accessibility instrumentation."""
    memory_room_service.record_metric(
        profile_id=profile_id,
        init_time_ms=metric.init_time_ms,
        object_count=metric.visible_objects_count,
        webgl_available=metric.webgl_available,
        fallback_used=metric.fallback_mode_active,
        avatar_loaded=metric.avatar_loaded,
        asset_failures=metric.asset_failures
    )
    return {"status": "recorded"}
