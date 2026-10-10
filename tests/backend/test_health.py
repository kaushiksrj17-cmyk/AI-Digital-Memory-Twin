"""Health Check Tests."""

import pytest
from fastapi.testclient import TestClient
import sys

# Ensure D:\ECHO is in sys.path
sys.path.insert(0, r"D:\ECHO")

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify /api/v1/health returns status 200, healthy status, and storage verification."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ECHO" in data["project"]
    assert "storage" in data
    assert "ethical_boundary" in data
    assert data["ethical_boundary"]["enforced"] is True
    assert data["ethical_boundary"]["recreation_of_consciousness_claimed"] is False
    assert "ai_providers" in data
    assert len(data["ai_providers"]) >= 6


def test_root_endpoint():
    """Verify root endpoint responds with API metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "ECHO" in data["project"]
    assert data["api_v1"] == "/api/v1"
