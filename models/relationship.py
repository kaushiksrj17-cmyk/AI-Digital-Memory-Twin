"""Relationship Domain Model for Phase 8 Evidence-Grounded Social & Kinship Graph.

Encapsulates:
- Evidence-grounded social and kinship connections
- Verification lifecycle (VERIFIED, PENDING_REVIEW, DISPUTED, REJECTED, UNKNOWN)
- Source evidence links and provenance status
- Duplicate entity detection and merge workflows
- Backward compatibility with Phase 1 Person-to-Person models
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4

from models.enums import (
    RelationshipType,
    GraphRelationshipType,
    GraphNodeType,
    ConfidenceLevel,
    ProvenanceStatus,
    VerificationStatus,
)


class RelationshipBase(BaseModel):
    person_a_id: str
    person_b_id: str
    relationship_type: RelationshipType
    description: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    closeness_rating: Optional[int] = Field(None, ge=1, le=5)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RelationshipCreate(RelationshipBase):
    memorial_profile_id: str


class Relationship(RelationshipBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Phase 8 Evidence-Grounded Graph Relationship Details
# ==============================================================================

class RelationshipDetail(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "demo-profile-001"
    source_entity_id: str
    source_entity_name: str
    source_entity_type: GraphNodeType = GraphNodeType.PERSON
    target_entity_id: str
    target_entity_name: str
    target_entity_type: GraphNodeType = GraphNodeType.PERSON
    relationship_type: GraphRelationshipType
    description: Optional[str] = None
    
    # Evidentiary Grounding
    source_evidence_ids: List[str] = Field(default_factory=list)
    source_memory_ids: List[str] = Field(default_factory=list)
    provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    confidence_score: float = 1.0
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    
    # Dispute Tracking
    is_disputed: bool = False
    dispute_notes: Optional[str] = None
    competing_evidence_ids: List[str] = Field(default_factory=list)
    
    # Authorship & Timestamps
    created_by: str = "demo-user-001"
    is_ai_suggested: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class RelationshipEdgeCreate(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relationship_type: GraphRelationshipType
    description: Optional[str] = None
    source_evidence_ids: List[str] = Field(default_factory=list)
    source_memory_ids: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    verification_status: VerificationStatus = VerificationStatus.PENDING_REVIEW


class RelationshipVerifyRequest(BaseModel):
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    notes: Optional[str] = None


class RelationshipDisputeRequest(BaseModel):
    dispute_reason: str = Field(..., description="Explanation of why this connection is contested")
    competing_evidence_id: Optional[str] = None
    notes: Optional[str] = None


class DuplicateEntityCandidate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    entity_a_id: str
    entity_a_name: str
    entity_a_label: GraphNodeType
    entity_b_id: str
    entity_b_name: str
    entity_b_label: GraphNodeType
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    detection_reason: str
    suggested_canonical_id: str
    status: str = Field(default="PENDING_REVIEW", description="PENDING_REVIEW, MERGED, DISMISSED")


class EntityMergeRequest(BaseModel):
    canonical_entity_id: str
    duplicate_entity_id: str
    merge_notes: Optional[str] = None


class RelationshipGraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[RelationshipDetail]
    total_nodes: int
    total_edges: int
    verified_edges_count: int
    disputed_edges_count: int
    pending_review_edges_count: int
    duplicate_candidates_count: int
