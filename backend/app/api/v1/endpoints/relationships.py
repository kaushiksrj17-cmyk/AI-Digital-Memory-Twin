"""Relationships API Endpoints for ECHO.

Provides evidence-grounded social and kinship graph querying, edge CRUD,
verification, dispute resolution, and duplicate entity detection/merging.
"""

from fastapi import APIRouter, HTTPException, Query, status, Header
from typing import List, Optional, Dict, Any

from models.relationship import (
    RelationshipDetail,
    RelationshipEdgeCreate,
    RelationshipVerifyRequest,
    RelationshipDisputeRequest,
    DuplicateEntityCandidate,
    EntityMergeRequest,
    RelationshipGraphResponse,
    Relationship,
)
from models.enums import (
    GraphRelationshipType,
    GraphNodeType,
    VerificationStatus,
)
from backend.app.services.relationship_service import relationship_service

router = APIRouter()


@router.get("/", response_model=RelationshipGraphResponse)
async def get_relationship_graph(
    memorial_profile_id: str = "demo-profile-001",
    relationship_type: Optional[GraphRelationshipType] = None,
    verification_status: Optional[VerificationStatus] = None,
    entity_label: Optional[GraphNodeType] = None,
    search_query: Optional[str] = None,
):
    """Retrieve full interactive social and kinship graph with evidence and verification states."""
    return await relationship_service.get_graph(
        memorial_profile_id=memorial_profile_id,
        relationship_type=relationship_type,
        verification_status=verification_status,
        entity_label=entity_label,
        search_query=search_query,
    )


@router.get("/edges", response_model=List[RelationshipDetail])
async def list_relationship_edges(
    memorial_profile_id: str = "demo-profile-001",
    relationship_type: Optional[GraphRelationshipType] = None,
    verification_status: Optional[VerificationStatus] = None,
):
    """Retrieve list of evidence-grounded relationship edges for table fallback view."""
    graph_res = await relationship_service.get_graph(
        memorial_profile_id=memorial_profile_id,
        relationship_type=relationship_type,
        verification_status=verification_status,
    )
    return graph_res.edges


@router.get("/duplicates", response_model=List[DuplicateEntityCandidate])
async def get_duplicate_candidates(
    memorial_profile_id: str = "demo-profile-001",
):
    """Detect possible duplicate entity nodes using fuzzy token similarity."""
    return await relationship_service.detect_duplicate_entities(
        memorial_profile_id=memorial_profile_id
    )


@router.post("/merge-duplicates", response_model=Dict[str, Any])
async def merge_duplicate_entities(
    merge_req: EntityMergeRequest,
    x_user_id: str = Header(default="demo-user-001"),
    x_user_role: str = Header(default="FAMILY_ADMIN"),
):
    """Merge duplicate entity into canonical entity and re-route relationship edges (FAMILY_ADMIN or OWNER only)."""
    if x_user_role not in ["FAMILY_ADMIN", "OWNER", "vault_owner", "admin"]:
        raise HTTPException(status_code=403, detail="Merging entities requires FAMILY_ADMIN or OWNER clearance")
    
    return await relationship_service.merge_duplicate_entities(
        merge_req,
        actor_id=x_user_id,
        actor_role=x_user_role
    )


@router.get("/{edge_id}", response_model=RelationshipDetail)
async def get_relationship_edge(edge_id: str):
    """Retrieve details for a single relationship edge with archival evidence references."""
    edge = await relationship_service.get_relationship(edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Relationship edge not found")
    return edge


@router.post("/", response_model=RelationshipDetail, status_code=status.HTTP_201_CREATED)
async def create_relationship_edge(
    edge_in: RelationshipEdgeCreate,
    x_user_id: str = Header(default="demo-user-001"),
    x_user_role: str = Header(default="CONTRIBUTOR"),
):
    """Create a new evidence-grounded relationship edge."""
    return await relationship_service.create_relationship(
        edge_in,
        actor_id=x_user_id,
        actor_role=x_user_role
    )


@router.post("/{edge_id}/verify", response_model=RelationshipDetail)
async def verify_relationship_edge(
    edge_id: str,
    verify_req: RelationshipVerifyRequest,
    x_user_id: str = Header(default="demo-user-001"),
    x_user_role: str = Header(default="FAMILY_ADMIN"),
):
    """Officially verify or reject a relationship edge (FAMILY_ADMIN or OWNER only)."""
    if x_user_role not in ["FAMILY_ADMIN", "OWNER", "vault_owner", "admin"]:
        raise HTTPException(status_code=403, detail="Verification requires FAMILY_ADMIN or OWNER clearance")

    verified = await relationship_service.verify_relationship(
        edge_id,
        verify_req,
        actor_id=x_user_id,
        actor_role=x_user_role
    )
    if not verified:
        raise HTTPException(status_code=404, detail="Relationship edge not found")
    return verified


@router.post("/{edge_id}/dispute", response_model=RelationshipDetail)
async def dispute_relationship_edge(
    edge_id: str,
    dispute_req: RelationshipDisputeRequest,
    x_user_id: str = Header(default="demo-user-001"),
):
    """Register a dispute for a relationship while preserving both competing perspectives."""
    disputed = await relationship_service.dispute_relationship(
        edge_id,
        dispute_req,
        actor_id=x_user_id
    )
    if not disputed:
        raise HTTPException(status_code=404, detail="Relationship edge not found")
    return disputed
