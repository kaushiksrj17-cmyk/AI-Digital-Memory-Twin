"""Conversation Session and Grounded Interaction Models.

Maintains ethical disclaimers, message history, evidence citations,
and safety audits on every memorial dialog exchange.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4
from models.enums import (
    ConfidenceLevel,
    SourceType,
    ProvenanceStatus,
    QuestionCategory,
    GuardianDecision,
    ClaimStatus,
    ConversationRole,
    RetrievalMode,
)
from models.provenance import ProvenanceRecord, GroundedClaim

ETHICAL_DISCLAIMER_TEXT = (
    "ECHO is an AI-generated memorial representation. "
    "It does not recreate consciousness, identity, or the actual person. "
    "All responses are grounded strictly in preserved archival evidence."
)


class QuestionClassification(BaseModel):
    """Categorization of a user inquiry for retrieval and safety routing."""
    category: QuestionCategory
    confidence: float = 1.0
    reason: str
    requires_archive: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResponseClaim(BaseModel):
    """Discrete factual claim extracted from generated text for evidentiary auditing."""
    claim_id: str = Field(default_factory=lambda: str(uuid4()))
    message_id: Optional[str] = None
    text: str
    subject: Optional[str] = None
    predicate: Optional[str] = None
    object: Optional[str] = None
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    confidence_score: float = 1.0
    status: ClaimStatus = ClaimStatus.SUPPORTED
    notes: Optional[str] = None


class ResponseSource(BaseModel):
    """Clickable, provenance-backed source citation for UI and audit logs."""
    source_id: str = Field(default_factory=lambda: str(uuid4()))
    source_title: str
    source_type: SourceType = SourceType.DOCUMENT
    memory_id: Optional[str] = None
    media_id: Optional[str] = None
    evidence_id: Optional[str] = None
    evidence_text: str
    provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    citation_label: str = "Based on preserved evidence"
    source_url: Optional[str] = None
    created_at: Optional[datetime] = None


class GuardianResult(BaseModel):
    """Audit outcome of Memory Guardian verification on a response."""
    result_id: str = Field(default_factory=lambda: str(uuid4()))
    message_id: Optional[str] = None
    guardian_status: GuardianDecision = GuardianDecision.PASS
    reason: str
    violations: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    missing_evidence: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    provenance: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    recommended_action: str = "DELIVER_RESPONSE"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageBase(BaseModel):
    role: str = Field(..., description="'user', 'assistant', 'system'")
    content: str = Field(..., description="Message text")
    ethical_disclaimer: str = Field(
        default=ETHICAL_DISCLAIMER_TEXT,
        description="Mandatory ethical boundary disclosure on all AI output"
    )
    confidence: ConfidenceLevel = Field(
        default=ConfidenceLevel.VERIFIED,
        description="Overall confidence rating of the response"
    )
    confidence_score: float = Field(
        default=1.0,
        description="Calculated confidence score between 0.0 and 1.0"
    )
    is_ai_generated: bool = Field(
        default=True,
        description="Explicit flag enforcing that AI output is never disguised as organic human communication"
    )
    guardian_status: GuardianDecision = Field(
        default=GuardianDecision.PASS,
        description="Verdict produced by Memory Guardian"
    )
    provenance_citations: List[ProvenanceRecord] = Field(
        default_factory=list,
        description="Preserved evidence sources backing claims in this response"
    )
    sources: List[ResponseSource] = Field(
        default_factory=list,
        description="Structured clickable source citations"
    )
    claims: List[ResponseClaim] = Field(
        default_factory=list,
        description="Detailed claim-by-claim grounding audit"
    )
    grounded_claims: List[GroundedClaim] = Field(
        default_factory=list,
        description="Detailed claim-by-claim grounding audit (legacy compatibility)"
    )
    contradictions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Conflicting evidence records detected for this response"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="User-facing evidentiary warnings or disclaimers"
    )
    contains_unsupported_claims: bool = Field(
        default=False,
        description="Flagged if any statement lacks preserved evidence"
    )
    retrieval_context_summary: Optional[str] = None


class Message(MessageBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def generated_by_ai(self) -> bool:
        return self.is_ai_generated


class ConversationSessionBase(BaseModel):
    memorial_profile_id: str
    user_id: str
    title: str = Field(default="Memorial Dialogue Session")
    topic_summary: Optional[str] = None
    ethical_boundary_acknowledged: bool = Field(
        default=True,
        description="User has explicitly acknowledged that ECHO does not possess consciousness"
    )


class ConversationSessionCreate(ConversationSessionBase):
    pass


class ConversationSession(ConversationSessionBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    messages: List[Message] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    @property
    def session_id(self) -> str:
        return self.id


class RAGQueryRequest(BaseModel):
    """Input payload for evidence-grounded RAG retrieval and generation."""
    query: str
    memorial_profile_id: str
    conversation_id: Optional[str] = None
    top_k: Optional[int] = 5
    retrieval_mode: Optional[RetrievalMode] = RetrievalMode.HYBRID
    confidence_threshold: Optional[float] = 0.5


class RAGQueryResponse(BaseModel):
    """Complete grounded answer and safety audit bundle."""
    conversation_id: Optional[str] = None
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    query: str
    answer: str
    confidence_level: ConfidenceLevel = ConfidenceLevel.VERIFIED
    confidence_score: float = 1.0
    guardian_status: GuardianDecision = GuardianDecision.PASS
    generated_by_ai: bool = True
    ethical_disclaimer: str = ETHICAL_DISCLAIMER_TEXT
    sources: List[ResponseSource] = Field(default_factory=list)
    claims: List[ResponseClaim] = Field(default_factory=list)
    contradictions: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    retrieval_explanation: Optional[str] = None
    question_classification: Optional[QuestionClassification] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
