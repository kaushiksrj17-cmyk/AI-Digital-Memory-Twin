"""Avatar and Presence Representation Endpoints.

CRITICAL ETHICAL REQUIREMENT:
Visual avatars are artistic, evidence-grounded representations.
They do not possess consciousness, independent will, or subjective emotions.
MANDATORY DISCLOSURE:
"AI-GENERATED MEMORIAL REPRESENTATION — NOT THE ACTUAL PERSON."
"""

from fastapi import APIRouter, HTTPException, Query, status, Body
from typing import Dict, Any, Optional

from models.memory_room import (
    AvatarConfig,
    AvatarConfigUpdate,
    AvatarSpeechRequest,
    AvatarSpeechResponse,
    MANDATORY_AVATAR_DISCLOSURE,
)
from backend.app.services.memory_room_service import memory_room_service

router = APIRouter()


@router.get("/status")
async def get_avatar_engine_status() -> Dict[str, Any]:
    """Retrieve visual presence engine and Three.js shader pipeline readiness."""
    return {
        "engine": "Three.js / WebGL Memorial Presence Shader",
        "status": "ready",
        "mesh_type": "evidence_grounded_spatial_representation",
        "ethical_boundary": MANDATORY_AVATAR_DISCLOSURE,
        "interactive_memory_room_ready": True
    }


@router.get("/config", response_model=AvatarConfig)
async def get_avatar_configuration(
    profile_id: str = Query("default-profile-001", description="Memorial subject profile ID")
):
    """Retrieve avatar configuration, pose, model type, and likeness consent status."""
    return await memory_room_service.get_avatar_config(
        memorial_profile_id=profile_id
    )


@router.put("/config", response_model=AvatarConfig)
async def update_avatar_configuration(
    config_update: AvatarConfigUpdate = Body(...),
    profile_id: str = Query("default-profile-001", description="Memorial subject profile ID"),
    user_id: str = Query("demo-user-001", description="Authenticated user ID")
):
    """Update avatar enabled state, pose, model type, and subtle responsiveness."""
    return await memory_room_service.update_avatar_config(
        memorial_profile_id=profile_id,
        update=config_update,
        user_id=user_id
    )


@router.post("/speak", response_model=AvatarSpeechResponse)
async def trigger_avatar_speech(
    speech_req: AvatarSpeechRequest = Body(...),
    user_id: str = Query("demo-user-001", description="Authenticated user ID")
):
    """Trigger verified avatar speech response guarded by Memory Guardian and authorized TTS."""
    try:
        return await memory_room_service.trigger_avatar_speech(
            request=speech_req,
            actor=user_id
        )
    except PermissionError as pe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(pe)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
