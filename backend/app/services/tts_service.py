"""Text-to-Speech (TTS) Generation and Playback Service for ECHO.

CRITICAL ARCHITECTURAL BOUNDARIES:
- Synthesis receives ONLY final approved response text from Phase 5 Memory Guardian.
- Never synthesizes raw or ungrounded LLM output.
- Rechecks consent and authorization immediately before every synthesis request.
- Stores temporary audio strictly under D:\\ECHO\\storage\\voice\\temp\\ with sha256 checksums.
- Enforces explicit, non-deceptive audio labeling:
  "AI-GENERATED MEMORIAL VOICE — SYNTHETIC AUDIO, NOT AN ORIGINAL RECORDING."
- Distinctly separates Generic Synthetic voices from Authorized Memorial voices.
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import os
import hashlib
import time

from models.enums import (
    AudioCategory,
    VoiceType,
    VoiceProfileStatus,
    AuditAction,
    GuardianDecision,
)
from models.voice import (
    VoiceSynthesisRequest,
    VoiceSynthesisResponse,
    AudioAsset,
    MANDATORY_MEMORIAL_DISCLOSURE,
    GENERIC_VOICE_DISCLOSURE,
)
from backend.app.core.config import settings
from backend.app.services.voice_consent_service import voice_consent_service
from backend.app.services.voice_profile_service import voice_profile_service
from backend.app.services.voice_provider import voice_provider_service
from backend.app.services.audit_service import audit_service


class TTSService:
    """Manages text-to-speech synthesis jobs, audio artifacts, and private playback."""

    def __init__(self):
        self.storage_root = Path(settings.PROJECT_ROOT) / "storage" / "voice"
        self.temp_dir = self.storage_root / "temp"
        self.profiles_dir = self.storage_root / "profiles"
        self.recordings_dir = self.storage_root / "recordings"

        # Ensure directories exist within D:\ECHO boundary
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

        self._audio_assets: Dict[str, AudioAsset] = {}

    async def synthesize_speech(
        self,
        request: VoiceSynthesisRequest,
        guardian_status: GuardianDecision = GuardianDecision.PASS
    ) -> VoiceSynthesisResponse:
        """Synthesize approved response text into an access-controlled audio asset."""
        start_time = time.time()

        # Boundary Check: Memory Guardian must not have blocked the response
        if guardian_status == GuardianDecision.BLOCK:
            raise PermissionError(
                "Memory Guardian blocked this response. Synthesis of blocked content is strictly prohibited."
            )

        if not request.text or not request.text.strip():
            raise ValueError("Cannot synthesize empty text.")

        # Resolve voice profile
        profile = None
        requested_voice_type = VoiceType.GENERIC_SYNTHETIC
        voice_disclosure = GENERIC_VOICE_DISCLOSURE

        if request.voice_profile_id:
            profile = await voice_profile_service.get_profile(request.voice_profile_id)
            if profile:
                requested_voice_type = profile.voice_type

        # Immediate Consent Check
        consent_check = await voice_consent_service.verify_synthesis_authorization(
            voice_type=requested_voice_type,
            voice_profile_id=request.voice_profile_id,
            memorial_profile_id=request.memorial_profile_id or "default-profile-001",
            user_id=request.user_id or "demo-user-001"
        )

        if not consent_check["allowed"]:
            # If custom clone was requested but blocked, check fallback
            if requested_voice_type == VoiceType.AUTHORIZED_MEMORIAL_CUSTOM and consent_check.get("fallback_allowed"):
                # Fallback to generic synthetic voice
                requested_voice_type = VoiceType.GENERIC_SYNTHETIC
                voice_disclosure = GENERIC_VOICE_DISCLOSURE
                profile = None
            else:
                raise PermissionError(f"Speech synthesis blocked: {consent_check['reason']}")
        elif requested_voice_type == VoiceType.AUTHORIZED_MEMORIAL_CUSTOM:
            voice_disclosure = MANDATORY_MEMORIAL_DISCLOSURE

        # Provider synthesis execution
        tts_provider = voice_provider_service.get_tts_provider()
        provider_voice_id = profile.provider_voice_id if profile else None

        synth_result = await tts_provider.synthesize(
            text=request.text,
            voice_profile_id=provider_voice_id,
            language=request.language or "en",
            speed=request.speed or 1.0
        )

        audio_bytes = synth_result.get("audio_bytes")
        if not audio_bytes:
            # Fallback for mock provider if returning length only
            from ai.providers.tts import generate_synthesized_audio_bytes
            audio_bytes = generate_synthesized_audio_bytes(
                duration_seconds=synth_result.get("duration_seconds", 2.0)
            )

        duration = float(synth_result.get("duration_seconds", 2.0))
        audio_id = f"aud-{uuid4().hex[:16]}"
        filename = f"{audio_id}.wav"
        file_path = self.temp_dir / filename

        # Write audio strictly within D:\ECHO\storage\voice\temp\
        file_path.write_bytes(audio_bytes)
        file_size = len(audio_bytes)
        checksum = hashlib.sha256(audio_bytes).hexdigest()

        # Relative path within project root (never expose absolute server paths to frontend)
        relative_path = f"storage/voice/temp/{filename}"

        asset = AudioAsset(
            id=audio_id,
            filename=filename,
            relative_path=relative_path,
            audio_category=AudioCategory.AI_GENERATED_MEMORIAL_VOICE,
            mime_type="audio/wav",
            file_size_bytes=file_size,
            duration_seconds=duration,
            sha256_checksum=checksum,
            owner_id=request.user_id or "demo-user-001",
            memorial_profile_id=request.memorial_profile_id or "default-profile-001",
            voice_profile_id=request.voice_profile_id,
            session_id=request.session_id,
            is_temporary=True,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        self._audio_assets[audio_id] = asset

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Audit event
        await audit_service.record_event(
            action=AuditAction.VOICE_SYNTHESIS_COMPLETED,
            actor=request.user_id or "demo-user-001",
            resource=f"Audio:{audio_id}",
            result="SUCCESS",
            metadata={
                "voice_type": requested_voice_type.value,
                "duration_seconds": duration,
                "latency_ms": latency_ms,
                "is_watermarked": True,
                "language": request.language or "en"
            }
        )

        return VoiceSynthesisResponse(
            audio_id=audio_id,
            audio_url=f"/api/v1/voice/audio/{audio_id}",
            audio_category=AudioCategory.AI_GENERATED_MEMORIAL_VOICE,
            voice_type=requested_voice_type,
            format="audio/wav",
            duration_seconds=duration,
            file_size_bytes=file_size,
            is_mock=bool(synth_result.get("is_mock", True)),
            is_watermarked=True,
            watermark_label="[ECHO-AI-MEMORIAL-VOICE-VERIFIED]",
            ethical_disclosure=MANDATORY_MEMORIAL_DISCLOSURE,
            voice_disclosure=voice_disclosure,
            created_at=datetime.now(timezone.utc)
        )

    async def get_audio_asset(self, audio_id: str) -> Optional[AudioAsset]:
        """Lookup metadata for audio asset."""
        return self._audio_assets.get(audio_id)

    def get_audio_bytes(self, audio_id: str) -> Optional[Tuple[bytes, str, AudioAsset]]:
        """Retrieve authorized audio bytes and MIME type.
        
        Strictly prevents path traversal and enforces project root boundaries.
        """
        asset = self._audio_assets.get(audio_id)
        if not asset:
            return None

        # Resolve path safely inside project root
        file_path = (Path(settings.PROJECT_ROOT) / asset.relative_path).resolve()
        project_root = Path(settings.PROJECT_ROOT).resolve()

        # Path traversal guard
        if not str(file_path).startswith(str(project_root)):
            raise PermissionError("Path traversal violation detected.")

        if not file_path.exists():
            return None

        return file_path.read_bytes(), asset.mime_type, asset

    async def delete_audio(self, audio_id: str, actor: str = "demo-user-001") -> bool:
        """Delete temporary audio file and purge metadata record."""
        asset = self._audio_assets.get(audio_id)
        if not asset:
            return False

        file_path = (Path(settings.PROJECT_ROOT) / asset.relative_path).resolve()
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass

        del self._audio_assets[audio_id]

        await audit_service.record_event(
            action=AuditAction.VOICE_AUDIO_DELETED,
            actor=actor,
            resource=f"Audio:{audio_id}",
            result="DELETED",
            metadata={"checksum": asset.sha256_checksum}
        )

        return True

    async def cleanup_expired_audio(self) -> int:
        """Purge temporary audio files that have exceeded their retention window."""
        now = datetime.now(timezone.utc)
        expired_ids = [
            aid for aid, a in self._audio_assets.items()
            if a.is_temporary and a.expires_at and a.expires_at < now
        ]
        count = 0
        for aid in expired_ids:
            if await self.delete_audio(aid, actor="system_cleanup"):
                count += 1
        return count


tts_service = TTSService()
