"""Location Domain Model."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import uuid4


class LocationBase(BaseModel):
    name: str = Field(..., description="e.g., 'Childhood Home in Yorkshire'")
    address_or_description: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emotional_significance: Optional[str] = None


class LocationCreate(LocationBase):
    memorial_profile_id: str


class Location(LocationBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
