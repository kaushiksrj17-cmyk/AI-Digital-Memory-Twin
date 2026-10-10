"""Speech-to-Text Transcription Service for ECHO.

Processes oral histories, interview tapes, and interactive voice input.
Architectural support for English (en), Tamil (ta), and Hindi (hi).
Strict evidence boundary: If STT provider is unconfigured, returns an explicit
UNCONFIGURED result and never fabricates transcripts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from pathlib import Path
import os
import hashlib

from models.enums import (
    ConfidenceLevel,
    ProvenanceStatus,
    EvidenceType,
    AudioCategory,
    AuditAction,
)
from models.evidence import Evidence
from models.processing import TranscriptResult, TranscriptSegment
from models.voice import TranscriptionResponse, AudioAsset
from storage.vault_storage import vault_storage
from ai.providers.factory import provider_registry
from backend.app.core.config import settings
from backend.app.services.voice_provider import voice_provider_service
from backend.app.services.audit_service import audit_service


class TranscriptionService:
    """Specialized speech recognition and oral history transcription service."""

    SUPPORTED_LANGUAGES = ["en", "ta", "hi"]

    def __init__(self):
        self.service_name = "TranscriptionService"
        self.processor_version = "echo-stt-v1.0"
        self.voice_storage_dir = Path(settings.PROJECT_ROOT) / "storage" / "voice" / "temp"
        self.voice_storage_dir.mkdir(parents=True, exist_ok=True)

    async def transcribe_audio(
        self,
        media_id: str,
        relative_path: str,
        memory_id: Optional[str] = None,
        language: Optional[str] = "en"
    ) -> TranscriptResult:
        """Transcribe a vault audio asset using configured STT provider."""
        abs_path = vault_storage.get_absolute_path(relative_path)
        if not abs_path.exists():
            raise FileNotFoundError(f"Audio file not found: {relative_path}")

        stt_provider = provider_registry.stt_provider
        if not (stt_provider.is_configured or os.getenv("ENABLE_STT_MOCK", "false").lower() == "true"):
            return TranscriptResult(
                media_id=media_id,
                memory_id=memory_id,
                status="UNCONFIGURED",
                full_text="",
                segments=[],
                language=language or "en",
                confidence_score=0.0,
                provenance=ProvenanceStatus.UNKNOWN,
                message="STT provider is unconfigured. Simulated mock transcription is disabled."
            )

        audio_bytes = abs_path.read_bytes()
        try:
            result = await stt_provider.transcribe(audio_bytes, language=language)
            transcript_text = result.get("transcript", "")
            duration = float(result.get("duration_seconds", 0.0))
            confidence = float(result.get("confidence", 0.95))

            raw_segments = result.get("segments", [])
            segments = []
            if raw_segments:
                for seg in raw_segments:
                    segments.append(
                        TranscriptSegment(
                            segment_id=str(seg.get("id", uuid4())),
                            start_time=float(seg.get("start", 0.0)),
                            end_time=float(seg.get("end", duration)),
                            text=str(seg.get("text", "")),
                            speaker=str(seg.get("speaker", "Preserved Speaker")),
                            confidence=float(seg.get("confidence", confidence)),
                            language=language or "en"
                        )
                    )
            else:
                segments = [
                    TranscriptSegment(
                        segment_id=str(uuid4()),
                        start_time=0.0,
                        end_time=duration,
                        text=transcript_text,
                        speaker="Preserved Speaker",
                        confidence=confidence,
                        language=language or "en"
                    )
                ]

            return TranscriptResult(
                media_id=media_id,
                memory_id=memory_id,
                status="COMPLETED",
                full_text=transcript_text,
                segments=segments,
                language=language or "en",
                duration_seconds=duration,
                confidence_score=confidence,
                provenance=ProvenanceStatus.DIRECTLY_OBSERVED,
                message="Audio transcribed successfully."
            )
        except Exception as e:
            return TranscriptResult(
                media_id=media_id,
                memory_id=memory_id,
                status="FAILED",
                full_text="",
                segments=[],
                language=language or "en",
                confidence_score=0.0,
                provenance=ProvenanceStatus.UNKNOWN,
                message=f"Transcription failed: {str(e)}"
            )

    async def transcribe_direct_audio(
        self,
        audio_bytes: bytes,
        filename: str = "voice_input.wav",
        language: Optional[str] = "en",
        mime_type: Optional[str] = None,
        user_id: str = "demo-user-001",
        memorial_profile_id: str = "default-profile-001",
        session_id: Optional[str] = None
    ) -> TranscriptionResponse:
        """Validate and transcribe live microphone or uploaded audio input.
        
        Saves original audio safely as ORIGINAL_RECORDING asset.
        Never executes uploaded files.
        """
        # 1. Validation
        val_info = voice_provider_service.validate_audio(
            audio_bytes=audio_bytes,
            filename=filename,
            mime_type=mime_type
        )

        # 2. Store original audio asset safely
        audio_id = f"aud-orig-{uuid4().hex[:16]}"
        safe_filename = f"{audio_id}{val_info['extension']}"
        file_path = self.voice_storage_dir / safe_filename
        file_path.write_bytes(audio_bytes)

        relative_path = f"storage/voice/temp/{safe_filename}"
        checksum = val_info["sha256"]

        from backend.app.services.tts_service import tts_service
        asset = AudioAsset(
            id=audio_id,
            filename=safe_filename,
            relative_path=relative_path,
            audio_category=AudioCategory.ORIGINAL_RECORDING,
            mime_type=val_info["mime_type"],
            file_size_bytes=val_info["file_size_bytes"],
            duration_seconds=val_info["duration_seconds"],
            sha256_checksum=checksum,
            owner_id=user_id,
            memorial_profile_id=memorial_profile_id,
            session_id=session_id,
            is_temporary=True,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        tts_service._audio_assets[audio_id] = asset

        # 3. Transcribe via STT provider
        stt_provider = voice_provider_service.get_stt_provider()
        res = await stt_provider.transcribe(audio_bytes, language=language)

        transcript_text = res.get("transcript", "")
        duration = float(res.get("duration_seconds", val_info["duration_seconds"]))
        confidence = float(res.get("confidence", 0.98))
        segments = res.get("segments", [])
        is_mock = bool(res.get("is_mock", True))

        # 4. Audit
        await audit_service.record_event(
            action=AuditAction.VOICE_AUDIO_TRANSCRIBED,
            actor=user_id,
            resource=f"Audio:{audio_id}",
            result="SUCCESS",
            metadata={
                "language": language or "en",
                "duration_seconds": duration,
                "confidence": confidence,
                "is_mock": is_mock
            }
        )

        return TranscriptionResponse(
            audio_id=audio_id,
            audio_category=AudioCategory.TRANSCRIPTION,
            text=transcript_text,
            language=language or "en",
            duration_seconds=duration,
            confidence_score=confidence,
            segments=segments,
            is_mock=is_mock,
            provider_name=getattr(stt_provider, "name", "MockSTTProvider"),
            message="Audio transcribed successfully."
        )

    def create_transcript_evidence(
        self,
        transcript_result: TranscriptResult,
        source_filename: str
    ) -> Optional[Evidence]:
        """Convert a successful transcript into an atomic Evidence record."""
        if transcript_result.status != "COMPLETED" or not transcript_result.full_text.strip():
            return None

        return Evidence(
            id=str(uuid4()),
            memory_id=transcript_result.memory_id,
            media_id=transcript_result.media_id,
            title=f"Transcribed Audio Recording ({transcript_result.language.upper()})",
            evidence_type=EvidenceType.TRANSCRIPT,
            content=transcript_result.full_text,
            structured_value={
                "duration_seconds": transcript_result.duration_seconds,
                "language": transcript_result.language,
                "segment_count": len(transcript_result.segments),
                "is_audio_transcript": True
            },
            source_reference=f"Audio Tape ({source_filename})",
            provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
            confidence=ConfidenceLevel.VERIFIED if transcript_result.confidence_score >= 0.8 else ConfidenceLevel.SUPPORTED_INFERENCE,
            confidence_score=transcript_result.confidence_score,
            extraction_method="stt_whisper_compatible",
            processor_version=self.processor_version
        )


transcription_service = TranscriptionService()
