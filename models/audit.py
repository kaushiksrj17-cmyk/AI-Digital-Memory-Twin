"""Audit Log Domain Model.

Records tamper-evident audit events for Memory Vault operations:
UPLOAD, VIEW, EDIT, DELETE, ARCHIVE, EXPORT, VERIFY, REJECT,
CONSENT_GRANTED, CONSENT_REVOKED, PRIVACY_CHANGED.
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from models.enums import AuditAction


class AuditLogBase(BaseModel):
    action: AuditAction
    actor: Optional[str] = Field(default="system", description="User ID or guardian identifier performing action")
    actor_user_id: Optional[str] = Field(None, description="Phase 1 alias for actor")
    resource: str = Field(default="Vault", description="Target resource or entity identifier")
    target_entity_type: Optional[str] = Field(None, description="e.g. Memory, Media, Consent")
    target_entity_id: Optional[str] = Field(None, description="Specific ID of target entity")
    result: str = Field(default="SUCCESS", description="Outcome: SUCCESS, FAILURE, BLOCKED, etc.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Safe contextual metadata (no secrets/passwords)")
    details: Optional[Dict[str, Any]] = Field(None, description="Phase 1 alias for metadata")
    ip_address: Optional[str] = None
    is_security_alert: bool = False

    @model_validator(mode='before')
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Sync actor <-> actor_user_id
            if not data.get("actor") and data.get("actor_user_id"):
                data["actor"] = data["actor_user_id"]
            elif not data.get("actor_user_id") and data.get("actor"):
                data["actor_user_id"] = data["actor"]
            # Sync metadata <-> details
            if not data.get("metadata") and data.get("details"):
                data["metadata"] = data["details"]
            elif not data.get("details") and data.get("metadata"):
                data["details"] = data["metadata"]
            # Sync resource
            if not data.get("resource") and data.get("target_entity_type"):
                ent_type = data.get("target_entity_type")
                ent_id = data.get("target_entity_id", "")
                data["resource"] = f"{ent_type}:{ent_id}" if ent_id else ent_type
        return data


class AuditLog(AuditLogBase):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
