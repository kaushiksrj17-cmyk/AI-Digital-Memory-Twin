"""Family Collaboration API Endpoints for ECHO.

Provides workspace governance, 4-tier RBAC, single-use invitation lifecycle,
contribution and verification review queue, and empirical Phase 8 research metrics.
"""

from fastapi import APIRouter, HTTPException, Query, status, Header
from typing import List, Optional, Dict, Any

from models.family import (
    FamilyWorkspace,
    FamilyMember,
    FamilyMemberRoleUpdate,
    FamilyInvitation,
    FamilyInvitationCreate,
    FamilyInvitationResponse,
    FamilyInvitationAccept,
    FamilyContribution,
    FamilyContributionCreate,
    ContributionReviewRequest,
    Phase8Metrics,
)
from models.enums import (
    FamilyRole,
    ContributionStatus,
    ContributionType,
)
from backend.app.services.family_service import (
    family_service,
    UnauthorizedFamilyActionError,
    SelfApprovalViolationError,
)

router = APIRouter()


# ==============================================================================
# Workspace & Member Governance
# ==============================================================================

@router.get("/workspace", response_model=Dict[str, Any])
async def get_workspace(
    x_user_id: str = Header(default="demo-user-001"),
):
    """Retrieve family collaboration workspace summary and caller's active role."""
    return await family_service.get_workspace(user_id=x_user_id)


@router.get("/members", response_model=List[FamilyMember])
async def list_family_members(
    x_user_id: str = Header(default="demo-user-001"),
):
    """List active members in the family memorial workspace."""
    try:
        return await family_service.list_members(user_id=x_user_id)
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))


@router.put("/members/{member_id}/role", response_model=FamilyMember)
async def update_member_role(
    member_id: str,
    role_in: FamilyMemberRoleUpdate,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Modify role permissions for a family member (Strictly OWNER only)."""
    try:
        return await family_service.update_member_role(
            target_member_id=member_id,
            role_in=role_in,
            actor_user_id=x_user_id
        )
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.delete("/members/{member_id}")
async def remove_family_member(
    member_id: str,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Remove a member from the workspace (OWNER or FAMILY_ADMIN)."""
    try:
        removed = await family_service.remove_member(
            target_member_id=member_id,
            actor_user_id=x_user_id
        )
        if not removed:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"status": "success", "message": f"Member {member_id} removed"}
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))


# ==============================================================================
# Single-Use Invitation Lifecycle
# ==============================================================================

@router.get("/invitations", response_model=List[FamilyInvitation])
async def list_invitations(
    x_user_id: str = Header(default="demo-user-001"),
):
    """List pending and historical family invitations (OWNER or FAMILY_ADMIN only)."""
    try:
        return await family_service.list_invitations(actor_user_id=x_user_id)
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))


@router.post("/invitations", response_model=FamilyInvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invite_in: FamilyInvitationCreate,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Generate a single-use cryptographically hashed invitation token (OWNER or FAMILY_ADMIN only)."""
    try:
        return await family_service.create_invitation(
            invite_in=invite_in,
            actor_user_id=x_user_id
        )
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.delete("/invitations/{invitation_id}")
async def revoke_invitation(
    invitation_id: str,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Revoke a pending family invitation prior to use."""
    try:
        revoked = await family_service.revoke_invitation(
            invitation_id=invitation_id,
            actor_user_id=x_user_id
        )
        if not revoked:
            raise HTTPException(status_code=404, detail="Pending invitation not found")
        return {"status": "success", "message": f"Invitation {invitation_id} revoked"}
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))


@router.post("/invitations/accept", response_model=FamilyMember)
async def accept_invitation(
    accept_in: FamilyInvitationAccept,
    x_user_id: str = Header(default="new-user-001"),
    x_user_email: str = Header(default="invitee@echo-memorial.org"),
    x_user_name: str = Header(default="Invited Relative"),
):
    """Claim and activate a single-use invitation token."""
    try:
        return await family_service.accept_invitation(
            accept_in=accept_in,
            authenticated_user_id=x_user_id,
            authenticated_user_email=x_user_email,
            authenticated_user_name=x_user_name
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


# ==============================================================================
# Memory Contribution & Verification Review Queue
# ==============================================================================

@router.get("/contributions", response_model=List[FamilyContribution])
async def list_contributions(
    status: Optional[ContributionStatus] = None,
    contribution_type: Optional[ContributionType] = None,
    x_user_id: str = Header(default="demo-user-001"),
):
    """List memory contributions in the review queue."""
    try:
        return await family_service.list_contributions(
            status=status,
            contribution_type=contribution_type,
            actor_user_id=x_user_id
        )
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))


@router.get("/contributions/{contribution_id}", response_model=FamilyContribution)
async def get_contribution(
    contribution_id: str,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Retrieve contribution detail with diffs and complete version history."""
    try:
        contrib = await family_service.get_contribution(
            contribution_id=contribution_id,
            actor_user_id=x_user_id
        )
        if not contrib:
            raise HTTPException(status_code=404, detail="Contribution not found")
        return contrib
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))


@router.post("/contributions", response_model=FamilyContribution, status_code=status.HTTP_201_CREATED)
async def submit_contribution(
    contrib_in: FamilyContributionCreate,
    x_user_id: str = Header(default="demo-user-003"),
):
    """Submit a proposed memory, correction, or document for family review (CONTRIBUTOR+)."""
    try:
        return await family_service.submit_contribution(
            contrib_in=contrib_in,
            actor_user_id=x_user_id
        )
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))


@router.post("/contributions/{contribution_id}/review", response_model=FamilyContribution)
async def review_contribution(
    contribution_id: str,
    review_in: ContributionReviewRequest,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Approve, reject, dispute, or request changes on a contribution.
    
    Self-approval by the original contributor is strictly blocked.
    """
    try:
        return await family_service.review_contribution(
            contribution_id=contribution_id,
            review_in=review_in,
            actor_user_id=x_user_id
        )
    except SelfApprovalViolationError as se:
        raise HTTPException(status_code=403, detail=str(se))
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


@router.post("/contributions/{contribution_id}/withdraw", response_model=FamilyContribution)
async def withdraw_contribution(
    contribution_id: str,
    x_user_id: str = Header(default="demo-user-003"),
):
    """Retract a contribution before it is committed (Contributor only)."""
    try:
        return await family_service.withdraw_contribution(
            contribution_id=contribution_id,
            actor_user_id=x_user_id
        )
    except UnauthorizedFamilyActionError as ue:
        raise HTTPException(status_code=403, detail=str(ue))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))


# ==============================================================================
# Research Telemetry Metrics
# ==============================================================================

@router.get("/metrics", response_model=Phase8Metrics)
async def get_phase8_metrics(
    x_user_id: str = Header(default="demo-user-001"),
):
    """Retrieve empirical research telemetry metrics for Phase 8."""
    return await family_service.get_metrics()
