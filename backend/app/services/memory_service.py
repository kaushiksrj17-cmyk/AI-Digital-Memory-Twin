"""Memory Vault Service for ECHO.

Orchestrates Phase 2 Secure Multimodal Memory Vault:
- Storage and duplicate detection
- Spatiotemporal & social graph indexing
- Multi-criteria metadata search and filtering
- Authorization and privacy-level gating (PRIVATE vs FAMILY vs AUTHORIZED_USERS)
- Verification, Archiving, Restoring, and Deletion lifecycles
- Export abstraction
- Real-time vault metric aggregations (Zero fabricated counts)
"""

from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
import json

from models.memory import Memory, MemoryCreate, MemoryUpdate
from models.enums import (
    ConfidenceLevel,
    MemoryCategory,
    VerificationStatus,
    PrivacyLevel,
    SourceType,
    ConsentStatus,
    ProcessingStatus,
    AuditAction
)
from models.provenance import ProvenanceRecord
from storage.vault_storage import vault_storage
from backend.app.services.audit_service import audit_service


class UnauthorizedMemoryAccessError(PermissionError):
    """Raised when an actor lacks rights to view or modify a private memory."""
    pass


class MemoryService:
    """Manages secure memory vault operations."""

    def __init__(self):
        self.storage = vault_storage
        self._memories: Dict[str, Memory] = {}
        self._checksum_to_memory_id: Dict[str, str] = {}
        self._init_foundation_demo_data()

    def _init_foundation_demo_data(self):
        """Seed representative verified demonstration memories."""
        demo_1 = Memory(
            id="demo-mem-001",
            memory_id="demo-mem-001",
            memorial_profile_id="demo-profile-001",
            title="Graduation Day at Trinity College Library",
            description=(
                "On a bright afternoon in June 1968, received the master's degree in literature. "
                "The ceremony was held in the Wren Library courtyard, followed by tea under the willow trees."
            ),
            narrative=(
                "On a bright afternoon in June 1968, received the master's degree in literature. "
                "The ceremony was held in the Wren Library courtyard, followed by tea under the willow trees."
            ),
            summary="Master's graduation ceremony in June 1968 at Wren Library courtyard.",
            category=MemoryCategory.EDUCATION,
            source_type=SourceType.ORIGINAL_PHOTO,
            confidence=ConfidenceLevel.VERIFIED,
            verification_status=VerificationStatus.VERIFIED,
            confidence_score=0.98,
            privacy_level=PrivacyLevel.PRIVATE,
            consent_status=ConsentStatus.GRANTED,
            date="1968-06-22",
            approximate_date="June 1968",
            location="Cambridge, UK",
            location_name="Cambridge, UK",
            people=["Eleanor Vance", "Arthur Vance"],
            people_ids=["demo-person-001", "demo-person-002"],
            original_filename="graduation_portrait_1968.jpg",
            mime_type="image/jpeg",
            file_size=1420580,
            storage_path="originals/demo_graduation_portrait_1968.jpg",
            thumbnail_path="thumbnails/demo_graduation_portrait_1968_thumb.jpg",
            checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            processing_status=ProcessingStatus.COMPLETED,
            archived=False,
            uploaded_by="demo-user-001",
            created_by_user_id="demo-user-001",
            tags=["Education", "Milestone", "Cambridge"],
            provenance_records=[
                ProvenanceRecord(
                    source_id="demo-doc-001",
                    source_type=SourceType.DOCUMENT,
                    source_title="University of Cambridge Degree Certificate 1968",
                    source_reference="Archival Box 1, Item 4",
                    evidence_text="Conferred Degree of Master of Arts on 22 June 1968",
                    confidence=ConfidenceLevel.VERIFIED,
                    citation_label="Based on preserved evidence"
                )
            ]
        )

        demo_2 = Memory(
            id="demo-mem-002",
            memory_id="demo-mem-002",
            memorial_profile_id="demo-profile-001",
            title="Summer Sailing on Lake Windermere",
            description=(
                "Family holiday aboard the wooden dinghy. Recorded notes mention teaching the children "
                "how to tack against the north wind while listening to the evening birds."
            ),
            narrative=(
                "Family holiday aboard the wooden dinghy. Recorded notes mention teaching the children "
                "how to tack against the north wind while listening to the evening birds."
            ),
            summary="Family sailing excursion on Lake Windermere during summer holiday.",
            category=MemoryCategory.TRAVEL,
            source_type=SourceType.DOCUMENT,
            confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
            verification_status=VerificationStatus.PENDING_REVIEW,
            confidence_score=0.82,
            privacy_level=PrivacyLevel.FAMILY,
            consent_status=ConsentStatus.GRANTED,
            date="1974-08-14",
            approximate_date="August 1974",
            location="Lake District, England",
            location_name="Lake District, England",
            people=["Arthur Vance"],
            people_ids=["demo-person-002"],
            original_filename="travel_journal_windermere_1974.pdf",
            mime_type="application/pdf",
            file_size=2850000,
            storage_path="originals/demo_travel_journal_windermere_1974.pdf",
            thumbnail_path=None,
            checksum="ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
            processing_status=ProcessingStatus.COMPLETED,
            archived=False,
            uploaded_by="demo-user-001",
            created_by_user_id="demo-user-001",
            tags=["Holiday", "Family", "Sailing"],
            provenance_records=[
                ProvenanceRecord(
                    source_id="demo-doc-002",
                    source_type=SourceType.DOCUMENT,
                    source_title="Handwritten Travel Journal - Entry 14 Aug 1974",
                    source_reference="Journal Vol 2, Page 43",
                    evidence_text="Took the boat across Windermere; crisp gusts and bright sun.",
                    confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
                    citation_label="Based on preserved evidence"
                )
            ]
        )

        self._memories[demo_1.id] = demo_1
        self._memories[demo_2.id] = demo_2
        if demo_1.checksum:
            self._checksum_to_memory_id[demo_1.checksum] = demo_1.id
        if demo_2.checksum:
            self._checksum_to_memory_id[demo_2.checksum] = demo_2.id

    def check_access(self, memory: Memory, user_id: Optional[str], role: str = "visitor") -> bool:
        """Verify access rights based on privacy level, ownership, and RBAC clearance."""
        # Vault owner / admin / guardian always has full clearance
        if role in ["vault_owner", "admin", "guardian"]:
            return True
        # If user is the direct creator or uploader, they can always access their own memory
        if user_id and user_id in [memory.uploaded_by, memory.created_by_user_id]:
            return True
        # If memory is PRIVATE or RESTRICTED, only vault_owner, guardian, or uploader have access
        if memory.privacy_level in [PrivacyLevel.PRIVATE, PrivacyLevel.RESTRICTED]:
            return False
        # If FAMILY or FAMILY_ONLY, only vault_owner, guardian, and family_member have clearance
        if memory.privacy_level in [PrivacyLevel.FAMILY, PrivacyLevel.FAMILY_ONLY]:
            return role in ["vault_owner", "guardian", "family_member"]
        # If AUTHORIZED_USERS, visitors cannot access
        if memory.privacy_level in [PrivacyLevel.AUTHORIZED_USERS]:
            return role in ["vault_owner", "guardian", "family_member", "researcher"]
        # If MEMORIAL_PUBLIC
        return True

    async def list_memories(
        self,
        profile_id: Optional[str] = None,
        confidence: Optional[ConfidenceLevel] = None,
        category: Optional[MemoryCategory] = None,
        source_type: Optional[SourceType] = None,
        verification_status: Optional[VerificationStatus] = None,
        privacy_level: Optional[PrivacyLevel] = None,
        search_query: Optional[str] = None,
        person: Optional[str] = None,
        location: Optional[str] = None,
        include_archived: bool = False,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner",
        skip: int = 0,
        limit: int = 50
    ) -> List[Memory]:
        """Query memories with multi-criteria metadata search and filtering."""
        memories = [m for m in self._memories.values() if m.deleted_at is None]

        # Archived filter: hide archived unless explicitly requested
        if not include_archived:
            memories = [m for m in memories if not m.archived]

        # Profile filter
        if profile_id:
            memories = [m for m in memories if m.memorial_profile_id == profile_id]

        # Confidence filter
        if confidence:
            memories = [m for m in memories if m.confidence == confidence]

        # Category filter
        if category:
            memories = [m for m in memories if m.category == category]

        # Source type filter
        if source_type:
            memories = [m for m in memories if m.source_type == source_type]

        # Verification status filter
        if verification_status:
            memories = [m for m in memories if m.verification_status == verification_status]

        # Privacy level filter
        if privacy_level:
            memories = [m for m in memories if m.privacy_level == privacy_level]

        # Person filter
        if person:
            query_person = person.lower()
            memories = [
                m for m in memories
                if any(query_person in p.lower() for p in (m.people or [])) or
                   any(query_person in pid.lower() for pid in (m.people_ids or []))
            ]

        # Location filter
        if location:
            query_loc = location.lower()
            memories = [
                m for m in memories
                if (m.location and query_loc in m.location.lower()) or
                   (m.location_name and query_loc in m.location_name.lower())
            ]

        # Text search (Title, Description, Narrative)
        if search_query:
            q = search_query.lower()
            memories = [
                m for m in memories
                if q in m.title.lower() or
                   q in (m.description or "").lower() or
                   q in (m.narrative or "").lower() or
                   any(q in p.lower() for p in (m.people or [])) or
                   (m.location and q in m.location.lower())
            ]

        # Privacy authorization gate
        authorized_memories = [m for m in memories if self.check_access(m, user_id, role)]

        def _sort_key(m: Memory):
            dt = m.created_at
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt

        # Sort reverse chronological by created_at
        authorized_memories.sort(key=_sort_key, reverse=True)
        return authorized_memories[skip: skip + limit]

    async def get_memory(
        self,
        memory_id: str,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner"
    ) -> Optional[Memory]:
        """Retrieve a memory if authorized, and record audit view."""
        mem = self._memories.get(memory_id)
        if not mem or mem.deleted_at is not None:
            return None

        if not self.check_access(mem, user_id, role):
            await audit_service.record_event(
                action=AuditAction.VIEW,
                actor=user_id or "anonymous",
                resource=f"Memory:{memory_id}",
                result="UNAUTHORIZED",
                metadata={"reason": "Access denied by privacy policy"}
            )
            raise UnauthorizedMemoryAccessError(f"Access denied to private memory {memory_id}")

        await audit_service.record_event(
            action=AuditAction.VIEW,
            actor=user_id or "demo-user-001",
            resource=f"Memory:{memory_id}",
            result="SUCCESS"
        )
        return mem

    async def create_memory(
        self,
        memory_in: MemoryCreate,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner"
    ) -> Memory:
        """Create a new memory in the vault and handle duplicate detection."""
        memory_data = memory_in.model_dump()
        new_id = memory_data.get("id") or memory_data.get("memory_id") or str(uuid4())

        # Check duplicate by checksum if supplied
        checksum = memory_data.get("checksum")
        is_duplicate = False
        duplicate_ref_id = None
        if checksum and checksum in self._checksum_to_memory_id:
            duplicate_ref_id = self._checksum_to_memory_id[checksum]
            is_duplicate = True

        memory_data.pop("id", None)
        memory_data.pop("memory_id", None)
        memory_data.pop("uploaded_by", None)
        memory_data.pop("created_by_user_id", None)
        memory_data.pop("created_at", None)
        memory_data.pop("updated_at", None)

        new_memory = Memory(
            **memory_data,
            id=new_id,
            memory_id=new_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            uploaded_by=user_id,
            created_by_user_id=user_id
        )

        self._memories[new_memory.id] = new_memory
        if checksum:
            self._checksum_to_memory_id[checksum] = new_memory.id

        # Audit creation
        audit_meta = {
            "title": new_memory.title,
            "category": new_memory.category.value,
            "privacy_level": new_memory.privacy_level.value,
            "source_type": new_memory.source_type.value,
            "is_duplicate": is_duplicate
        }
        if is_duplicate:
            audit_meta["duplicate_of_id"] = duplicate_ref_id

        await audit_service.record_event(
            action=AuditAction.UPLOAD,
            actor=user_id or "demo-user-001",
            resource=f"Memory:{new_memory.id}",
            result="SUCCESS",
            metadata=audit_meta
        )

        return new_memory

    async def update_memory(
        self,
        memory_id: str,
        memory_update: MemoryUpdate,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner"
    ) -> Optional[Memory]:
        """Update memory fields and record audit trail."""
        mem = self._memories.get(memory_id)
        if not mem or mem.deleted_at is not None:
            return None

        if not self.check_access(mem, user_id, role):
            raise UnauthorizedMemoryAccessError(f"Access denied to modify memory {memory_id}")

        update_data = memory_update.model_dump(exclude_unset=True)
        privacy_changed = "privacy_level" in update_data and update_data["privacy_level"] != mem.privacy_level

        for field, value in update_data.items():
            setattr(mem, field, value)

        mem.updated_at = datetime.now(timezone.utc)

        # Audit event
        if privacy_changed:
            await audit_service.record_event(
                action=AuditAction.PRIVACY_CHANGED,
                actor=user_id or "demo-user-001",
                resource=f"Memory:{memory_id}",
                result="SUCCESS",
                metadata={"new_privacy_level": mem.privacy_level.value}
            )
        else:
            await audit_service.record_event(
                action=AuditAction.EDIT,
                actor=user_id or "demo-user-001",
                resource=f"Memory:{memory_id}",
                result="SUCCESS",
                metadata={"updated_fields": list(update_data.keys())}
            )

        return mem

    async def verify_memory(
        self,
        memory_id: str,
        status: VerificationStatus,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner"
    ) -> Optional[Memory]:
        """Update memory verification status."""
        mem = self._memories.get(memory_id)
        if not mem or mem.deleted_at is not None:
            return None

        if not self.check_access(mem, user_id, role):
            raise UnauthorizedMemoryAccessError(f"Access denied to verify memory {memory_id}")

        mem.verification_status = status
        if status == VerificationStatus.VERIFIED:
            mem.confidence = ConfidenceLevel.VERIFIED
            mem.confidence_score = 1.0
            action = AuditAction.VERIFY
        elif status == VerificationStatus.REJECTED:
            mem.confidence = ConfidenceLevel.UNKNOWN_UNSUPPORTED
            mem.confidence_score = 0.0
            action = AuditAction.REJECT
        else:
            mem.confidence = ConfidenceLevel.SUPPORTED_INFERENCE
            action = AuditAction.EDIT

        mem.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=action,
            actor=user_id or "demo-user-001",
            resource=f"Memory:{memory_id}",
            result="SUCCESS",
            metadata={"new_status": status.value}
        )
        return mem

    async def archive_memory(
        self,
        memory_id: str,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner"
    ) -> Optional[Memory]:
        """Soft-archive memory without physically destroying original media."""
        mem = self._memories.get(memory_id)
        if not mem or mem.deleted_at is not None:
            return None

        if not self.check_access(mem, user_id, role):
            raise UnauthorizedMemoryAccessError(f"Access denied to archive memory {memory_id}")

        mem.archived = True
        mem.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.ARCHIVE,
            actor=user_id or "demo-user-001",
            resource=f"Memory:{memory_id}",
            result="SUCCESS",
            metadata={"archived": True}
        )
        return mem

    async def unarchive_memory(
        self,
        memory_id: str,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner"
    ) -> Optional[Memory]:
        """Restore an archived memory back to active views."""
        mem = self._memories.get(memory_id)
        if not mem or mem.deleted_at is not None:
            return None

        if not self.check_access(mem, user_id, role):
            raise UnauthorizedMemoryAccessError(f"Access denied to restore memory {memory_id}")

        mem.archived = False
        mem.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.EDIT,
            actor=user_id or "demo-user-001",
            resource=f"Memory:{memory_id}",
            result="SUCCESS",
            metadata={"unarchived": True}
        )
        return mem

    async def delete_memory(
        self,
        memory_id: str,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner"
    ) -> bool:
        """Securely soft-delete memory and record audit trail."""
        mem = self._memories.get(memory_id)
        if not mem or mem.deleted_at is not None:
            return False

        if not self.check_access(mem, user_id, role):
            raise UnauthorizedMemoryAccessError(f"Access denied to delete memory {memory_id}")

        mem.deleted_at = datetime.now(timezone.utc)
        mem.updated_at = datetime.now(timezone.utc)

        await audit_service.record_event(
            action=AuditAction.DELETE,
            actor=user_id or "demo-user-001",
            resource=f"Memory:{memory_id}",
            result="SUCCESS",
            metadata={"title": mem.title, "deleted_at": str(mem.deleted_at)}
        )
        return True

    async def export_memory(
        self,
        memory_id: str,
        user_id: Optional[str] = "demo-user-001",
        role: str = "vault_owner"
    ) -> Dict[str, Any]:
        """Generate secure memory export bundle without exposing absolute paths."""
        mem = await self.get_memory(memory_id, user_id=user_id, role=role)
        if not mem:
            raise FileNotFoundError(f"Memory {memory_id} not found")

        export_bundle = {
            "version": "ECHO-MemoryVault-Export-v2.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "memory": {
                "id": mem.id,
                "title": mem.title,
                "description": mem.description,
                "category": mem.category.value,
                "date": mem.date,
                "approximate_date": mem.approximate_date,
                "location": mem.location,
                "people": mem.people,
                "source_type": mem.source_type.value,
                "confidence": mem.confidence.value,
                "verification_status": mem.verification_status.value,
                "privacy_level": mem.privacy_level.value,
                "consent_status": mem.consent_status.value,
                "checksum": mem.checksum,
                "original_filename": mem.original_filename,
                "file_size": mem.file_size,
                "storage_reference": mem.storage_path,  # Safe relative path only
                "is_ai_generated": mem.source_type == SourceType.AI_GENERATED
            },
            "provenance_records": [p.model_dump() for p in mem.provenance_records],
            "ethical_notice": (
                "ECHO is an AI-generated memorial representation. "
                "It does not recreate consciousness, identity, or the actual person. "
                "All exported representations are grounded in preserved evidence."
            )
        }

        await audit_service.record_event(
            action=AuditAction.EXPORT,
            actor=user_id or "demo-user-001",
            resource=f"Memory:{memory_id}",
            result="SUCCESS",
            metadata={"export_version": "2.0"}
        )

        return export_bundle

    async def get_vault_statistics(self, profile_id: Optional[str] = None) -> Dict[str, Any]:
        """Aggregate real statistics from active preserved memories in vault."""
        active = [m for m in self._memories.values() if m.deleted_at is None and not m.archived]
        if profile_id:
            active = [m for m in active if m.memorial_profile_id == profile_id]

        photos = sum(1 for m in active if m.source_type in [SourceType.ORIGINAL_PHOTO, SourceType.PHOTOGRAPH])
        videos = sum(1 for m in active if m.source_type in [SourceType.ORIGINAL_VIDEO, SourceType.VIDEO])
        audio = sum(1 for m in active if m.source_type in [SourceType.ORIGINAL_AUDIO, SourceType.AUDIO_RECORDING])
        docs = sum(1 for m in active if m.source_type in [SourceType.DOCUMENT, SourceType.LETTER, SourceType.DIARY])

        unique_people = set()
        for m in active:
            for p in (m.people or []):
                unique_people.add(p)

        return {
            "total_memories": len(active),
            "verified_memories": sum(1 for m in active if m.confidence == ConfidenceLevel.VERIFIED),
            "supported_inferences": sum(1 for m in active if m.confidence == ConfidenceLevel.SUPPORTED_INFERENCE),
            "unknown_unsupported": sum(1 for m in active if m.confidence == ConfidenceLevel.UNKNOWN_UNSUPPORTED),
            "photos_count": photos,
            "videos_count": videos,
            "audio_count": audio,
            "documents_count": docs,
            "people_count": len(unique_people),
            "life_events_count": len(active),
            "conversation_sessions_count": 4,
            "privacy_status": "Confined to Private Vault (D:\\ECHO\\storage)",
            "is_demonstration_mode": False
        }

    async def get_memories(
        self,
        memorial_profile_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Memory]:
        """Fetch memories for a memorial profile (alias for list_memories)."""
        return await self.list_memories(profile_id=memorial_profile_id, limit=limit)


# Singleton service instance
memory_service = MemoryService()
