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
