"""Media Asset Domain Model.

Extended for Phase 2 Secure Multimodal Memory Vault with:
- Checksum & Duplicate Reference Support
- Strict Relative Safe Storage & Thumbnail paths
- MIME & Processing lifecycle tracking
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from models.enums import SourceType, PrivacyLevel, ProcessingStatus


class MediaBase(BaseModel):
    file_name: str
    original_file_name: str
    media_type: SourceType = Field(default=SourceType.DOCUMENT)
    mime_type: str
    file_size_bytes: int
    relative_storage_path: str = Field(..., description="Safe relative path within D:\\ECHO\\storage, e.g. originals/...")
    thumbnail_path: Optional[str] = Field(None, description="Safe relative thumbnail path, e.g. thumbnails/...")
    description: Optional[str] = None
    captured_date: Optional[str] = None
    privacy_level: PrivacyLevel = Field(default=PrivacyLevel.PRIVATE)
    metadata_extracted: Dict[str, Any] = Field(default_factory=dict)
    sha256_checksum: Optional[str] = None
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.COMPLETED)
    
    # Duplicate Tracking
    is_duplicate: bool = Field(default=False)
    duplicate_of_media_id: Optional[str] = None
    duplicate_of_memory_id: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def sync_legacy_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "original_filename" in data and "original_file_name" not in data:
                data["original_file_name"] = data["original_filename"]
            if "storage_path" in data and "relative_storage_path" not in data:
                data["relative_storage_path"] = data["storage_path"]
            if "checksum" in data and "sha256_checksum" not in data:
                data["sha256_checksum"] = data["checksum"]
            if "file_size" in data and "file_size_bytes" not in data:
                data["file_size_bytes"] = data["file_size"]
        return data


class MediaCreate(MediaBase):
    memorial_profile_id: str = Field(default="default-profile-001")


class Media(MediaBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    memorial_profile_id: str = Field(default="default-profile-001")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by_user_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
