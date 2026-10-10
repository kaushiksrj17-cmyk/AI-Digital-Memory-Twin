"""Life Event Domain Model for Chronological Timeline."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import uuid4
from models.enums import ConfidenceLevel


class LifeEventBase(BaseModel):
    title: str = Field(..., description="e.g., 'Graduated from Oxford', 'Wedding Day in Kyoto'")
    event_category: str = Field(..., description="Career, Education, Marriage, Milestone, Travel, Family")
    event_date: Optional[date] = None
    date_description: Optional[str] = Field(None, description="e.g., 'Early June 1982'")
    location_name: Optional[str] = None
    narrative: Optional[str] = None
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.VERIFIED)
    people_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)


class LifeEventCreate(LifeEventBase):
    memorial_profile_id: str


class LifeEvent(LifeEventBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)
