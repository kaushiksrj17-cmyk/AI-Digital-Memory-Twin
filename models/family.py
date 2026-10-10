"""Family Collaboration and Governance Domain Models for ECHO.

Encapsulates:
- 4-Tier Role-Based Access Control (OWNER, FAMILY_ADMIN, CONTRIBUTOR, VIEWER)
- Secure single-use invitation lifecycle with cryptographic hashing and expiry
- Memory contribution & verification lifecycle:
  DRAFT -> SUBMITTED -> UNDER_REVIEW -> APPROVED / NEEDS_CHANGES / REJECTED / DISPUTED / WITHDRAWN
- Strict prevention of unauthorized contributor self-approval
- Version history preservation
- Empirical Phase 8 research metrics and audit logging
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import (
    FamilyRole,
    InvitationStatus,
    ContributionStatus,
    ContributionType,
    ConfidenceLevel,
    ProvenanceStatus,
    VerificationStatus,
)


# ==============================================================================
# Family Workspace & Membership
# ==============================================================================

class FamilyWorkspace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(default="Vance Family Memorial Archive")
    memorial_profile_id: str = "demo-profile-001"
    owner_user_id: str = "demo-user-001"
    description: Optional[str] = "Collaborative archival workspace for authorized family custodians and contributors."
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    members_count: int = 1


class FamilyMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str = "workspace-001"
    user_id: str
    email: EmailStr
    full_name: str
    role: FamilyRole = FamilyRole.CONTRIBUTOR
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = Field(default="ACTIVE", description="ACTIVE, SUSPENDED, REMOVED")
    invited_by_user_id: Optional[str] = None
    relationship_to_subject: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FamilyMemberRoleUpdate(BaseModel):
    role: FamilyRole


# ==============================================================================
# Secure Single-Use Invitations
# ==============================================================================

class FamilyInvitationCreate(BaseModel):
    email: EmailStr
    role: FamilyRole = FamilyRole.CONTRIBUTOR
    relationship_to_subject: Optional[str] = Field(None, description="e.g. Granddaughter, Niece, Lifelong Colleague")
    expires_in_days: int = Field(default=7, ge=1, le=30)
    personal_note: Optional[str] = None


class FamilyInvitation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str = "workspace-001"
    email: EmailStr
    role: FamilyRole
    relationship_to_subject: Optional[str] = None
    token_hash: str = Field(..., description="Cryptographic SHA256 digest of secret invitation token")
    status: InvitationStatus = InvitationStatus.PENDING
    invited_by_user_id: str
    invited_by_name: str = "Memorial Guardian"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    accepted_by_user_id: Optional[str] = None
    revoked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FamilyInvitationResponse(BaseModel):
    id: str
    email: EmailStr
    role: FamilyRole
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
    invited_by_name: str
    invite_url: Optional[str] = Field(None, description="Only returned upon initial creation for safe sharing")


class FamilyInvitationAccept(BaseModel):
    invitation_token: str = Field(..., description="Plaintext single-use token provided in invitation link")


# ==============================================================================
# Memory Contribution & Verification Workflow
# ==============================================================================

class FamilyContributionBase(BaseModel):
    contribution_type: ContributionType
    title: str = Field(..., description="Descriptive summary of submission or correction")
    target_id: Optional[str] = Field(None, description="ID of existing memory/event/edge if updating")
    proposed_content: Dict[str, Any] = Field(..., description="Submitted fields, narratives, or metadata")
    original_content: Optional[Dict[str, Any]] = Field(None, description="Snapshot of existing state for diff display")
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Documents, photos or citations")
    contributor_notes: Optional[str] = Field(None, description="Explanation or personal recollections from contributor")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.SUPPORTED_INFERENCE)
    provenance: ProvenanceStatus = Field(default=ProvenanceStatus.USER_PROVIDED)
    is_ai_suggested: bool = Field(default=False)


class FamilyContributionCreate(FamilyContributionBase):
    pass


class ContributionReviewRequest(BaseModel):
    decision: ContributionStatus = Field(
        ...,
        description="APPROVED, NEEDS_CHANGES, REJECTED, or DISPUTED"
    )
    review_notes: str = Field(..., min_length=3, description="Evidentiary justification or editorial feedback")


class FamilyContribution(FamilyContributionBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str = "workspace-001"
    contributor_id: str
    contributor_name: str
    contributor_email: EmailStr
    status: ContributionStatus = ContributionStatus.SUBMITTED
    version: int = 1
    
    # Review record
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    review_decision: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Version audit history
    version_history: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Empirical Phase 8 Research Metrics
# ==============================================================================

class Phase8Metrics(BaseModel):
    timeline_retrieval_latency_ms: float = 0.0
    events_with_supporting_evidence_count: int = 0
    events_awaiting_review_count: int = 0
    disputed_events_count: int = 0
    disputed_relationships_count: int = 0
    relationship_evidence_coverage_pct: float = 0.0
    contribution_approval_count: int = 0
    contribution_rejection_count: int = 0
    review_turnaround_time_hours_avg: float = 0.0
    unauthorized_access_attempts_count: int = 0
    duplicate_entity_suggestions_count: int = 0
    contradiction_detection_count: int = 0
    active_family_members_count: int = 0
    pending_invitations_count: int = 0
    total_contributions_count: int = 0
    measured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
