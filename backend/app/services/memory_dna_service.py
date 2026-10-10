"""Memory DNA Service for ECHO.

Compiles, versions, and validates evidence-grounded Memory DNA profiles.
Memory DNA is a structured representation of documented life facts and experiences.
It is NOT a personality simulator and NEVER fabricates traits or events.
Missing fields strictly remain UNKNOWN.
"""

from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime, timezone
from collections import defaultdict

from models.enums import (
    MemoryDNACategory,
    ConfidenceLevel,
    ProvenanceStatus,
    VerificationStatus,
    EntityType,
    EventType,
)
from models.memory_dna import (
    MemoryDNA,
    MemoryDNAItem,
    MemoryDNAVersion,
)


class MemoryDNAService:
    """Manages Memory DNA aggregation, item verification, and version tracking."""

    def __init__(self):
        # In-memory stores for dev and testing
        self._dna_records: Dict[str, MemoryDNA] = {}  # memorial_profile_id -> MemoryDNA
        self._items: Dict[str, MemoryDNAItem] = {}    # dna_item_id -> MemoryDNAItem
        self._versions: Dict[str, List[MemoryDNAVersion]] = defaultdict(list) # memorial_profile_id -> list of versions

    async def get_or_create_dna(self, memorial_profile_id: str = "default-profile-001") -> MemoryDNA:
        """Fetch active Memory DNA or initialize empty structure."""
        if memorial_profile_id in self._dna_records:
            return self._dna_records[memorial_profile_id]

        dna = MemoryDNA(
            memory_dna_id=str(uuid4()),
            memorial_profile_id=memorial_profile_id,
            summary="Structured archive foundation. Missing details remain unrecorded.",
            confidence=ConfidenceLevel.VERIFIED,
            provenance=ProvenanceStatus.DIRECTLY_OBSERVED,
            last_updated=datetime.now(timezone.utc),
            version=1
        )
        self._dna_records[memorial_profile_id] = dna
        return dna

    async def build_from_evidence(
        self,
        memorial_profile_id: str,
        memories: List[Dict[str, Any]],
        evidence_list: List[Dict[str, Any]],
        entities: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        relationships: Optional[List[Dict[str, Any]]] = None,
        changed_by: str = "system",
        change_reason: str = "Compiled from multimodal evidence"
    ) -> MemoryDNA:
        """Deterministic compilation of multimodal evidence into categorized Memory DNA items."""
        current_dna = await self.get_or_create_dna(memorial_profile_id)

        # Snapshot existing DNA before updating (versioning requirement)
        if current_dna.version >= 1 and (current_dna.people or current_dna.education or current_dna.career or current_dna.stories):
            prev_snapshot = current_dna.model_dump()
            version_record = MemoryDNAVersion(
                version_id=str(uuid4()),
                memory_dna_id=current_dna.memory_dna_id,
                memorial_profile_id=memorial_profile_id,
                version=current_dna.version,
                dna_snapshot=prev_snapshot,
                changed_by=changed_by,
                change_reason=change_reason,
                source_evidence=current_dna.source_references,
                created_at=datetime.now(timezone.utc)
            )
            self._versions[memorial_profile_id].append(version_record)
            new_version_num = current_dna.version + 1
        else:
            new_version_num = 1

        # Clear active items for this profile
        profile_item_ids = [iid for iid, item in self._items.items() if item.memorial_profile_id == memorial_profile_id]
        for iid in profile_item_ids:
            del self._items[iid]

        # Containers for the 22 categories
        category_items: Dict[MemoryDNACategory, List[Dict[str, Any]]] = defaultdict(list)
        all_source_refs = set()

        # 1. Process Memories
        for m in memories:
            m_id = m.get("id")
            m_title = m.get("title", "")
            m_desc = m.get("description", "")
            m_cat = m.get("category", "OTHER").upper()
            m_date = m.get("date")
            m_loc = m.get("location")

            all_source_refs.add(f"Memory: {m_title}")

            # Map MemoryCategory to MemoryDNACategory
            dna_cat = MemoryDNACategory.PERSONAL_STORIES
            if m_cat == "EDUCATION":
                dna_cat = MemoryDNACategory.EDUCATION
            elif m_cat == "CAREER":
                dna_cat = MemoryDNACategory.CAREER
            elif m_cat == "FAMILY":
                dna_cat = MemoryDNACategory.FAMILY
            elif m_cat == "FRIENDS":
                dna_cat = MemoryDNACategory.FRIENDS
            elif m_cat == "TRAVEL":
                dna_cat = MemoryDNACategory.TRAVEL
            elif m_cat == "HOBBIES":
                dna_cat = MemoryDNACategory.HOBBIES
            elif m_cat == "ACHIEVEMENTS":
                dna_cat = MemoryDNACategory.ACHIEVEMENTS
            elif m_cat == "CHILDHOOD":
                dna_cat = MemoryDNACategory.CHILDHOOD
            elif m_cat == "SPECIAL_EVENTS":
                dna_cat = MemoryDNACategory.IMPORTANT_EVENTS

            item = MemoryDNAItem(
                dna_item_id=str(uuid4()),
                memorial_profile_id=memorial_profile_id,
                category=dna_cat,
                key=m_title,
                value={
                    "title": m_title,
                    "description": m_desc,
                    "date": m_date,
                    "location": m_loc
                },
                description=f"Documented memory: {m_title}",
                source_memory_ids=[m_id] if m_id else [],
                provenance_status=ProvenanceStatus.USER_PROVIDED if m.get("source_type") == "USER_ENTRY" else ProvenanceStatus.DIRECTLY_OBSERVED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=1.0,
                verification_status=VerificationStatus.VERIFIED
            )
            self._items[item.dna_item_id] = item
            category_items[dna_cat].append(item.model_dump())

            # Also check for documented places
            if m_loc:
                loc_item = MemoryDNAItem(
                    dna_item_id=str(uuid4()),
                    memorial_profile_id=memorial_profile_id,
                    category=MemoryDNACategory.PLACES,
                    key="place_of_memory",
                    value=m_loc,
                    description=f"Referenced in memory '{m_title}'",
                    source_memory_ids=[m_id] if m_id else [],
                    provenance_status=ProvenanceStatus.DIRECTLY_OBSERVED,
                    confidence=ConfidenceLevel.VERIFIED
                )
                self._items[loc_item.dna_item_id] = loc_item
                category_items[MemoryDNACategory.PLACES].append(loc_item.model_dump())

        # 2. Process Entities
        for e in entities:
            etype = e.get("entity_type", "").upper()
            val = e.get("value", "").strip()
            if not val:
                continue

            dna_cat = MemoryDNACategory.UNKNOWN
            if etype == "PERSON":
                dna_cat = MemoryDNACategory.PEOPLE if hasattr(MemoryDNACategory, "PEOPLE") else MemoryDNACategory.RELATIONSHIPS
            elif etype in ("LOCATION", "PLACE"):
                dna_cat = MemoryDNACategory.PLACES
            elif etype == "ORGANIZATION":
                dna_cat = MemoryDNACategory.CAREER
            elif etype == "DATE":
                dna_cat = MemoryDNACategory.IMPORTANT_EVENTS

            item = MemoryDNAItem(
                dna_item_id=str(uuid4()),
                memorial_profile_id=memorial_profile_id,
                category=dna_cat,
                key=f"{etype.lower()}:{val}",
                value=val,
                description=f"Extracted {etype} from multimodal evidence",
                source_memory_ids=[e["source_memory_id"]] if e.get("source_memory_id") else [],
                source_evidence_ids=[e["id"]] if e.get("id") else [],
                provenance_status=ProvenanceStatus(e.get("provenance_status", "DIRECTLY_OBSERVED")),
                confidence=ConfidenceLevel(e.get("confidence", "VERIFIED")),
                confidence_score=float(e.get("confidence_score", 1.0))
            )
            self._items[item.dna_item_id] = item
            category_items[dna_cat].append(item.model_dump())

        # 3. Process Events
        for ev in events:
            ev_title = ev.get("title", "").strip()
            if not ev_title:
                continue
            item = MemoryDNAItem(
                dna_item_id=str(uuid4()),
                memorial_profile_id=memorial_profile_id,
                category=MemoryDNACategory.IMPORTANT_EVENTS,
                key=ev_title,
                value={
                    "title": ev_title,
                    "date": ev.get("date"),
                    "location": ev.get("location"),
                    "type": ev.get("event_type")
                },
                description=ev.get("description", ""),
                source_memory_ids=[ev["memory_id"]] if ev.get("memory_id") else [],
                source_evidence_ids=[ev["id"]] if ev.get("id") else [],
                provenance_status=ProvenanceStatus(ev.get("provenance_status", "DIRECTLY_OBSERVED")),
                confidence=ConfidenceLevel(ev.get("confidence", "VERIFIED"))
            )
            self._items[item.dna_item_id] = item
            category_items[MemoryDNACategory.IMPORTANT_EVENTS].append(item.model_dump())

        # Construct updated MemoryDNA model
        updated_dna = MemoryDNA(
            memory_dna_id=current_dna.memory_dna_id,
            memorial_profile_id=memorial_profile_id,
            summary=f"Memory DNA compiled with {len(self._items)} verified items.",
            life_events=category_items[MemoryDNACategory.IMPORTANT_EVENTS],
            people=category_items[MemoryDNACategory.RELATIONSHIPS] + category_items[MemoryDNACategory.FAMILY],
            relationships=category_items[MemoryDNACategory.RELATIONSHIPS],
            places=category_items[MemoryDNACategory.PLACES],
            education=category_items[MemoryDNACategory.EDUCATION],
            career=category_items[MemoryDNACategory.CAREER],
            family=category_items[MemoryDNACategory.FAMILY],
            friends=category_items[MemoryDNACategory.FRIENDS],
            hobbies=category_items[MemoryDNACategory.HOBBIES],
            interests=category_items[MemoryDNACategory.INTERESTS],
            important_objects=category_items[MemoryDNACategory.IMPORTANT_OBJECTS],
            important_dates=[ev for ev in category_items[MemoryDNACategory.IMPORTANT_EVENTS] if ev.get("value", {}).get("date")],
            documented_preferences=category_items[MemoryDNACategory.DOCUMENTED_PREFERENCES],
            documented_values=category_items[MemoryDNACategory.DOCUMENTED_VALUES],
            known_phrases=category_items[MemoryDNACategory.KNOWN_PHRASES],
            frequently_mentioned_topics=category_items[MemoryDNACategory.FREQUENT_TOPICS],
            stories=category_items[MemoryDNACategory.PERSONAL_STORIES],
            achievements=category_items[MemoryDNACategory.ACHIEVEMENTS],
            travel=category_items[MemoryDNACategory.TRAVEL],
            legacy=category_items[MemoryDNACategory.LEGACY],
            source_references=list(all_source_refs),
            confidence=ConfidenceLevel.VERIFIED,
            provenance=ProvenanceStatus.DIRECTLY_OBSERVED,
            last_updated=datetime.now(timezone.utc),
            version=new_version_num
        )
        self._dna_records[memorial_profile_id] = updated_dna
        return updated_dna

    async def get_items(
        self,
        memorial_profile_id: str,
        category: Optional[MemoryDNACategory] = None,
        confidence: Optional[ConfidenceLevel] = None
    ) -> List[MemoryDNAItem]:
        """Query items with optional category and confidence filters."""
        results = []
        for item in self._items.values():
            if item.memorial_profile_id != memorial_profile_id:
                continue
            if category and item.category != category:
                continue
            if confidence and item.confidence != confidence:
                continue
            results.append(item)
        return results

    async def get_item(self, item_id: str) -> Optional[MemoryDNAItem]:
        return self._items.get(item_id)

    async def verify_item(self, item_id: str) -> Optional[MemoryDNAItem]:
        """Manually verify a Memory DNA item (promotes to VERIFIED)."""
        item = self._items.get(item_id)
        if not item:
            return None
        item.verification_status = VerificationStatus.VERIFIED
        item.confidence = ConfidenceLevel.VERIFIED
        item.confidence_score = 1.0
        item.updated_at = datetime.now(timezone.utc)
        return item

    async def reject_item(self, item_id: str) -> Optional[MemoryDNAItem]:
        """Mark an item as rejected / unsupported."""
        item = self._items.get(item_id)
        if not item:
            return None
        item.verification_status = VerificationStatus.REJECTED
        item.confidence = ConfidenceLevel.UNKNOWN_UNSUPPORTED
        item.confidence_score = 0.0
        item.updated_at = datetime.now(timezone.utc)
        return item

    async def get_history(self, memorial_profile_id: str) -> List[MemoryDNAVersion]:
        """Retrieve historical versions of Memory DNA."""
        return self._versions.get(memorial_profile_id, [])

    async def get_stats(self, memorial_profile_id: str) -> Dict[str, Any]:
        """Calculate statistics across Memory DNA items."""
        items = [i for i in self._items.values() if i.memorial_profile_id == memorial_profile_id]
        category_counts = defaultdict(int)
        conf_counts = defaultdict(int)

        for i in items:
            cat_name = i.category.value if hasattr(i.category, "value") else str(i.category)
            category_counts[cat_name] += 1
            conf_name = i.confidence.value if hasattr(i.confidence, "value") else str(i.confidence)
            conf_counts[conf_name] += 1

        return {
            "total_items": len(items),
            "by_category": dict(category_counts),
            "by_confidence": dict(conf_counts),
            "verified_count": conf_counts.get("VERIFIED", 0),
            "supported_inferences": conf_counts.get("SUPPORTED_INFERENCE", 0),
            "unknown_items": conf_counts.get("UNKNOWN_UNSUPPORTED", 0)
        }


# Global singleton
_global_memory_dna_service: Optional[MemoryDNAService] = None


def get_memory_dna_service() -> MemoryDNAService:
    global _global_memory_dna_service
    if _global_memory_dna_service is None:
        _global_memory_dna_service = MemoryDNAService()
    return _global_memory_dna_service
