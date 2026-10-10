"""Voice Profile Management Service for ECHO.

Manages authorized voice-profile metadata, lifecycle states, and access boundaries.
Voice Profile Lifecycle:
- UNCONFIGURED
- PENDING_CONSENT
- READY
- REVOKED
- DISABLED

CRITICAL SAFEGUARD:
Never clones an identifiable voice without verified legal consent.
Revocation immediately blocks all future synthesis using that profile.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import (
    VoiceProfileStatus,
    VoiceType,
    ConsentStatus,
    ConsentType,
    AuditAction,
)
from models.voice import (
    VoiceProfile,
    VoiceProfileCreate,
    VoiceProfileUpdate,
)
from backend.app.services.voice_consent_service import voice_consent_service
from backend.app.services.audit_service import audit_service


class VoiceProfileService:
    """Manages voice profiles, training references, and ethical usage limits."""

    def __init__(self):
        self._profiles: Dict[str, VoiceProfile] = {}
        self._init_default_profiles()

    def _init_default_profiles(self):
        """Seed baseline generic synthetic voice and demonstration profiles."""
        # 1. Standard Generic Synthetic Voice (Default for all users)
        generic_profile = VoiceProfile(
            id="vp-generic-standard",
            memorial_profile_id="default-profile-001",
            owner_id="system",
            name="Standard Generic Memorial Voice (AI Assistant)",
            description="Ethically safe generic synthetic voice. Not trained on authentic personal recordings.",
            voice_type=VoiceType.GENERIC_SYNTHETIC,
            status=VoiceProfileStatus.READY,
            supported_languages=["en", "ta", "hi"],
            provider_id="mock-tts",
            provider_voice_id="echo-generic-01",
            retention_policy="PERMANENT_SYSTEM",
            sample_duration_seconds=0.0,
            consent_status=ConsentStatus.GRANTED,
            consent_verified_at=datetime.now(timezone.utc),
            metadata_json={"is_default_generic": True}
        )
        self._profiles[generic_profile.id] = generic_profile

        # 2. Authorized Memorial Custom Voice (Kinship authorized demonstration profile)
        custom_profile = VoiceProfile(
            id="vp-edinburgh-memorial-01",
            memorial_profile_id="default-profile-001",
            owner_id="demo-user-001",
            name="Archival Edinburgh Memorial Voice",
            description="Authorized acoustic representation based on preserved 1984 oral history tapes.",
            voice_type=VoiceType.AUTHORIZED_MEMORIAL_CUSTOM,
            status=VoiceProfileStatus.READY,
            supported_languages=["en", "ta", "hi"],
            provider_id="mock-tts",
            provider_voice_id="echo-custom-edinburgh-01",
            consent_id="consent-voice-demo-01",
            consent_status=ConsentStatus.GRANTED,
            consent_verified_at=datetime.now(timezone.utc),
            retention_policy="FAMILY_ARCHIVE",
            sample_duration_seconds=420.5,
            metadata_json={"archival_reel": "Reel 4", "recording_year": 1984}
        )
        self._profiles[custom_profile.id] = custom_profile

    async def list_profiles(
        self,
        memorial_profile_id: Optional[str] = None,
        user_id: Optional[str] = None,
        include_revoked: bool = True
    ) -> List[VoiceProfile]:
        """List accessible voice profiles for user and memorial profile."""
        profiles = list(self._profiles.values())
        if memorial_profile_id:
            profiles = [
                p for p in profiles
                if p.memorial_profile_id == memorial_profile_id or p.owner_id == "system"
            ]
        if not include_revoked:
            profiles = [p for p in profiles if p.status != VoiceProfileStatus.REVOKED]
        return sorted(profiles, key=lambda p: p.created_at, reverse=True)

    async def get_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Retrieve voice profile by ID with latest status."""
        return self._profiles.get(profile_id)

    async def create_profile(
        self,
        profile_in: VoiceProfileCreate,
        actor: str = "demo-user-001"
    ) -> VoiceProfile:
        """Create new voice profile subject to consent verification."""
        profile_id = f"vp-{uuid4().hex[:12]}"

        # If custom voice requested, verify consent exists
        status = VoiceProfileStatus.PENDING_CONSENT
        consent_status = ConsentStatus.PENDING
        verified_at = None

        if profile_in.voice_type == VoiceType.AUTHORIZED_MEMORIAL_CUSTOM:
            auth_check = await voice_consent_service.verify_synthesis_authorization(
                voice_type=VoiceType.AUTHORIZED_MEMORIAL_CUSTOM,
                voice_profile_id=profile_id,
                memorial_profile_id=profile_in.memorial_profile_id,
                user_id=actor
            )
            if auth_check["allowed"]:
                status = VoiceProfileStatus.READY
                consent_status = ConsentStatus.GRANTED
                verified_at = datetime.now(timezone.utc)
            else:
                status = VoiceProfileStatus.PENDING_CONSENT
                consent_status = ConsentStatus.PENDING
        else:
            # Generic synthetic voice does not require custom voice consent
            status = VoiceProfileStatus.READY
            consent_status = ConsentStatus.GRANTED
            verified_at = datetime.now(timezone.utc)

        profile = VoiceProfile(
            id=profile_id,
            memorial_profile_id=profile_in.memorial_profile_id,
            owner_id=actor,
            name=profile_in.name,
            description=profile_in.description,
            voice_type=profile_in.voice_type,
            status=status,
            supported_languages=profile_in.supported_languages,
            provider_id=profile_in.provider_id,
            provider_voice_id=profile_in.provider_voice_id,
            consent_id=profile_in.consent_id,
            consent_status=consent_status,
            consent_verified_at=verified_at,
            retention_policy=profile_in.retention_policy,
            sample_duration_seconds=profile_in.sample_duration_seconds or 0.0,
            metadata_json=profile_in.metadata_json or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        self._profiles[profile.id] = profile

        await audit_service.record_event(
            action=AuditAction.VOICE_PROFILE_CREATED,
            actor=actor,
            resource=f"VoiceProfile:{profile.id}",
            result="SUCCESS",
            metadata={
                "name": profile.name,
                "voice_type": profile.voice_type.value,
                "status": profile.status.value
            }
        )

        return profile

    async def update_profile(
        self,
        profile_id: str,
        update_in: VoiceProfileUpdate,
        actor: str = "demo-user-001"
    ) -> Optional[VoiceProfile]:
        """Update existing voice profile metadata."""
        profile = self._profiles.get(profile_id)
        if not profile:
            return None

        if update_in.name is not None:
            profile.name = update_in.name
        if update_in.description is not None:
            profile.description = update_in.description
        if update_in.provider_voice_id is not None:
            profile.provider_voice_id = update_in.provider_voice_id
        if update_in.retention_policy is not None:
            profile.retention_policy = update_in.retention_policy
        if update_in.metadata_json is not None:
            profile.metadata_json.update(update_in.metadata_json)

        profile.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.VOICE_PROFILE_UPDATED,
            actor=actor,
            resource=f"VoiceProfile:{profile_id}",
            result="SUCCESS",
            metadata={"updated_fields": list(update_in.model_dump(exclude_unset=True).keys())}
        )

        return profile

    async def revoke_profile(
        self,
        profile_id: str,
        reason: str = "Revocation requested by memorial guardian",
        actor: str = "demo-user-001"
    ) -> Optional[VoiceProfile]:
        """Immediately revoke a voice profile and block all future synthesis."""
        profile = self._profiles.get(profile_id)
        if not profile:
            return None

        now = datetime.now(timezone.utc)
        profile.status = VoiceProfileStatus.REVOKED
        profile.consent_status = ConsentStatus.REVOKED
        profile.revoked_at = now
        profile.updated_at = now

        # Revoke underlying consent record if present
        await voice_consent_service.revoke_voice_consent(
            consent_id=profile.consent_id,
            memorial_profile_id=profile.memorial_profile_id,
            actor=actor,
            reason=reason
        )

        await audit_service.record_event(
            action=AuditAction.VOICE_PROFILE_REVOKED,
            actor=actor,
            resource=f"VoiceProfile:{profile_id}",
            result="REVOKED",
            metadata={"reason": reason, "revoked_at": str(now)}
        )

        return profile

    async def disable_profile(
        self,
        profile_id: str,
        actor: str = "demo-user-001"
    ) -> Optional[VoiceProfile]:
        """Disable a voice profile temporarily without full legal revocation."""
        profile = self._profiles.get(profile_id)
        if not profile:
            return None

        now = datetime.now(timezone.utc)
        profile.status = VoiceProfileStatus.DISABLED
        profile.disabled_at = now
        profile.updated_at = now

        await audit_service.record_event(
            action=AuditAction.VOICE_PROFILE_DISABLED,
            actor=actor,
            resource=f"VoiceProfile:{profile_id}",
            result="DISABLED",
            metadata={"disabled_at": str(now)}
        )

        return profile


voice_profile_service = VoiceProfileService()
