"""Memorial Profile Model.

Represents the memorial identity being preserved.
CRITICAL ETHICAL NOTICE:
This profile represents an AI-generated memorial representation created from
authorized archival evidence. It NEVER claims to recreate consciousness, a soul,
or the actual living identity of the individual.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from uuid import uuid4


class MemorialProfileBase(BaseModel):
    subject_full_name: str = Field(..., description="Full legal or personal name of the memorialized person")
    preferred_name: Optional[str] = None
    biographical_overview: Optional[str] = Field(None, description="Curated evidence-grounded biography")
    birth_date: Optional[date] = None
    passing_date: Optional[date] = None
    birth_place: Optional[str] = None
    primary_language: str = "en"
    ethical_disclaimer_accepted: bool = Field(
        default=True,
        description="Acknowledged that ECHO does not recreate consciousness or identity"
    )
    is_active: bool = True


class MemorialProfileCreate(MemorialProfileBase):
    pass


class MemorialProfile(MemorialProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: str = Field(default_factory=lambda: str(uuid4()))
    owner_user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
