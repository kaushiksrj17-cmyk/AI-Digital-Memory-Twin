"""Audit Trail API Endpoints.

Provides tamper-evident historical audit logs for memory vault operations.
Access restricted to authorized Memorial Guardians and Vault Owners.
"""

from fastapi import APIRouter, Query, Depends
from typing import List, Optional, Dict, Any
from models.audit import AuditLog
from models.enums import AuditAction
from backend.app.services.audit_service import audit_service
from backend.app.core.security import require_permission, Permission

router = APIRouter()


@router.get("/", response_model=List[AuditLog])
async def list_audit_logs(
    resource: Optional[str] = None,
    action: Optional[AuditAction] = None,
    actor: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(require_permission(Permission.VIEW_AUDIT))
):
    """Retrieve filtered audit history. Requires VIEW_AUDIT clearance."""
    return await audit_service.list_logs(
        resource=resource,
        action=action,
        actor=actor,
        skip=skip,
        limit=limit
    )
