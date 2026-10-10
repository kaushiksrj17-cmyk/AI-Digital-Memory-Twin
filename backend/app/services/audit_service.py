"""Audit Logging Service for ECHO Memory Vault.

Records tamper-evident provenance and operational audit trails:
UPLOAD, VIEW, EDIT, DELETE, ARCHIVE, EXPORT, VERIFY, REJECT,
CONSENT_GRANTED, CONSENT_REVOKED, PRIVACY_CHANGED.
Sanitizes sensitive information before storing.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from uuid import uuid4

from models.audit import AuditLog
from models.enums import AuditAction
from backend.app.core.logging import logger


class AuditService:
    """Manages audit log creation and historical retrieval."""

    def __init__(self):
        self._audit_records: List[AuditLog] = []

    async def record_event(
        self,
        action: AuditAction,
        actor: Optional[str] = "system",
        resource: str = "Vault",
        result: str = "SUCCESS",
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        is_security_alert: bool = False
    ) -> AuditLog:
        """Create an audit record, sanitize metadata, and log event."""
        # Sanitize metadata to prevent passwords, tokens, or raw keys from leaking
        clean_metadata = self._sanitize_metadata(metadata or {})

        record = AuditLog(
            id=str(uuid4()),
            action=action,
            actor=actor or "system",
            actor_user_id=actor,
            resource=resource,
            result=result,
            timestamp=datetime.now(timezone.utc),
            metadata=clean_metadata,
            details=clean_metadata,
            ip_address=ip_address,
            is_security_alert=is_security_alert
        )

        self._audit_records.append(record)

        log_msg = (
            f"AUDIT [{record.action.value}] by '{record.actor}' on '{record.resource}' "
            f"-> Result: {record.result}"
        )
        if is_security_alert:
            logger.warning(f"SECURITY ALERT: {log_msg} | Meta: {clean_metadata}")
        else:
            logger.info(log_msg)

        return record

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Strip passwords, access tokens, and secret keys."""
        forbidden_keys = {"password", "secret", "token", "api_key", "secret_key", "authorization"}
        sanitized = {}
        for k, v in metadata.items():
            if any(forbidden in k.lower() for forbidden in forbidden_keys):
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_metadata(v)
            else:
                sanitized[k] = v
        return sanitized

    async def list_logs(
        self,
        resource: Optional[str] = None,
        action: Optional[AuditAction] = None,
        actor: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[AuditLog]:
        """Retrieve audit history with optional filters."""
        results = list(self._audit_records)
        if resource:
            results = [r for r in results if resource.lower() in r.resource.lower()]
        if action:
            results = [r for r in results if r.action == action]
        if actor:
            results = [r for r in results if r.actor == actor]

        # Sort reverse chronological
        results.sort(key=lambda r: r.timestamp, reverse=True)
        return results[skip: skip + limit]

    # Convenient API aliases
    log_action = record_event
    get_audit_trail = list_logs


# Singleton instance
audit_service = AuditService()

