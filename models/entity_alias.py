"""Entity Alias Model for Conservative Entity Resolution in ECHO.

Prevents duplicate entity nodes while strictly prohibiting silent merges.
Potential matches with ambiguity are marked as unconfirmed.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class EntityAlias(BaseModel):
    """An alias mapping for an entity without destructive data merging."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "default-profile-001"
    canonical_entity_id: str
    canonical_name: str
    alias_name: str
    entity_type: str = "PERSON"
    similarity_score: float = 1.0
    is_confirmed: bool = False
    is_possible_duplicate: bool = True
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
