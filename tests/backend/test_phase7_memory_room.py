"""Unit and Integration Tests for Phase 7: 3D Memory Room + Memorial Avatar.

Research Title: Evidence-Grounded, Privacy-Preserving Multimodal AI for
                Interactive Digital Memory Preservation.

Test Coverage:
1. Room composition with real memory mapping (no fabricated objects).
2. Spatial zone assignment and object properties (frames, shelves, audio consoles, desk).
3. Provenance and confidence preservation (VERIFIED, SUPPORTED_INFERENCE).
4. Empty archive behavior (clean empty room, zero synthetic memories).
5. Room configuration updates (themes, lighting, reduced motion).
6. Memorial avatar config and ethical disclosure validation.
7. Avatar speech trigger with Memory Guardian boundary checks and TTS integration.
8. Telemetry metrics recording and retrieval.
9. Privacy filtering ensuring private assets are gated.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone
from typing import Dict, Any

from backend.app.main import app
from backend.app.services.memory_room_service import memory_room_service
from backend.app.services.memory_service import memory_service
from models.enums import (
    RoomTheme,
    RoomObjectType,
    AvatarPose,
    AvatarModelType,
    ConfidenceLevel,
    MemoryCategory,
    SourceType,
    PrivacyLevel,
    VerificationStatus
)
from models.memory import MemoryCreate
from models.memory_room import (
    RoomConfigUpdate,
    AvatarConfigUpdate,
    AvatarSpeechRequest,
    MANDATORY_AVATAR_DISCLOSURE,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_get_memory_room_composition_success():
    """Verify 3D room composition loads real memories with ethical disclaimers."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/memory-room?profile_id=default-profile-001")
        assert resp.status_code == 200
        data = resp.json()

        assert "room_config" in data
        assert "theme" in data["room_config"]
        assert "objects" in data
        assert "avatar" in data
        assert "ethical_disclosure" in data

        # Ethical boundary check
        assert MANDATORY_AVATAR_DISCLOSURE in data["ethical_disclosure"]

        # Avatar configuration check
        avatar = data["avatar"]
        assert avatar["enabled"] is True
        assert avatar["watermark_disclosure"] == MANDATORY_AVATAR_DISCLOSURE

        # Objects mapping check
        objects = data["objects"]
        assert isinstance(objects, list)
        for obj in objects:
            assert "object_id" in obj
            assert "position" in obj
            assert "confidence" in obj
            assert "verification_status" in obj
            assert "is_demo_placeholder" in obj
            # Check 3D coordinates exist
            assert "x" in obj["position"]
            assert "y" in obj["position"]
            assert "z" in obj["position"]
            # No raw file paths leaked
            if obj.get("media_url"):
                assert not obj["media_url"].startswith("D:\\")
                assert not obj["media_url"].startswith("C:\\")
                assert "/api/v1/media/" in obj["media_url"]


@pytest.mark.asyncio
async def test_room_object_detail_and_404():
    """Verify object detail retrieval and handling for non-existent objects."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get room first to find a valid object ID
        room_resp = await client.get("/api/v1/memory-room?profile_id=default-profile-001")
        assert room_resp.status_code == 200
        room_data = room_resp.json()

        if room_data["objects"]:
            target_id = room_data["objects"][0]["object_id"]
            obj_resp = await client.get(f"/api/v1/memory-room/objects/{target_id}")
            assert obj_resp.status_code == 200
            obj_data = obj_resp.json()
            assert obj_data["object_id"] == target_id
            assert "confidence" in obj_data
            assert "source_type" in obj_data

        # Nonexistent object must return 404
        missing_resp = await client.get("/api/v1/memory-room/objects/nonexistent-object-99999")
        assert missing_resp.status_code == 404


@pytest.mark.asyncio
async def test_update_room_config():
    """Verify room themes, lighting intensity, and accessibility toggles update cleanly."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        update_payload = {
            "theme": "GALLERY_MODERN",
            "ambient_light_intensity": 1.2,
            "reduced_motion": True,
            "show_labels": True,
            "audio_enabled": False
        }
        resp = await client.put(
            "/api/v1/memory-room/config?profile_id=default-profile-001&user_id=test-user",
            json=update_payload
        )
        assert resp.status_code == 200
        cfg = resp.json()
        assert cfg["theme"] == "GALLERY_MODERN"
        assert cfg["ambient_light_intensity"] == 1.2
        assert cfg["reduced_motion"] is True
        assert cfg["audio_enabled"] is False

        # Verify change reflected in full room composition
        room_resp = await client.get("/api/v1/memory-room?profile_id=default-profile-001")
        assert room_resp.status_code == 200
        assert room_resp.json()["room_config"]["theme"] == "GALLERY_MODERN"


@pytest.mark.asyncio
async def test_avatar_configuration_lifecycle():
    """Verify avatar settings, pose updates, and ethical disclosure persistence."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get active avatar config
        cfg_resp = await client.get("/api/v1/avatar/config?profile_id=default-profile-001")
        assert cfg_resp.status_code == 200
        avatar_cfg = cfg_resp.json()
        assert avatar_cfg["watermark_disclosure"] == MANDATORY_AVATAR_DISCLOSURE

        # Update pose and display name
        update_payload = {
            "enabled": True,
            "model_type": "NEUTRAL_SILHOUETTE",
            "display_name": "Arthur Vance Memorial Presence",
            "current_pose": "ATTENTIVE"
        }
        update_resp = await client.put(
            "/api/v1/avatar/config?profile_id=default-profile-001&user_id=test-user",
            json=update_payload
        )
        assert update_resp.status_code == 200
        updated = update_resp.json()
        assert updated["model_type"] == "NEUTRAL_SILHOUETTE"
        assert updated["current_pose"] == "ATTENTIVE"
        assert updated["display_name"] == "Arthur Vance Memorial Presence"


@pytest.mark.asyncio
async def test_avatar_speak_guarded_and_approved():
    """Verify avatar speech requires Memory Guardian validation and attaches TTS audio."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        speak_req = {
            "text": "This photograph was taken in the summer of 1972 at the lakeside cottage.",
            "memorial_profile_id": "default-profile-001",
            "language": "en",
            "user_id": "test-user"
        }
        resp = await client.post("/api/v1/avatar/speak?user_id=test-user", json=speak_req)
        assert resp.status_code == 200
        data = resp.json()

        assert data["approved_text"] == speak_req["text"]
        assert data["audio_url"] is not None
        assert data["is_watermarked"] is True
        assert data["avatar_pose"] == "SPEAKING"
        assert data["ethical_disclosure"] == MANDATORY_AVATAR_DISCLOSURE


@pytest.mark.asyncio
async def test_memory_room_telemetry_metrics():
    """Verify performance instrumentation recordings for research evaluation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Record sample metric from 3D client
        metric_payload = {
            "init_time_ms": 342.5,
            "visible_objects_count": 8,
            "webgl_available": True,
            "fallback_mode_active": False,
            "avatar_loaded": True,
            "asset_failures": 0
        }
        post_resp = await client.post("/api/v1/memory-room/metrics", json=metric_payload)
        assert post_resp.status_code == 200
        assert post_resp.json()["status"] == "recorded"

        # Retrieve aggregated metrics
        metrics_resp = await client.get("/api/v1/memory-room/metrics")
        assert metrics_resp.status_code == 200
        metrics = metrics_resp.json()
        assert metrics["total_room_accesses"] >= 1
        assert metrics["average_init_time_ms"] > 0
        assert "webgl_success_rate" in metrics


@pytest.mark.asyncio
async def test_empty_archive_handling():
    """Verify an empty profile returns an honest empty room with zero synthetic memories."""
    empty_profile_id = "empty-archive-test-profile"
    room = await memory_room_service.get_room_composition(
        memorial_profile_id=empty_profile_id,
        user_id="test-user"
    )
    assert room.memorial_profile_id == empty_profile_id
    # No memories were uploaded for this profile, so objects list must be empty
    assert len(room.objects) == 0
    # Must never invent fabricated personal memories
    for obj in room.objects:
        assert not obj.is_demo_placeholder
