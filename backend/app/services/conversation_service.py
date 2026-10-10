"""Conversation Service for ECHO.

Governs multi-turn memorial dialogue sessions, routes user questions through the
evidence-grounded RAG service, tracks conversation state, and preserves tamper-evident
audits and export packages.
"""

from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone

from models.conversation import (
    ConversationSession,
    ConversationSessionCreate,
    Message,
    ETHICAL_DISCLAIMER_TEXT,
    RAGQueryRequest,
    ResponseSource,
    ResponseClaim,
)
from models.enums import ConfidenceLevel, GuardianDecision, AuditAction
from backend.app.services.rag_service import RAGService, get_rag_service
from backend.app.core.audit import audit_logger


class ConversationService:
    """Manages conversational memorial dialogue sessions and message history."""

    def __init__(self, rag_service: Optional[RAGService] = None):
        self.rag_service = rag_service or get_rag_service()
        self._sessions: Dict[str, ConversationSession] = {}
        self._init_demo_session()

    def _init_demo_session(self):
        """Seed initial verified demonstration dialogue."""
        session = ConversationSession(
            id="demo-session-001",
            memorial_profile_id="demo-profile-001",
            user_id="demo-user-001",
            title="Reflections on Early University Years",
            topic_summary="Discussions centered around Cambridge studies and graduation",
            ethical_boundary_acknowledged=True,
            messages=[
                Message(
                    id="msg-001",
                    role="user",
                    content="Can you tell me about the graduation day in 1968?",
                    ethical_disclaimer=ETHICAL_DISCLAIMER_TEXT,
                    confidence=ConfidenceLevel.VERIFIED,
                    is_ai_generated=False,
                ),
                Message(
                    id="msg-002",
                    role="assistant",
                    content=(
                        "According to the preserved archival certificate and personal notes, "
                        "the master's degree ceremony occurred on June 22, 1968, in Cambridge. "
                        "The diploma was presented in the Wren Library courtyard, followed by family tea."
                    ),
                    ethical_disclaimer=ETHICAL_DISCLAIMER_TEXT,
                    confidence=ConfidenceLevel.VERIFIED,
                    confidence_score=1.0,
                    is_ai_generated=True,
                    guardian_status=GuardianDecision.PASS,
                    sources=[
                        ResponseSource(
                            source_id="src-grad-001",
                            source_title="University Degree Certificate 1968",
                            evidence_text="Degree of Master of Arts conferred June 22, 1968",
                            provenance_status="DIRECTLY_OBSERVED",
                            confidence=ConfidenceLevel.VERIFIED,
                            citation_label="Based on University Degree Certificate 1968"
                        )
                    ],
                    claims=[
                        ResponseClaim(
                            claim_id="clm-001",
                            text="the master's degree ceremony occurred on June 22, 1968, in Cambridge.",
                            subject="education",
                            confidence=ConfidenceLevel.VERIFIED,
                            confidence_score=1.0,
                            status="SUPPORTED"
                        )
                    ]
                )
            ]
        )
        self._sessions[session.id] = session

    async def list_sessions(self, profile_id: Optional[str] = None) -> List[ConversationSession]:
        """List active conversation sessions."""
        sessions = list(self._sessions.values())
        if profile_id:
            sessions = [s for s in sessions if s.memorial_profile_id == profile_id]
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)

    async def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Retrieve a specific session by ID."""
        return self._sessions.get(session_id)

    async def create_session(
        self,
        create_data: Optional[ConversationSessionCreate] = None,
        memorial_profile_id: Optional[str] = None,
        user_id: Optional[str] = None,
        title: Optional[str] = None,
    ) -> ConversationSession:
        """Create a new conversational memorial session."""
        prof_id = (create_data.memorial_profile_id if create_data else memorial_profile_id) or "default-profile-001"
        u_id = (create_data.user_id if create_data else user_id) or "default-user-001"
        s_title = (create_data.title if create_data and create_data.title else title) or "New Memorial Dialogue"
        topic = create_data.topic_summary if create_data else None
        acknowledged = create_data.ethical_boundary_acknowledged if create_data else True

        session = ConversationSession(
            id=str(uuid4()),
            memorial_profile_id=prof_id,
            user_id=u_id,
            title=s_title,
            topic_summary=topic,
            ethical_boundary_acknowledged=acknowledged,
            messages=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._sessions[session.id] = session

        audit_logger.log_event(
            user_id=session.user_id,
            action=AuditAction.CONVERSATION_CREATED,
            target_id=session.id,
            details={"title": session.title, "memorial_profile_id": session.memorial_profile_id}
        )
        return session

    async def post_message(
        self,
        session_id: str,
        content: str,
        user_id: str = "default-user-001",
        memorial_profile_id: Optional[str] = None,
    ) -> Message:
        """Post a user message, run evidence-grounded RAG, and record assistant turn."""
        session = self._sessions.get(session_id)
        if not session:
            # Auto-create session if missing
            session = ConversationSession(
                id=session_id,
                memorial_profile_id=memorial_profile_id or "default-profile-001",
                user_id=user_id,
                title="Active Memorial Session",
                messages=[],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self._sessions[session_id] = session

        # 1. Append User Message
        user_msg = Message(
            id=str(uuid4()),
            role="user",
            content=content,
            ethical_disclaimer=ETHICAL_DISCLAIMER_TEXT,
            confidence=ConfidenceLevel.VERIFIED,
            is_ai_generated=False,
            timestamp=datetime.now(timezone.utc),
        )
        session.messages.append(user_msg)
        session.updated_at = datetime.now(timezone.utc)

        audit_logger.log_event(
            user_id=user_id,
            action=AuditAction.MESSAGE_CREATED,
            target_id=user_msg.id,
            details={"session_id": session_id, "role": "user"}
        )

        # 2. Execute RAG Query Pipeline
        rag_req = RAGQueryRequest(
            query=content,
            memorial_profile_id=session.memorial_profile_id,
            conversation_id=session_id,
            top_k=5,
        )
        rag_resp = await self.rag_service.query(rag_req, user_id=user_id)

        # 3. Append Grounded Assistant Message
        assistant_msg = Message(
            id=rag_resp.message_id,
            role="assistant",
            content=rag_resp.answer,
            ethical_disclaimer=rag_resp.ethical_disclaimer,
            confidence=rag_resp.confidence_level,
            confidence_score=rag_resp.confidence_score,
            is_ai_generated=True,
            guardian_status=rag_resp.guardian_status,
            sources=rag_resp.sources,
            claims=rag_resp.claims,
            contradictions=rag_resp.contradictions,
            warnings=rag_resp.warnings,
            retrieval_context_summary=rag_resp.retrieval_explanation,
            timestamp=datetime.now(timezone.utc),
        )
        session.messages.append(assistant_msg)
        session.updated_at = datetime.now(timezone.utc)

        audit_logger.log_event(
            user_id=user_id,
            action=AuditAction.RESPONSE_GENERATED,
            target_id=assistant_msg.id,
            details={
                "session_id": session_id,
                "confidence": assistant_msg.confidence.value,
                "guardian_status": assistant_msg.guardian_status.value,
            }
        )

        return assistant_msg

    async def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export a complete session transcript with evidence citations and guardian audits."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session.id,
            "memorial_profile_id": session.memorial_profile_id,
            "title": session.title,
            "topic_summary": session.topic_summary,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": len(session.messages),
            "ethical_notice": ETHICAL_DISCLAIMER_TEXT,
            "metadata": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "system": "ECHO Memorial AI",
                "version": "1.0",
                "strict_evidence_enforced": True,
            },
            "transcript": [
                {
                    "message_id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "confidence": m.confidence.value,
                    "confidence_score": m.confidence_score,
                    "guardian_status": m.guardian_status.value if hasattr(m.guardian_status, "value") else str(m.guardian_status),
                    "is_ai_generated": m.is_ai_generated,
                    "sources": [s.model_dump() for s in m.sources],
                    "claims": [c.model_dump() for c in m.claims],
                    "contradictions": m.contradictions,
                    "warnings": m.warnings,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in session.messages
            ],
            "messages": [
                {
                    "message_id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "confidence": m.confidence.value,
                    "confidence_score": m.confidence_score,
                    "guardian_status": m.guardian_status.value if hasattr(m.guardian_status, "value") else str(m.guardian_status),
                    "is_ai_generated": m.is_ai_generated,
                    "sources": [s.model_dump() for s in m.sources],
                    "claims": [c.model_dump() for c in m.claims],
                    "contradictions": m.contradictions,
                    "warnings": m.warnings,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in session.messages
            ]
        }


conversation_service = ConversationService()


def get_conversation_service() -> ConversationService:
    return conversation_service
