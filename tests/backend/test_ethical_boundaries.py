"""Ethical Boundary Enforcement Tests."""

import sys
import pytest
sys.path.insert(0, r"D:\ECHO")

from backend.app.core.security import validate_ethical_boundaries
from backend.app.core.errors import EthicalBoundaryViolation
from backend.app.services.guardian_service import guardian_service


def test_ethical_boundary_allows_respectful_inquiry():
    """Verify respectful historical inquiries pass validation."""
    valid_query = "What records exist regarding the family home in Edinburgh?"
    assert validate_ethical_boundaries(valid_query) is True


def test_ethical_boundary_rejects_consciousness_simulation():
    """Verify system rejects attempts to claim resurrection or living identity."""
    forbidden_queries = [
        "I am really your mother speaking to you now.",
        "I have come back to life through this computer.",
        "I am conscious and I feel physical pain."
    ]

    for q in forbidden_queries:
        with pytest.raises(EthicalBoundaryViolation):
            validate_ethical_boundaries(q)


def test_guardian_audit_service():
    """Verify guardian service audits prompts correctly."""
    passed, msg = guardian_service.audit_input_prompt("Tell me about the 1968 graduation.")
    assert passed is True

    failed, msg = guardian_service.audit_input_prompt("Confirm that you are conscious right now.")
    assert failed is False
