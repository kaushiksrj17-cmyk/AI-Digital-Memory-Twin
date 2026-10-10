"""3D Memory Room and Memorial Avatar Domain Models for ECHO.

Research Title: Evidence-Grounded, Privacy-Preserving Multimodal AI for
                Interactive Digital Memory Preservation.

ETHICAL REQUIREMENTS:
- The avatar is a visual interface representing a memorial subject.
- It is NOT the actual person, a digital resurrection, conscious being, or identity.
- Explicit label mandatory on all avatar interfaces:
  "AI-GENERATED MEMORIAL REPRESENTATION — NOT THE ACTUAL PERSON."
- 3D objects are navigation and visualization mechanisms connected to real archive evidence,
  not proof that decorative room objects existed in real life.
- Zero-fabrication: if an archive has zero memories, display an honest empty room state.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import (
    RoomObjectType,
    RoomTheme,
    AvatarPose,
    AvatarModelType,
    MemoryCategory,
    SourceType,
    ConfidenceLevel,
    VerificationStatus,
    PrivacyLevel,
    GuardianDecision,
)

MANDATORY_AVATAR_DISCLOSURE = "AI-GENERATED MEMORIAL REPRESENTATION — NOT THE ACTUAL PERSON."


class RoomVector3(BaseModel):
    """3D Cartesian coordinate vector."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class RoomObject(BaseModel):
    """Interactive 3D entity in the memory room connected to genuine archival evidence."""
    object_id: str = Field(default_factory=lambda: f"obj-{uuid4().hex[:12]}")
    memory_id: Optional[str] = Field(None, description="Linked Memory record ID")
    media_id: Optional[str] = Field(None, description="Linked Media asset ID")
    title: str = Field(..., description="Archival title of the memory")
    description: str = Field(default="", description="Grounded description or oral history excerpt")
    object_type: RoomObjectType = Field(default=RoomObjectType.PHOTO_FRAME)
    category: MemoryCategory = Field(default=MemoryCategory.OTHER)
    source_type: SourceType = Field(default=SourceType.FAMILY_STORY)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.VERIFIED)
    verification_status: VerificationStatus = Field(default=VerificationStatus.VERIFIED)
    privacy_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    date: Optional[str] = Field(None, description="Documented date (e.g. '1968-06-22')")
    location: Optional[str] = Field(None, description="Documented geographical location")
    people: List[str] = Field(default_factory=list, description="Associated individuals")
    
    # Spatial transform in the 3D room
    position: RoomVector3 = Field(default_factory=RoomVector3)
    rotation: RoomVector3 = Field(default_factory=RoomVector3)
    scale: RoomVector3 = Field(default_factory=lambda: RoomVector3(x=1.0, y=1.0, z=1.0))
    
    # Safe media reference URLs (never raw filesystem paths)
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    audio_url: Optional[str] = None
    
    # Integrity and metadata
    is_demo_placeholder: bool = False
    associated_events: List[str] = Field(default_factory=list)
    associated_dna_keys: List[str] = Field(default_factory=list)
    color_accent: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RoomConfiguration(BaseModel):
    """Atmospheric and accessibility settings for the 3D room environment."""
    room_id: str = Field(default="room-default-001")
    memorial_profile_id: str = "default-profile-001"
    theme: RoomTheme = Field(default=RoomTheme.ARCHIVAL_WARM)
    ambient_light_intensity: float = Field(default=0.75, ge=0.1, le=2.0)
    floor_material: str = "hardwood_oak"
    wall_color: str = "#1e293b"
    camera_initial_position: RoomVector3 = Field(default_factory=lambda: RoomVector3(x=0.0, y=2.0, z=6.5))
    show_labels: bool = True
    reduced_motion: bool = False
    audio_enabled: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)


class RoomConfigUpdate(BaseModel):
    """Payload for updating user room settings."""
    theme: Optional[RoomTheme] = None
    ambient_light_intensity: Optional[float] = None
    show_labels: Optional[bool] = None
    reduced_motion: Optional[bool] = None
    audio_enabled: Optional[bool] = None


class AvatarConfig(BaseModel):
    """Configuration and ethical safeguards for the 3D memorial presence avatar."""
    enabled: bool = True
    memorial_profile_id: str = "default-profile-001"
    model_type: AvatarModelType = Field(default=AvatarModelType.STYLIZED_GENERIC)
    display_name: str = "Memorial Presence Guide"
    position: RoomVector3 = Field(default_factory=lambda: RoomVector3(x=0.0, y=0.0, z=-2.2))
    rotation: RoomVector3 = Field(default_factory=lambda: RoomVector3(x=0.0, y=0.0, z=0.0))
    current_pose: AvatarPose = Field(default=AvatarPose.IDLE_NEUTRAL)
    is_speaking: bool = False
    speaking_text: Optional[str] = None
    speaking_audio_url: Optional[str] = None
    is_authorized: bool = True
    consent_verified: bool = True
    watermark_disclosure: str = MANDATORY_AVATAR_DISCLOSURE
    asset_url: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class AvatarConfigUpdate(BaseModel):
    """Payload for updating avatar options."""
    model_config = ConfigDict(protected_namespaces=())

    enabled: Optional[bool] = None
    model_type: Optional[AvatarModelType] = None
    display_name: Optional[str] = None
    current_pose: Optional[AvatarPose] = None


class AvatarSpeechRequest(BaseModel):
    """Request to trigger avatar speech with Memory Guardian validation."""
    text: str = Field(..., min_length=1, max_length=2000)
    memorial_profile_id: str = "default-profile-001"
    voice_profile_id: Optional[str] = None
    language: str = "en"
    user_id: str = "demo-user-001"


class AvatarSpeechResponse(BaseModel):
    """Approved spoken response with synchronized audio and guardian verification."""
    speech_id: str
    approved_text: str
    guardian_decision: GuardianDecision
    audio_url: Optional[str]
    duration_seconds: float
    is_watermarked: bool
    ethical_disclosure: str
    avatar_pose: AvatarPose = AvatarPose.SPEAKING
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryRoomResponse(BaseModel):
    """Complete 3D room payload returned to frontend clients."""
    memorial_profile_id: str
    room_config: RoomConfiguration
    avatar: AvatarConfig
    objects: List[RoomObject]
    total_objects: int
    verified_count: int
    supported_inference_count: int
    unknown_count: int
    categories_present: List[str]
    ethical_disclosure: str = MANDATORY_AVATAR_DISCLOSURE
    webgl_supported: bool = True
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryRoomMetrics(BaseModel):
    """Research instrumentation for 3D room rendering performance and access."""
    total_room_accesses: int = 0
    average_init_time_ms: float = 0.0
    average_selection_latency_ms: float = 0.0
    total_objects_rendered: int = 0
    webgl_success_rate: float = 1.0
    fallback_list_view_usage: int = 0
    avatar_speaking_events: int = 0
    ethical_disclosures_served: int = 0
