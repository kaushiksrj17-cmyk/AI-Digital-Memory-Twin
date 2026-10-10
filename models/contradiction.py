"""Contradiction Record Pydantic Models for ECHO.

Prepares foundation for contradiction detection across heterogeneous evidence.
Contradictions are explicitly recorded and tracked rather than silently resolved.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from models.enums import ContradictionStatus


class ContradictionRecord(BaseModel):
    """Structured record of conflicting evidence claims."""
    contradiction_id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = "default-profile-001"
    subject: str
    claim_a: str
    claim_b: str
    source_a: str
    source_b: str
    confidence_a: float = 1.0
    confidence_b: float = 1.0
    status: ContradictionStatus = ContradictionStatus.OPEN
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
