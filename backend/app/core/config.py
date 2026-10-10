"""Centralized Application Configuration.

Loads environment variables, enforces D:\\ECHO storage boundary,
and establishes ethical safeguards.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


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

    # Storage Root Bound to D:\ECHO
    PROJECT_ROOT: str = "D:\\ECHO"
    STORAGE_ROOT: str = "D:\\ECHO\\storage\\local"

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

    # Security & Tokens
    SECRET_KEY: str = Field(
        default="REPLACE_IN_PRODUCTION_SECURE_RANDOM_ECHO_TOKEN_KEY_MIN_32_CHARS",
        description="JWT signature secret key"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///D:/ECHO/storage/local/echo_dev.db"
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
        env_file="D:\\ECHO\\.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
