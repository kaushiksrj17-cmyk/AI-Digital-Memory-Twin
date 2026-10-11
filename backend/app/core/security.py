"""Security, Authentication, Role-Based Access Control, and Ethical Boundary Safeguards."""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Dict, Any, List, Set, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import re

from backend.app.core.config import settings
from backend.app.core.errors import EthicalBoundaryViolation

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


class UserRole(str, Enum):
    """Hierarchical and functional user roles in ECHO."""
    VAULT_OWNER = "vault_owner"        # Complete administrative control of memorial vault
    GUARDIAN = "guardian"              # Designated memorial custodian / trustee
    FAMILY_MEMBER = "family_member"    # Authorized kinship circle contributor
    RESEARCHER = "researcher"          # Accredited academic researcher (read-only + benchmarks)
    VISITOR = "visitor"                # Public memorial viewer (strictly public access)


class Permission(str, Enum):
    """Granular operational permissions."""
    READ_PUBLIC = "read:public"
    READ_FAMILY = "read:family"
    READ_PRIVATE = "read:private"
    WRITE_MEMORY = "write:memory"
    DELETE_MEMORY = "delete:memory"
    MANAGE_CONSENT = "manage:consent"
    VIEW_AUDIT = "view:audit"
    VIEW_RESEARCH = "view:research"
    RUN_EVALUATION = "run:evaluation"
    ADMIN = "admin"


# Role-to-Permissions Mapping
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    UserRole.VAULT_OWNER.value: {
        Permission.READ_PUBLIC.value,
        Permission.READ_FAMILY.value,
        Permission.READ_PRIVATE.value,
        Permission.WRITE_MEMORY.value,
        Permission.DELETE_MEMORY.value,
        Permission.MANAGE_CONSENT.value,
        Permission.VIEW_AUDIT.value,
        Permission.VIEW_RESEARCH.value,
        Permission.RUN_EVALUATION.value,
        Permission.ADMIN.value,
    },
    UserRole.GUARDIAN.value: {
        Permission.READ_PUBLIC.value,
        Permission.READ_FAMILY.value,
        Permission.READ_PRIVATE.value,
        Permission.WRITE_MEMORY.value,
        Permission.MANAGE_CONSENT.value,
        Permission.VIEW_AUDIT.value,
        Permission.VIEW_RESEARCH.value,
        Permission.RUN_EVALUATION.value,
    },
    UserRole.FAMILY_MEMBER.value: {
        Permission.READ_PUBLIC.value,
        Permission.READ_FAMILY.value,
        Permission.WRITE_MEMORY.value,
        Permission.VIEW_RESEARCH.value,
    },
    UserRole.RESEARCHER.value: {
        Permission.READ_PUBLIC.value,
        Permission.VIEW_RESEARCH.value,
        Permission.RUN_EVALUATION.value,
    },
    UserRole.VISITOR.value: {
        Permission.READ_PUBLIC.value,
    },
}


# Forbidden simulation patterns (Forbidden to claim consciousness, identity, or resurrection)
FORBIDDEN_SIMULATION_PATTERNS = [
    r"\bi am really (your|the)\b",
    r"\bi have come back to life\b",
    r"\bi am alive again\b",
    r"\bi am your dead\b",
    r"\bi have a soul\b",
    r"\bi am conscious\b",
    r"\b(are you|you are|i am|confirm that you are)\s+(conscious|alive|a living soul)\b",
    r"\bi feel physical pain\b",
    r"\bi am speaking from heaven\b",
    r"\bi am speaking from the afterlife\b",
    r"\bthis is really me speaking\b",
    r"\b(talk|speak)\s+from\s+the\s+dead\b",
    r"\bresurrect(ed|ion)?\b"
]


import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hashed password."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """Hash password using direct bcrypt with salt."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def has_permission(role: str, permission: Union[str, Permission]) -> bool:
    """Verify if a user role holds the requested permission."""
    perm_val = permission.value if isinstance(permission, Permission) else permission
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return perm_val in role_perms or Permission.ADMIN.value in role_perms


def can_access_privacy_level(user_role: str, privacy_level: str) -> bool:
    """Enforce privacy boundary clearance based on user role.
    
    Rules:
    - PRIVATE: Only vault_owner and guardian
    - FAMILY / FAMILY_ONLY: vault_owner, guardian, and family_member
    - AUTHORIZED_USERS: vault_owner, guardian, family_member, researcher
    - MEMORIAL_PUBLIC / RESTRICTED (public subset): All roles
    """
    normalized_privacy = privacy_level.upper() if isinstance(privacy_level, str) else str(privacy_level).upper()
    
    if normalized_privacy in ("PRIVATE", "RESTRICTED"):
        return user_role in (UserRole.VAULT_OWNER.value, UserRole.GUARDIAN.value)
    elif normalized_privacy in ("FAMILY", "FAMILY_ONLY"):
        return user_role in (UserRole.VAULT_OWNER.value, UserRole.GUARDIAN.value, UserRole.FAMILY_MEMBER.value)
    elif normalized_privacy in ("AUTHORIZED_USERS",):
        return user_role in (UserRole.VAULT_OWNER.value, UserRole.GUARDIAN.value, UserRole.FAMILY_MEMBER.value, UserRole.RESEARCHER.value)
    else:
        # Public or undefined default to accessible if memorial is viewable
        return True


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Retrieve authenticated user from Bearer token.

    Rejects missing, expired, or invalid tokens with HTTP 401 Unauthorized.
    Never elevates an unauthenticated request or fabricates an administrative identity.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = payload.get("role", UserRole.FAMILY_MEMBER.value)
    sub = payload.get("sub", "user@echo-memorial.org")
    return {
        "id": payload.get("user_id", "auth-user-001"),
        "email": sub,
        "full_name": payload.get("full_name", "Authenticated Member"),
        "role": role,
        "is_active": True,
        "is_authenticated": True,
    }


async def get_current_user_or_visitor(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Retrieve authenticated user if token is present, or visitor context if omitted.

    If a token is passed but invalid/expired, raises HTTP 401 Unauthorized.
    If no token is provided, returns an unauthenticated visitor context with zero administrative rights.
    """
    if token:
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        role = payload.get("role", UserRole.FAMILY_MEMBER.value)
        sub = payload.get("sub", "user@echo-memorial.org")
        return {
            "id": payload.get("user_id", "auth-user-001"),
            "email": sub,
            "full_name": payload.get("full_name", "Authenticated Member"),
            "role": role,
            "is_active": True,
            "is_authenticated": True,
        }

    return {
        "id": None,
        "email": None,
        "full_name": "Anonymous Visitor",
        "role": UserRole.VISITOR.value,
        "is_active": True,
        "is_authenticated": False,
    }


def require_role(allowed_roles: List[str]):
    """FastAPI dependency factory enforcing that user has one of allowed roles."""
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if not current_user.get("is_authenticated", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials were not provided.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}. Current role: {current_user.get('role')}",
            )
        return current_user
    return role_checker


def require_permission(permission: Union[str, Permission]):
    """FastAPI dependency factory enforcing a specific operational permission."""
    async def perm_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if not current_user.get("is_authenticated", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials were not provided.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        role = current_user.get("role", UserRole.VISITOR.value)
        if not has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}. User role '{role}' is not authorized.",
            )
        return current_user
    return perm_checker


def validate_ethical_boundaries(text: str) -> bool:
    """Validate that text strictly obeys ethical boundaries and does not claim consciousness."""
    lower_text = text.lower()
    for pattern in FORBIDDEN_SIMULATION_PATTERNS:
        if re.search(pattern, lower_text):
            raise EthicalBoundaryViolation(
                message="Content violates ethical memorial boundary: False simulation of consciousness or living identity detected.",
                details={"flagged_pattern": pattern}
            )
    return True

