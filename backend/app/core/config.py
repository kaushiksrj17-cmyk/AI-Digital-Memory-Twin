"""Centralized Application Configuration.

Loads environment variables, enforces D:\\ECHO storage boundary,
and establishes ethical safeguards.
"""

from typing import List, Optional, Any, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path
import os

# Detect repository root dynamically (4 levels up from backend/app/core/config.py)
_DETECTED_ROOT = Path(__file__).resolve().parents[3]
# Preserve D:\ECHO if it exists (local development on Windows), otherwise use detected root
_DEFAULT_PROJECT_ROOT = "D:\\ECHO" if Path("D:\\ECHO").exists() else str(_DETECTED_ROOT)
_DEFAULT_STORAGE_ROOT = str(Path(_DEFAULT_PROJECT_ROOT) / "storage" / "local")
_DEFAULT_DB_FILE = (Path(_DEFAULT_STORAGE_ROOT) / "echo_dev.db").as_posix()
_DEFAULT_DB_URL = f"sqlite+aiosqlite:///{_DEFAULT_DB_FILE}"


class Settings(BaseSettings):
    # Core Application
    PROJECT_NAME: str = "ECHO — AI Digital Memory Twin"
    TAGLINE: str = "Preserve the memories. Hear the voice. See the presence. Keep the story alive."
    RESEARCH_TITLE: str = (
        "Evidence-Grounded, Privacy-Preserving Multimodal AI for "
        "Interactive Digital Memory Preservation"
    )
    VERSION: str = "1.0.0-phase1.foundation"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Storage Root Bound to project boundary (defaults to D:\ECHO locally, /app in cloud)
    PROJECT_ROOT: str = _DEFAULT_PROJECT_ROOT
    STORAGE_ROOT: str = _DEFAULT_STORAGE_ROOT

    # Server Bind
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        default_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ]
        if isinstance(v, str):
            # Parse comma-separated list from environment variable
            origins = [item.strip().rstrip("/") for item in v.split(",") if item.strip()]
            # Reject wildcard when credentials are enabled
            origins = [o for o in origins if o != "*"]
            for d in default_origins:
                if d not in origins:
                    origins.append(d)
            return origins
        elif isinstance(v, (list, tuple, set)):
            origins = [str(item).strip().rstrip("/") for item in v if str(item).strip() and str(item) != "*"]
            for d in default_origins:
                if d not in origins:
                    origins.append(d)
            return origins
        return default_origins

    # Security & Tokens
    SECRET_KEY: str = Field(
        default="REPLACE_IN_PRODUCTION_SECURE_RANDOM_ECHO_TOKEN_KEY_MIN_32_CHARS",
        description="JWT signature secret key"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = _DEFAULT_DB_URL
    DATABASE_ECHO: bool = False

    # AI Providers Configuration
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-pro"

    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-004"

    STT_PROVIDER: str = "mock"
    STT_API_KEY: Optional[str] = None

    TTS_PROVIDER: str = "mock"
    TTS_API_KEY: Optional[str] = None

    CV_PROVIDER: str = "mock"
    CV_API_KEY: Optional[str] = None

    OCR_PROVIDER: str = "mock"
    OCR_API_KEY: Optional[str] = None

    # Ethical Safeguards
    STRICT_ETHICAL_BOUNDARIES: bool = True
    MINIMUM_CONFIDENCE_THRESHOLD: float = 0.75
    ALLOW_UNSUPPORTED_INFERENCES: bool = False
    ETHICAL_DISCLAIMER_TEXT: str = (
        "ECHO is an AI-generated memorial representation. "
        "It does not recreate consciousness, identity, or the actual person. "
        "All representations are grounded in preserved archival evidence."
    )

    model_config = SettingsConfigDict(
        env_file=(
            str(Path(_DEFAULT_PROJECT_ROOT) / ".env"),
            ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
