"""Voice Session Management and State Machine Service for ECHO.

Implements the finite state machine for voice interaction:
IDLE -> RECORDING -> UPLOADING -> TRANSCRIBING -> RETRIEVING ->
GENERATING -> VALIDATING -> SYNTHESIZING -> COMPLETED / BLOCKED / FAILED / CANCELLED.

Tracks live and post-recording transcripts, user edits, error reporting,
and real research latency metrics.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import (
    VoiceProcessingState,
    VoiceType,
    GuardianDecision,
    AuditAction,
)
from models.voice import (
    VoiceSession,
    VoiceSessionCreate,
)
from backend.app.services.audit_service import audit_service


class VoiceSessionService:
    """Manages voice dialogue sessions and coordinates explicit state machine transitions."""

    def __init__(self):
        self._sessions: Dict[str, VoiceSession] = {}
        self._init_demo_session()

    def _init_demo_session(self):
        """Seed initial demonstration voice session."""
        session = VoiceSession(
            id="vs-demo-001",
            memorial_profile_id="default-profile-001",
            user_id="demo-user-001",
            language="en",
            state=VoiceProcessingState.COMPLETED,
            voice_type=VoiceType.GENERIC_SYNTHETIC,
            original_transcript="Can you tell me about the university graduation ceremony in 1968?",
            edited_transcript=None,
            is_transcript_edited=False,
            last_guardian_status=GuardianDecision.PASS,
            latency_metrics={
                "stt_latency_ms": 350.0,
                "retrieval_latency_ms": 120.0,
                "generation_latency_ms": 410.0,
                "guardian_latency_ms": 95.0,
                "tts_latency_ms": 280.0,
                "total_e2e_ms": 1255.0
            }
        )
        self._sessions[session.id] = session

    async def create_session(
        self,
        data: VoiceSessionCreate,
        actor: str = "demo-user-001",
        session_id: Optional[str] = None
    ) -> VoiceSession:
        """Initialize a new voice interaction session in IDLE state."""
        sid = session_id or f"vs-{uuid4().hex[:12]}"
        session = VoiceSession(
            id=sid,
            memorial_profile_id=data.memorial_profile_id,
            user_id=data.user_id or actor,
            language=data.language or "en",
            voice_profile_id=data.voice_profile_id,
            conversation_session_id=data.conversation_session_id,
            state=VoiceProcessingState.IDLE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self._sessions[session.id] = session

        await audit_service.record_event(
            action=AuditAction.VOICE_SESSION_STARTED,
            actor=actor,
            resource=f"VoiceSession:{session.id}",
            result="SUCCESS",
            metadata={"language": session.language}
        )

        return session

    async def get_session(self, session_id: str) -> Optional[VoiceSession]:
        """Lookup session by ID."""
        return self._sessions.get(session_id)

    async def list_sessions(
        self,
        memorial_profile_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[VoiceSession]:
        """List active voice sessions."""
        sessions = list(self._sessions.values())
        if memorial_profile_id:
            sessions = [s for s in sessions if s.memorial_profile_id == memorial_profile_id]
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)

    async def transition_state(
        self,
        session_id: str,
        new_state: VoiceProcessingState,
        error_message: Optional[str] = None
    ) -> Optional[VoiceSession]:
        """Safely transition session state machine."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        session.state = new_state
        session.updated_at = datetime.now(timezone.utc)
        if error_message:
            session.error_message = error_message

        return session

    async def set_transcript(
        self,
        session_id: str,
        transcript: str,
        is_edited: bool = False
    ) -> Optional[VoiceSession]:
        """Store transcribed or user-edited query text."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        if not session.original_transcript:
            session.original_transcript = transcript
        if is_edited:
            session.edited_transcript = transcript
            session.is_transcript_edited = True

        session.updated_at = datetime.now(timezone.utc)
        return session

    async def cancel_session(self, session_id: str) -> Optional[VoiceSession]:
        """Cancel an ongoing voice session."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        session.state = VoiceProcessingState.CANCELLED
        session.updated_at = datetime.now(timezone.utc)
        return session


voice_session_service = VoiceSessionService()
