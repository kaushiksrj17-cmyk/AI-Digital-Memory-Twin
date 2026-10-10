"""Authentication API Endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional

from backend.app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_access_token,
    get_current_user as core_get_current_user,
    UserRole,
    ROLE_PERMISSIONS
)
from models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Authenticate memorial vault access with role assignment."""
    if credentials.email and len(credentials.password) >= 6:
        # Determine role from request, email heuristic, or default to vault_owner
        assigned_role = UserRole.VAULT_OWNER.value
        if credentials.role and credentials.role in [r.value for r in UserRole]:
            assigned_role = credentials.role
        elif "researcher" in credentials.email.lower():
            assigned_role = UserRole.RESEARCHER.value
        elif "family" in credentials.email.lower():
            assigned_role = UserRole.FAMILY_MEMBER.value
        elif "visitor" in credentials.email.lower():
            assigned_role = UserRole.VISITOR.value

        token_data = {
            "sub": credentials.email,
            "role": assigned_role,
            "user_id": f"usr-{abs(hash(credentials.email)) % 10000:04d}",
            "full_name": credentials.email.split("@")[0].replace(".", " ").title(),
        }
        token = create_access_token(token_data)

        return TokenResponse(
            access_token=token,
            user={
                "id": token_data["user_id"],
                "email": credentials.email,
                "full_name": token_data["full_name"],
                "role": assigned_role,
                "permissions": list(ROLE_PERMISSIONS.get(assigned_role, set())),
                "is_active": True
            }
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials. Use any valid email and minimum 6 character password for demo."
    )


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_profile(user: Dict[str, Any] = Depends(core_get_current_user)):
    """Retrieve authenticated memorial guardian or member profile."""
    role = user.get("role", UserRole.VAULT_OWNER.value)
    return {
        **user,
        "permissions": list(ROLE_PERMISSIONS.get(role, set()))
    }


@router.post("/verify")
async def verify_token_endpoint(token_req: Dict[str, str]):
    """Verify an access token and return token claims."""
    token = token_req.get("token", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid, expired, or corrupted."
        )
    return {
        "valid": True,
        "claims": payload
    }

