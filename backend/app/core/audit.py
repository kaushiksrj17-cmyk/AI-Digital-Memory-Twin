"""Audit Logging Adapter for ECHO Core.

Provides a unified `audit_logger` interface used across RAG, Conversation,
and Guardian services, integrating directly with `AuditService`.
"""

from typing import Optional, Dict, Any
from models.enums import AuditAction
from backend.app.services.audit_service import audit_service
from backend.app.core.logging import logger


class AuditLogger:
    """Convenience adapter for logging conversational and security audit events."""

    def __init__(self):
        self.service = audit_service

    def log_event(
        self,
        user_id: Optional[str],
        action: AuditAction,
        target_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        resource: str = "ConversationEngine",
        result: str = "SUCCESS",
    ):
        """Synchronously dispatch or log an audit event."""
        metadata = dict(details or {})
        if target_id:
            metadata["target_id"] = target_id

        # Fire and log via internal logger and register into audit records
        logger.info(
            f"AUDIT_EVENT [{action.value}] actor={user_id} resource={resource} result={result} target={target_id}"
        )
        try:
            # We also record into the audit service's in-memory storage directly
            from models.audit import AuditLog
            from uuid import uuid4
            from datetime import datetime, timezone

            clean_meta = self.service._sanitize_metadata(metadata)
            rec = AuditLog(
                id=str(uuid4()),
                action=action,
                actor=user_id or "system",
                actor_user_id=user_id,
                resource=resource,
                result=result,
                timestamp=datetime.now(timezone.utc),
                metadata=clean_meta,
            )
            self.service._audit_records.append(rec)
        except Exception as e:
            logger.error(f"Failed to append audit record: {e}")


# Singleton instance
audit_logger = AuditLogger()
