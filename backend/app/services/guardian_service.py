"""Memory Guardian Service for ECHO.

Bridges foundation stub methods to the full Phase 5 Memory Guardian implementation.
"""

from typing import Dict, Any, List, Tuple
from backend.app.core.security import validate_ethical_boundaries
from backend.app.core.errors import EthicalBoundaryViolation
from models.conversation import ETHICAL_DISCLAIMER_TEXT, GuardianResult, ResponseClaim
from backend.app.services.memory_guardian import MemoryGuardian, get_memory_guardian


class MemoryGuardianService:
    """Pre-generation and Post-generation safety filter."""

    def __init__(self):
        self.is_active = True
        self.phase = "Phase 5 Memory Guardian"
        self._guardian = get_memory_guardian()

    def audit_input_prompt(self, user_prompt: str) -> Tuple[bool, str]:
        """Audit incoming user prompts to prevent coercive simulations."""
        try:
            validate_ethical_boundaries(user_prompt)
            return True, "Passed ethical input check."
        except EthicalBoundaryViolation as e:
            return False, e.message

    def audit_output_text(self, generated_text: str) -> Tuple[bool, str]:
        """Verify generated AI text adheres strictly to memorial boundaries."""
        try:
            validate_ethical_boundaries(generated_text)
            return True, "Passed ethical output check."
        except EthicalBoundaryViolation as e:
            return False, e.message

    def validate_response(
        self,
        response_text: str,
        evidence_items: List[Dict[str, Any]],
        claims: List[ResponseClaim],
        privacy_authorized: bool = True,
        consent_authorized: bool = True,
        contradictions: List[Dict[str, Any]] = None,
        is_revision: bool = False,
    ) -> GuardianResult:
        """Run all 18 Phase 5 Guardian checks."""
        return self._guardian.validate_response(
            response_text=response_text,
            evidence_items=evidence_items,
            claims=claims,
            privacy_authorized=privacy_authorized,
            consent_authorized=consent_authorized,
            contradictions=contradictions,
            is_revision=is_revision,
        )

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": "Memory Guardian (Phase 5 Full Active Deployment)",
            "status": "active",
            "phase": self.phase,
            "disclaimer_enforced": True,
            "checks_enforced": 18,
            "standard_disclaimer": ETHICAL_DISCLAIMER_TEXT,
        }


guardian_service = MemoryGuardianService()
