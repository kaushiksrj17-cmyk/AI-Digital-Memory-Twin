"""Security, Privacy, and Access Control API Endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from backend.app.core.config import settings
from backend.app.core.security import (
    can_access_privacy_level,
    has_permission,
    UserRole,
    Permission,
    ROLE_PERMISSIONS,
    get_current_user
)
from backend.app.services.audit_service import audit_service

router = APIRouter()


class AccessCheckRequest(BaseModel):
    role: str
    privacy_level: str
    action: Optional[str] = "READ"


class AccessCheckResponse(BaseModel):
    allowed: bool
    role: str
    privacy_level: str
    reason: str


@router.get("/status")
async def get_security_privacy_status() -> Dict[str, Any]:
    """Retrieve private vault encryption posture, storage isolation, and consent policies."""
    return {
        "storage_root": settings.STORAGE_ROOT,
        "is_local_isolated": True,
        "encryption_at_rest": "AES-256-GCM (Phase 2 Ready)",
        "zero_cloud_leakage": True,
        "consent_verification_active": True,
        "audit_logging_active": True,
        "ethical_boundary_enforced": settings.STRICT_ETHICAL_BOUNDARIES,
        "rbac_active": True,
        "supported_roles": [r.value for r in UserRole],
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }


@router.get("/roles")
async def get_roles_and_permissions() -> Dict[str, Any]:
    """Inspect all system roles and their assigned permissions."""
    return {
        "roles": {
            role: {
                "description": f"Role: {role}",
                "permissions": list(perms)
            }
            for role, perms in ROLE_PERMISSIONS.items()
        }
    }


@router.post("/check-access", response_model=AccessCheckResponse)
async def check_access_clearance(req: AccessCheckRequest) -> AccessCheckResponse:
    """Evaluate whether a given role has clearance to access a resource of a specific privacy tier."""
    is_allowed = can_access_privacy_level(req.role, req.privacy_level)
    reason = (
        f"Role '{req.role}' has clearance for privacy level '{req.privacy_level}'."
        if is_allowed
        else f"Role '{req.role}' lacks clearance for privacy level '{req.privacy_level}'."
    )
    return AccessCheckResponse(
        allowed=is_allowed,
        role=req.role,
        privacy_level=req.privacy_level,
        reason=reason
    )


@router.get("/audit-summary")
async def get_security_audit_summary() -> Dict[str, Any]:
    """Retrieve security audit summary, alert counts, and recent access attempts."""
    all_logs = await audit_service.list_logs(limit=200)
    alerts = [l for l in all_logs if getattr(l, "is_security_alert", False)]
    rejections = [l for l in all_logs if getattr(l, "result", "") == "REJECTED"]
    
    return {
        "total_audit_events": len(all_logs),
        "security_alerts_count": len(alerts),
        "rejections_count": len(rejections),
        "recent_alerts": [
            {
                "id": a.id,
                "action": a.action.value if hasattr(a.action, "value") else str(a.action),
                "actor": a.actor,
                "resource": a.resource,
                "timestamp": a.timestamp.isoformat() if hasattr(a.timestamp, "isoformat") else str(a.timestamp),
                "details": a.details
            }
            for a in alerts[:10]
        ]
    }

