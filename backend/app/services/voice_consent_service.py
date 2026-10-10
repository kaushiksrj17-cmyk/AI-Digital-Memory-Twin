"""Voice Consent Verification and Ethical Authorization Service.

Integrates directly with ECHO's Phase 2 Consent Framework and Phase 5 Memory Guardian.
CRITICAL AUTHORIZATION RULES:
- Never clone or imitate an identifiable person's voice without explicit, documented
  authorization appropriate to that person and use case.
- Possession of an audio recording is NEVER proof of permission to clone the voice.
- Rechecks consent and authorization immediately before EVERY custom voice synthesis request.
- If consent is missing, pending, expired, or revoked, BLOCKS custom voice synthesis.
- Revocation must prevent future synthesis and record tamper-evident audit logs.
- Supports granular scopes:
  VOICE_PROCESSING, AI_PROCESSING, CUSTOM_VOICE_SYNTHESIS, AUDIO_STORAGE, FAMILY_ACCESS.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from uuid import uuid4

from models.enums import ConsentType, ConsentStatus, AuditAction, VoiceType, VoiceProfileStatus
from models.consent import ConsentRecord, ConsentRecordCreate
from backend.app.services.consent_service import consent_service
from backend.app.services.audit_service import audit_service


class VoiceConsentService:
    """Specialized ethical gatekeeper for oral history processing and voice cloning."""

    def __init__(self):
        self._consent_mgr = consent_service

    async def verify_synthesis_authorization(
        self,
        voice_type: VoiceType,
        voice_profile_id: Optional[str] = None,
        memorial_profile_id: str = "default-profile-001",
        user_id: str = "demo-user-001"
    ) -> Dict[str, Any]:
        """Perform immediate, non-bypassable pre-synthesis consent check.
        
        Returns:
            dict with 'allowed': bool, 'reason': str, 'voice_type': VoiceType, 'consent_id': Optional[str]
        """
        # 1. Base AI processing consent is required for any AI-generated response
        ai_allowed = await self._consent_mgr.is_ai_processing_permitted(memorial_profile_id)
        if not ai_allowed:
            await audit_service.record_event(
                action=AuditAction.VOICE_SYNTHESIS_BLOCKED,
                actor=user_id,
                resource=f"VoiceSynthesis:{memorial_profile_id}",
                result="BLOCKED",
                metadata={"reason": "AI_PROCESSING consent revoked or missing."}
            )
            return {
                "allowed": False,
                "reason": "AI processing consent is revoked or missing for this memorial archive.",
                "voice_type": voice_type,
                "consent_id": None
            }

        # 2. General Voice Processing consent
        all_consents = await self._consent_mgr.get_consent_records()
        
        # Check if voice processing is explicitly revoked
        if memorial_profile_id != "default-profile-001":
            voice_proc_records = [
                r for r in all_consents
                if r.consent_type == ConsentType.VOICE_PROCESSING
                and r.memorial_profile_id == memorial_profile_id
            ]
        else:
            voice_proc_records = [
                r for r in all_consents
                if r.consent_type == ConsentType.VOICE_PROCESSING
                and r.memorial_profile_id == "default-profile-001"
            ]

        if any(r.status == ConsentStatus.REVOKED for r in voice_proc_records):
            await audit_service.record_event(
                action=AuditAction.VOICE_SYNTHESIS_BLOCKED,
                actor=user_id,
                resource=f"VoiceSynthesis:{memorial_profile_id}",
                result="BLOCKED",
                metadata={"reason": "VOICE_PROCESSING consent explicitly revoked."}
            )
            return {
                "allowed": False,
                "reason": "Voice processing consent has been explicitly revoked by family guardian.",
                "voice_type": voice_type,
                "consent_id": None
            }

        # 3. If Custom Memorial Voice Clone requested, MUST have active CUSTOM_VOICE_SYNTHESIS consent
        if voice_type == VoiceType.AUTHORIZED_MEMORIAL_CUSTOM:
            if memorial_profile_id != "default-profile-001":
                custom_records = [
                    r for r in all_consents
                    if r.consent_type == ConsentType.CUSTOM_VOICE_SYNTHESIS
                    and r.memorial_profile_id == memorial_profile_id
                ]
            else:
                custom_records = [
                    r for r in all_consents
                    if r.consent_type == ConsentType.CUSTOM_VOICE_SYNTHESIS
                    and r.memorial_profile_id == "default-profile-001"
                ]

            # If any revoked, strictly block
            if any(r.status == ConsentStatus.REVOKED for r in custom_records):
                await audit_service.record_event(
                    action=AuditAction.VOICE_SYNTHESIS_BLOCKED,
                    actor=user_id,
                    resource=f"CustomVoiceClone:{voice_profile_id}",
                    result="BLOCKED",
                    metadata={"reason": "CUSTOM_VOICE_SYNTHESIS consent revoked."}
                )
                return {
                    "allowed": False,
                    "reason": "CUSTOM_VOICE_SYNTHESIS consent is revoked for this memorial archive. Custom cloning is prohibited.",
                    "voice_type": voice_type,
                    "consent_id": None,
                    "fallback_allowed": True
                }

            active_custom = [r for r in custom_records if r.status == ConsentStatus.GRANTED and r.revoked_at is None]
            if not active_custom:
                await audit_service.record_event(
                    action=AuditAction.VOICE_SYNTHESIS_BLOCKED,
                    actor=user_id,
                    resource=f"CustomVoiceClone:{voice_profile_id}",
                    result="BLOCKED",
                    metadata={"reason": "No active CUSTOM_VOICE_SYNTHESIS consent on record."}
                )
                return {
                    "allowed": False,
                    "reason": "Missing verified legal consent for CUSTOM_VOICE_SYNTHESIS. Possession of archival tapes does not grant cloning rights.",
                    "voice_type": voice_type,
                    "consent_id": None,
                    "fallback_allowed": True
                }

            return {
                "allowed": True,
                "reason": "Verified active CUSTOM_VOICE_SYNTHESIS legal consent.",
                "voice_type": VoiceType.AUTHORIZED_MEMORIAL_CUSTOM,
                "consent_id": active_custom[0].id
            }

        # 4. Generic synthetic voice fallback is allowed
        return {
            "allowed": True,
            "reason": "Generic synthetic voice permitted under standard memorial presentation terms.",
            "voice_type": VoiceType.GENERIC_SYNTHETIC,
            "consent_id": None
        }

    async def grant_voice_consent(
        self,
        granter_name: str,
        granter_relationship: str,
        consent_type: ConsentType,
        memorial_profile_id: str = "default-profile-001",
        scope: str = "MEMORIAL_VOICE_SYNTHESIS",
        document_reference: Optional[str] = None,
        notes: Optional[str] = None,
        actor: str = "demo-user-001"
    ) -> ConsentRecord:
        """Issue verified consent authorization for voice operations."""
        record_in = ConsentRecordCreate(
            memorial_profile_id=memorial_profile_id,
            user_id=actor,
            granter_name=granter_name,
            granter_relationship=granter_relationship,
            consent_type=consent_type,
            scope=scope,
            status=ConsentStatus.GRANTED,
            document_reference=document_reference or f"DOC-VOICE-{uuid4().hex[:8].upper()}",
            notes=notes
        )
        record = await self._consent_mgr.grant_consent(record_in, actor=actor)
        return record

    async def revoke_voice_consent(
        self,
        consent_id: Optional[str] = None,
        consent_type: Optional[ConsentType] = None,
        memorial_profile_id: str = "default-profile-001",
        actor: str = "demo-user-001",
        reason: Optional[str] = "Guardian requested voice synthesis revocation"
    ) -> Optional[ConsentRecord]:
        """Revoke active voice consent, immediately stopping all custom synthesis."""
        target_type = consent_type or ConsentType.CUSTOM_VOICE_SYNTHESIS
        record = await self._consent_mgr.revoke_consent(
            consent_id=consent_id,
            consent_type=target_type,
            actor=actor,
            reason=reason
        )
        return record


voice_consent_service = VoiceConsentService()
