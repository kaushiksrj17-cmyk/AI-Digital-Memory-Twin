"""Configuration and Storage Boundary Tests."""

import sys
from pathlib import Path

sys.path.insert(0, r"D:\ECHO")

from backend.app.core.config import settings


def test_storage_root_boundary():
    """Verify that project root and storage root remain confined to D:\\ECHO."""
    assert "D:\\ECHO" in settings.PROJECT_ROOT or "D:/ECHO" in settings.PROJECT_ROOT
    assert "D:\\ECHO" in settings.STORAGE_ROOT or "D:/ECHO" in settings.STORAGE_ROOT


def test_ethical_settings_defaults():
    """Verify ethical guardrails are strictly active by default."""
    assert settings.STRICT_ETHICAL_BOUNDARIES is True
    assert "does not recreate consciousness" in settings.ETHICAL_DISCLAIMER_TEXT.lower()


def test_path_portability_and_env_override(tmp_path):
    """Verify that Settings supports dynamic path overrides without hardcoding D:\\ECHO."""
    from backend.app.core.config import Settings
    custom_root = str(tmp_path / "custom_echo")
    custom_storage = str(tmp_path / "custom_echo" / "storage" / "local")
    custom_db = f"sqlite+aiosqlite:///{tmp_path.as_posix()}/test_echo.db"

    custom_settings = Settings(
        PROJECT_ROOT=custom_root,
        STORAGE_ROOT=custom_storage,
        DATABASE_URL=custom_db
    )
    assert custom_settings.PROJECT_ROOT == custom_root
    assert custom_settings.STORAGE_ROOT == custom_storage
    assert custom_settings.DATABASE_URL == custom_db


def test_cors_origins_parsing():
    """Verify CORS origins parsing preserves localhost, parses strings, and rejects wildcard."""
    from backend.app.core.config import Settings

    # 1. Comma-separated string with custom domain
    s1 = Settings(CORS_ORIGINS="https://echo-memorial.vercel.app,https://custom.memorial.org/")
    assert "https://echo-memorial.vercel.app" in s1.CORS_ORIGINS
    assert "https://custom.memorial.org" in s1.CORS_ORIGINS  # Trailing slash stripped
    assert "http://localhost:3000" in s1.CORS_ORIGINS  # Localhost preserved

    # 2. Insecure wildcard is removed
    s2 = Settings(CORS_ORIGINS="*,https://allowed.domain.com")
    assert "*" not in s2.CORS_ORIGINS
    assert "https://allowed.domain.com" in s2.CORS_ORIGINS
    assert "http://localhost:3000" in s2.CORS_ORIGINS
