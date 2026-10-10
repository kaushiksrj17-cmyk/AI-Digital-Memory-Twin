"""Extracted Entity Model for ECHO Memorial Architecture.

Represents entities directly discovered or derived during multimodal processing.
Every extracted entity maintains evidentiary grounding without fabricating facts.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import EntityType, ProvenanceStatus, ConfidenceLevel


class EntityBase(BaseModel):
    entity_type: EntityType = Field(..., description="Entity classification")
    value: str = Field(..., description="Extracted entity string (e.g. 'Cambridge University', 'June 1968')")
    source_media_id: Optional[str] = None
    source_memory_id: Optional[str] = None
    provenance_status: ProvenanceStatus = Field(default=ProvenanceStatus.DIRECTLY_OBSERVED)
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.VERIFIED)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    extraction_method: str = Field(default="heuristic_ner", description="Method/model used for identification")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityCreate(EntityBase):
    pass


class Entity(EntityBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(from_attributes=True)
