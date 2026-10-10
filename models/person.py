"""Person and Kinship Domain Models."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import uuid4


class PersonBase(BaseModel):
    full_name: str
    nickname: Optional[str] = None
    relationship_to_subject: str = Field(..., description="e.g., 'Mother', 'Daughter', 'Childhood Friend'")
    biographical_note: Optional[str] = None
    avatar_media_id: Optional[str] = None
    is_deceased: bool = False


class PersonCreate(PersonBase):
    memorial_profile_id: str


class Person(PersonBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
