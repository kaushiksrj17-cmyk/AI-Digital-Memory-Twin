"""Consent Record Domain Model.

Ensures strict ethical and legal compliance regarding memory rights,
likeness preservation, and family authorization.
Supports granular consent scopes: MEDIA_PROCESSING, AI_PROCESSING,
VOICE_PROCESSING, AVATAR_PROCESSING, FAMILY_ACCESS.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from models.enums import ConsentStatus, ConsentType


class ConsentRecordBase(BaseModel):
    granter_name: str = Field(..., description="Legal name of authorizing next-of-kin or subject")
    granter_relationship: str = Field(default="Guardian", description="Relationship to memorialized subject")
    consent_type: ConsentType = Field(
        default=ConsentType.MEDIA_PROCESSING,
        description="Specific scope: MEDIA_PROCESSING, AI_PROCESSING, VOICE_PROCESSING, AVATAR_PROCESSING, FAMILY_ACCESS"
    )
    scope: str = Field(default="STANDARD_ARCHIVE", description="Descriptive text scope")
    status: ConsentStatus = Field(default=ConsentStatus.GRANTED)
    document_reference: Optional[str] = Field(None, description="Signed document or digital authorization hash")
    notes: Optional[str] = None
    memory_id: Optional[str] = Field(None, description="Optional target memory ID")
    media_id: Optional[str] = Field(None, description="Optional target media ID")
    expires_at: Optional[datetime] = None


class ConsentRecordCreate(ConsentRecordBase):
    memorial_profile_id: str = Field(default="default-profile-001")
    user_id: Optional[str] = Field(default="demo-user-001")


class ConsentRecord(ConsentRecordBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    consent_id: Optional[str] = None
    memorial_profile_id: str = Field(default="default-profile-001")
    user_id: str = Field(default="demo-user-001")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    granted_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None

    def __init__(self, **data):
        super().__init__(**data)
        if not self.consent_id:
            self.consent_id = self.id

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
