"""Voice and Audio Interaction API Endpoints for ECHO.

Research Title: Evidence-Grounded, Privacy-Preserving Multimodal AI for
                Interactive Digital Memory Preservation.

CRITICAL ETHICAL REQUIREMENTS:
- All synthesized audio must embed digital watermarks and explicit disclosures.
- Distinct audio categories:
  1. ORIGINAL RECORDING (authentic preserved audio)
  2. TRANSCRIPTION (extracted text)
  3. AI-GENERATED MEMORIAL VOICE (synthetic audio)
- Never present synthesized audio as an authentic original recording.
- Blocked responses from Phase 5 Memory Guardian are NEVER synthesized.
- Custom voice synthesis is strictly prohibited without verified consent.
- Never leak server filesystem paths, secrets, raw embeddings, or provider tokens.
"""

from fastapi import (
    APIRouter,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Query,
    Response,
    Request,
)
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import base64
from datetime import datetime, timezone

from models.enums import (
    AudioCategory,
    VoiceType,
    VoiceProfileStatus,
    VoiceProcessingState,
    ConsentType,
    ConsentStatus,
    GuardianDecision,
    AuditAction,
)
from models.voice import (
    VoiceProfile,
    VoiceProfileCreate,
    VoiceProfileUpdate,
    VoiceSession,
    VoiceSessionCreate,
    VoiceSynthesisRequest,
    VoiceSynthesisResponse,
    VoiceInteractionResponse,
    VoiceTranscriptQueryRequest,
    AudioUploadResponse,
    TranscriptionResponse,
    VoiceMetrics,
    MANDATORY_MEMORIAL_DISCLOSURE,
)
from backend.app.services.voice_provider import voice_provider_service
from backend.app.services.voice_consent_service import voice_consent_service
from backend.app.services.voice_profile_service import voice_profile_service
from backend.app.services.voice_session_service import voice_session_service
from backend.app.services.transcription_service import transcription_service
from backend.app.services.tts_service import tts_service
from backend.app.services.speech_service import speech_service
from backend.app.services.audit_service import audit_service

router = APIRouter()


# ==============================================================================
# Helper Schemas for JSON-based Audio Payloads
# ==============================================================================

class AudioPayloadJSON(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio bytes")
    filename: Optional[str] = "input.wav"
    language: Optional[str] = "en"
    session_id: Optional[str] = None
    voice_profile_id: Optional[str] = None
    memorial_profile_id: Optional[str] = "default-profile-001"
    user_id: Optional[str] = "demo-user-001"
    mime_type: Optional[str] = "audio/wav"


class VoiceConsentRequest(BaseModel):
    granter_name: str
    granter_relationship: str = "Guardian"
    consent_type: ConsentType = ConsentType.CUSTOM_VOICE_SYNTHESIS
    memorial_profile_id: str = "default-profile-001"
    scope: str = "MEMORIAL_VOICE_SYNTHESIS"
    document_reference: Optional[str] = None
    notes: Optional[str] = None
    user_id: str = "demo-user-001"


# ==============================================================================
# 1. Capability & Status Endpoints
# ==============================================================================

@router.get("/status")
@router.get("/capabilities")
async def get_voice_capabilities():
    """Retrieve speech interaction engine capabilities, languages, and provider status."""
    return voice_provider_service.get_capabilities()


# ==============================================================================
# 2. Voice Session Endpoints
# ==============================================================================

@router.post("/sessions", response_model=VoiceSession, status_code=status.HTTP_201_CREATED)
async def create_voice_session(
    data: VoiceSessionCreate,
    user_id: str = "demo-user-001"
):
    """Start an interactive voice session in IDLE state."""
    return await voice_session_service.create_session(data, actor=user_id)


@router.get("/sessions", response_model=List[VoiceSession])
async def list_voice_sessions(
    memorial_profile_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """List voice interaction sessions."""
    return await voice_session_service.list_sessions(
        memorial_profile_id=memorial_profile_id,
        user_id=user_id
    )


@router.get("/sessions/{session_id}", response_model=VoiceSession)
async def get_voice_session(session_id: str):
    """Get status, transcripts, and telemetry for a specific voice session."""
    session = await voice_session_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice session '{session_id}' not found."
        )
    return session


@router.post("/sessions/{session_id}/cancel", response_model=VoiceSession)
async def cancel_voice_session(session_id: str):
    """Cancel an active voice interaction session."""
    session = await voice_session_service.cancel_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice session '{session_id}' not found."
        )
    return session


# ==============================================================================
# 3. Speech-to-Text Transcription Endpoints
# ==============================================================================

async def _extract_audio_request_data(request: Request) -> Dict[str, Any]:
    """Helper to parse either application/json or multipart/form-data audio requests."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        payload = AudioPayloadJSON.model_validate(body)
        try:
            audio_bytes = base64.b64decode(payload.audio_base64)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid base64 audio payload."
            )
        return {
            "audio_bytes": audio_bytes,
            "filename": payload.filename or "recording.wav",
            "mime": payload.mime_type or "audio/wav",
            "language": payload.language or "en",
            "session_id": payload.session_id,
            "voice_profile_id": payload.voice_profile_id,
            "memorial_profile_id": payload.memorial_profile_id or "default-profile-001",
            "user_id": payload.user_id or "demo-user-001",
        }
    else:
        form = await request.form()
        uploaded_file = form.get("file")
        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide an audio file or base64 audio payload."
            )
        audio_bytes = await uploaded_file.read()
        filename = getattr(uploaded_file, "filename", "recording.wav") or "recording.wav"
        mime = getattr(uploaded_file, "content_type", None)
        return {
            "audio_bytes": audio_bytes,
            "filename": filename,
            "mime": mime,
            "language": str(form.get("language") or "en"),
            "session_id": form.get("session_id"),
            "voice_profile_id": form.get("voice_profile_id"),
            "memorial_profile_id": str(form.get("memorial_profile_id") or "default-profile-001"),
            "user_id": str(form.get("user_id") or "demo-user-001"),
        }


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio_endpoint(request: Request):
    """Upload audio for transcription (supports multipart file upload or JSON base64)."""
    data = await _extract_audio_request_data(request)

    try:
        resp = await transcription_service.transcribe_direct_audio(
            audio_bytes=data["audio_bytes"],
            filename=data["filename"],
            language=data["language"],
            mime_type=data["mime"],
            user_id=data["user_id"],
            session_id=data["session_id"]
        )
        if data["session_id"]:
            await voice_session_service.set_transcript(data["session_id"], resp.text, is_edited=False)
        return resp
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Transcription error: {str(e)}")


# ==============================================================================
# 4. End-to-End Voice Pipeline Endpoints
# ==============================================================================

@router.post("/pipeline", response_model=VoiceInteractionResponse)
@router.post("/interact", response_model=VoiceInteractionResponse)
async def complete_voice_pipeline_endpoint(request: Request):
    """Submit spoken question through the complete evidence-grounded voice pipeline."""
    data = await _extract_audio_request_data(request)

    try:
        return await speech_service.execute_voice_pipeline(
            audio_bytes=data["audio_bytes"],
            filename=data["filename"],
            mime_type=data["mime"],
            language=data["language"],
            session_id=data["session_id"],
            memorial_profile_id=data["memorial_profile_id"],
            voice_profile_id=data["voice_profile_id"],
            user_id=data["user_id"]
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Voice pipeline error: {str(e)}")


@router.post("/query-transcript", response_model=VoiceInteractionResponse)
async def query_transcript_endpoint(
    req: VoiceTranscriptQueryRequest,
    user_id: str = "demo-user-001",
    memorial_profile_id: str = "default-profile-001"
):
    """Submit a transcribed (or user-edited) question through Phase 5 RAG and TTS."""
    try:
        return await speech_service.execute_transcript_query(
            request=req,
            user_id=user_id,
            memorial_profile_id=memorial_profile_id
        )
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==============================================================================
# 5. Speech Synthesis & Playback Endpoints
# ==============================================================================

@router.post("/synthesize", response_model=VoiceSynthesisResponse)
async def synthesize_speech_endpoint(req: VoiceSynthesisRequest):
    """Synthesize speech from an approved memorial response."""
    try:
        return await tts_service.synthesize_speech(
            request=req,
            guardian_status=GuardianDecision.PASS
        )
    except PermissionError as pe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/audio/{audio_id}")
async def get_audio_playback(audio_id: str):
    """Securely stream audio bytes for authenticated playback."""
    result = tts_service.get_audio_bytes(audio_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio asset '{audio_id}' not found or expired."
        )

    audio_bytes, mime_type, asset = result

    # Provenance and ethical disclosure response headers
    headers = {
        "X-Audio-Category": asset.audio_category.value,
        "X-Ethical-Disclosure": MANDATORY_MEMORIAL_DISCLOSURE.replace("—", "--"),
        "X-SHA256-Checksum": asset.sha256_checksum,
        "Cache-Control": "private, no-cache, no-store, must-revalidate",
        "Accept-Ranges": "bytes"
    }

    return Response(
        content=audio_bytes,
        media_type=mime_type,
        headers=headers
    )


@router.delete("/audio/{audio_id}", status_code=status.HTTP_200_OK)
async def delete_audio_endpoint(
    audio_id: str,
    user_id: str = "demo-user-001"
):
    """Delete an eligible temporary audio asset."""
    success = await tts_service.delete_audio(audio_id, actor=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio asset '{audio_id}' not found."
        )
    return {"message": f"Audio asset '{audio_id}' successfully deleted.", "audio_id": audio_id}


# ==============================================================================
# 6. Voice Profiles Endpoints
# ==============================================================================

@router.get("/profiles", response_model=List[VoiceProfile])
async def list_voice_profiles(
    memorial_profile_id: Optional[str] = None,
    user_id: Optional[str] = None
):
    """List accessible voice profiles for the current user."""
    return await voice_profile_service.list_profiles(
        memorial_profile_id=memorial_profile_id,
        user_id=user_id
    )


@router.post("/profiles", response_model=VoiceProfile, status_code=status.HTTP_201_CREATED)
async def create_voice_profile(
    profile_in: VoiceProfileCreate,
    user_id: str = "demo-user-001"
):
    """Register metadata for a voice profile."""
    return await voice_profile_service.create_profile(profile_in, actor=user_id)


@router.get("/profiles/{profile_id}", response_model=VoiceProfile)
async def get_voice_profile(profile_id: str):
    """Get metadata and consent status for a specific voice profile."""
    profile = await voice_profile_service.get_profile(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile '{profile_id}' not found."
        )
    return profile


@router.put("/profiles/{profile_id}", response_model=VoiceProfile)
async def update_voice_profile(
    profile_id: str,
    update_in: VoiceProfileUpdate,
    user_id: str = "demo-user-001"
):
    """Update voice profile metadata."""
    profile = await voice_profile_service.update_profile(profile_id, update_in, actor=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile '{profile_id}' not found."
        )
    return profile


@router.post("/profiles/{profile_id}/revoke", response_model=VoiceProfile)
async def revoke_voice_profile(
    profile_id: str,
    reason: str = Query("Guardian requested immediate voice profile revocation"),
    user_id: str = "demo-user-001"
):
    """Immediately revoke a voice profile, blocking all future synthesis."""
    profile = await voice_profile_service.revoke_profile(profile_id, reason=reason, actor=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile '{profile_id}' not found."
        )
    return profile


@router.post("/profiles/{profile_id}/disable", response_model=VoiceProfile)
async def disable_voice_profile(
    profile_id: str,
    user_id: str = "demo-user-001"
):
    """Disable a voice profile temporarily without full revocation."""
    profile = await voice_profile_service.disable_profile(profile_id, actor=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile '{profile_id}' not found."
        )
    return profile


# ==============================================================================
# 7. Consent Management Endpoints
# ==============================================================================

@router.get("/consent")
async def get_voice_consent_status(
    memorial_profile_id: str = "default-profile-001",
    user_id: str = "demo-user-001"
):
    """Check voice processing and custom voice synthesis consent status."""
    custom_check = await voice_consent_service.verify_synthesis_authorization(
        voice_type=VoiceType.AUTHORIZED_MEMORIAL_CUSTOM,
        memorial_profile_id=memorial_profile_id,
        user_id=user_id
    )
    generic_check = await voice_consent_service.verify_synthesis_authorization(
        voice_type=VoiceType.GENERIC_SYNTHETIC,
        memorial_profile_id=memorial_profile_id,
        user_id=user_id
    )

    return {
        "memorial_profile_id": memorial_profile_id,
        "custom_memorial_voice_permitted": custom_check["allowed"],
        "custom_voice_reason": custom_check["reason"],
        "generic_synthetic_voice_permitted": generic_check["allowed"],
        "generic_voice_reason": generic_check["reason"],
        "required_scopes": [
            "VOICE_PROCESSING",
            "AI_PROCESSING",
            "CUSTOM_VOICE_SYNTHESIS",
            "AUDIO_STORAGE",
            "FAMILY_ACCESS"
        ],
        "ethical_boundary": "Possession of oral history audio does not grant voice cloning rights."
    }


@router.post("/consent")
async def grant_voice_consent_endpoint(req: VoiceConsentRequest):
    """Grant formal consent authorization for voice operations."""
    record = await voice_consent_service.grant_voice_consent(
        granter_name=req.granter_name,
        granter_relationship=req.granter_relationship,
        consent_type=req.consent_type,
        memorial_profile_id=req.memorial_profile_id,
        scope=req.scope,
        document_reference=req.document_reference,
        notes=req.notes,
        actor=req.user_id
    )
    return record


@router.post("/consent/revoke")
async def revoke_voice_consent_endpoint(
    consent_id: Optional[str] = None,
    consent_type: ConsentType = ConsentType.CUSTOM_VOICE_SYNTHESIS,
    memorial_profile_id: str = "default-profile-001",
    user_id: str = "demo-user-001",
    reason: str = "Guardian revoked voice consent"
):
    """Revoke consent for voice processing or custom voice synthesis."""
    record = await voice_consent_service.revoke_voice_consent(
        consent_id=consent_id,
        consent_type=consent_type,
        memorial_profile_id=memorial_profile_id,
        actor=user_id,
        reason=reason
    )
    return {"message": "Voice consent revoked successfully.", "consent_record": record}


# ==============================================================================
# 8. Research Evaluation Metrics & Audit Endpoints
# ==============================================================================

@router.get("/metrics", response_model=VoiceMetrics)
async def get_voice_research_metrics():
    """Retrieve empirical research telemetry and latency benchmarks."""
    return speech_service.get_metrics()


@router.get("/audit")
async def get_voice_audit_logs(limit: int = 50):
    """Retrieve tamper-evident audit records for voice processing."""
    logs = await audit_service.list_logs(limit=limit)
    voice_logs = [
        l for l in logs
        if "VOICE" in str(l.action.value if hasattr(l.action, "value") else l.action)
        or "AUDIO" in str(l.action.value if hasattr(l.action, "value") else l.action)
        or "Speech" in l.resource
    ]
    return {
        "total_voice_audit_events": len(voice_logs),
        "events": voice_logs[:limit]
    }
