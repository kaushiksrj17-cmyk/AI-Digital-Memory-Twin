"""Retrieval and Vector Index Pydantic Models for ECHO.

Defines schemas for Evidence Chunks, Embeddings, Retrieval Queries, and Explainable Ranked Results.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from models.enums import (
    RetrievalMode,
    ConfidenceLevel,
    ProvenanceStatus,
    PrivacyLevel,
)


class EvidenceChunk(BaseModel):
    """A granular chunk of evidence text preserving full provenance and source mapping."""
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "default-profile-001"
    memory_id: Optional[str] = None
    media_id: Optional[str] = None
    evidence_id: Optional[str] = None
    chunk_index: int = 0
    text: str
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    source_reference: str = "Primary Archive"
    provenance: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    confidence_score: float = 1.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmbeddingRecord(BaseModel):
    """Metadata record for a vector stored in the vector index."""
    vector_id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "default-profile-001"
    memory_id: Optional[str] = None
    media_id: Optional[str] = None
    evidence_id: Optional[str] = None
    chunk_id: Optional[str] = None
    content_type: str = "TEXT"
    text: str
    source_reference: str = "Primary Archive"
    provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetrievalQuery(BaseModel):
    """Query parameters for semantic, keyword, graph, or hybrid evidence retrieval."""
    query: str
    memorial_profile_id: str = "default-profile-001"
    user_id: Optional[str] = "demo-user-001"
    top_k: int = 5
    retrieval_mode: RetrievalMode = RetrievalMode.HYBRID
    confidence_threshold: Optional[float] = None
    provenance_filter: Optional[List[ProvenanceStatus]] = None
    category_filter: Optional[List[str]] = None
    privacy_boundary: Optional[PrivacyLevel] = PrivacyLevel.PRIVATE


class RetrievalResultItem(BaseModel):
    """Individual ranked evidence item returned by the retrieval engine."""
    result_id: str = Field(default_factory=lambda: str(uuid4()))
    memory_id: Optional[str] = None
    media_id: Optional[str] = None
    evidence_id: Optional[str] = None
    chunk_id: Optional[str] = None
    text: str
    score: float
    score_components: Dict[str, float] = Field(default_factory=dict)
    score_breakdown: Dict[str, float] = Field(default_factory=dict)
    source_reference: str = "Primary Archive"
    provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED
    content_type: str = "EVIDENCE"
    retrieval_method: RetrievalMode = RetrievalMode.HYBRID
    why_retrieved: str = "Semantic similarity to user query"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RetrievalResponse(BaseModel):
    """Complete explainable retrieval response payload."""
    query_id: str = Field(default_factory=lambda: str(uuid4()))
    query: str
    retrieval_mode: RetrievalMode
    top_k: int
    candidate_count: int
    returned_count: int
    latency_ms: float
    results: List[RetrievalResultItem] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
