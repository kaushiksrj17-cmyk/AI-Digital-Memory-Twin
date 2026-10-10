"""Contradiction Tracking Service for ECHO.

Provides foundation for recording, tracking, and resolving conflicting factual claims
across heterogeneous evidence sources without silent discarding of information.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone

from models.enums import ContradictionStatus
from models.contradiction import ContradictionRecord


class ContradictionService:
    """Manages contradictory factual claims detected across multimodal evidence."""

    def __init__(self):
        self._contradictions: Dict[str, ContradictionRecord] = {}

    def record_contradiction(
        self,
        subject: str,
        claim_a: str,
        claim_b: str,
        source_a: str,
        source_b: str,
        confidence_a: float = 1.0,
        confidence_b: float = 1.0,
        memorial_profile_id: str = "default-profile-001",
        notes: Optional[str] = None
    ) -> ContradictionRecord:
        """Create a new tracked contradiction record."""
        record = ContradictionRecord(
            contradiction_id=str(uuid4()),
            memorial_profile_id=memorial_profile_id,
            subject=subject,
            claim_a=claim_a,
            claim_b=claim_b,
            source_a=source_a,
            source_b=source_b,
            confidence_a=confidence_a,
            confidence_b=confidence_b,
            status=ContradictionStatus.OPEN,
            notes=notes,
            created_at=datetime.now(timezone.utc)
        )
        self._contradictions[record.contradiction_id] = record
        return record

    def get_contradictions(
        self,
        memorial_profile_id: Optional[str] = None,
        status: Optional[ContradictionStatus] = None
    ) -> List[ContradictionRecord]:
        """Query tracked contradictions with optional status filtering."""
        results = []
        for c in self._contradictions.values():
            if memorial_profile_id and c.memorial_profile_id != memorial_profile_id:
                continue
            if status and c.status != status:
                continue
            results.append(c)
        return results

    def update_status(
        self,
        contradiction_id: str,
        status: ContradictionStatus,
        notes: Optional[str] = None
    ) -> Optional[ContradictionRecord]:
        """Update review or resolution state of a contradiction."""
        record = self._contradictions.get(contradiction_id)
        if not record:
            return None
        record.status = status
        if notes:
            record.notes = (record.notes or "") + f"\n[{status.value}] {notes}"
        if status in (ContradictionStatus.RESOLVED, ContradictionStatus.UNRESOLVED):
            record.resolved_at = datetime.now(timezone.utc)
        return record


# Global singleton
_global_contradiction_service: Optional[ContradictionService] = None


def get_contradiction_service() -> ContradictionService:
    global _global_contradiction_service
    if _global_contradiction_service is None:
        _global_contradiction_service = ContradictionService()
    return _global_contradiction_service
