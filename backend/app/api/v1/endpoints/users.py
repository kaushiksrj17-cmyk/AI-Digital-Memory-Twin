"""Users API Endpoints."""

from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_users():
    """List authorized family members and memorial trustees."""
    return [
        {
            "id": "demo-user-001",
            "email": "guardian@echo-memorial.org",
            "full_name": "Eleanor Vance",
            "role": "vault_owner",
            "is_active": True
        },
        {
            "id": "demo-user-002",
            "email": "thomas.vance@example.org",
            "full_name": "Thomas Vance",
            "role": "family_member",
            "is_active": True
        }
    ]
