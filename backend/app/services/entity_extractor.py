"""Entity Extraction Service for ECHO.

Extracts structured named entities from documents, transcripts, captions, and descriptions:
- Entity types: PERSON, LOCATION, ORGANIZATION, OBJECT, DATE, EVENT, DOCUMENT, MEDIA
- Provenance grounding: records discovery method and source reference
- Strict evidence boundary: discovering a person's name in a document does not
  falsely assert their physical presence in an unrelated photograph.
"""

from typing import List, Dict, Any, Optional
import re
from uuid import uuid4
from datetime import datetime, timezone

from models.enums import EntityType, ProvenanceStatus, ConfidenceLevel
from models.entity import Entity


class EntityExtractor:
    """Specialized evidentiary entity extractor."""

    DATE_PATTERN = re.compile(
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b|"
        r"\b(?:19|20)\d{2}\b|"
        r"\b\d{1,2}/\d{1,2}/(?:19|20)\d{2}\b",
        re.IGNORECASE
    )

    ORG_KEYWORDS = ["university", "college", "school", "hospital", "library", "church", "foundation", "institute", "ministry", "association"]
    LOC_KEYWORDS = ["paris", "oxford", "cambridge", "london", "kyoto", "windermere", "boston", "india", "yorkshire", "highlands", "scotland"]

    def __init__(self):
        self.processor_name = "EntityExtractor"
        self.processor_version = "echo-entity-v1.0"
        self._entity_store: Dict[str, List[Entity]] = {}  # memory_id -> list of entities

    def extract_entities_from_text(
        self,
        text: str,
        media_id: Optional[str] = None,
        memory_id: Optional[str] = None,
        provenance_status: ProvenanceStatus = ProvenanceStatus.DIRECTLY_OBSERVED
    ) -> List[Entity]:
        """Extract typed entities from document text or narrative excerpt."""
        if not text or not text.strip():
            return []

        entities: List[Entity] = []
        seen_values = set()

        # 1. Date Extraction
        for match in self.DATE_PATTERN.finditer(text):
            val = match.group().strip()
            if val.lower() not in seen_values:
                seen_values.add(val.lower())
                entities.append(Entity(
                    id=str(uuid4()),
                    entity_type=EntityType.DATE,
                    value=val,
                    source_media_id=media_id,
                    source_memory_id=memory_id,
                    provenance_status=provenance_status,
                    confidence=ConfidenceLevel.VERIFIED,
                    confidence_score=1.0,
                    extraction_method="regex_date_parser"
                ))

        # 2. Heuristic Organization Extraction
        lines = text.split("\n")
        words = re.findall(r"\b[A-Z][a-zA-Z0-9\'-]+\b(?:\s+\b[A-Z][a-zA-Z0-9\'-]+\b)*", text)
        for chunk in words:
            chunk_lower = chunk.lower()
            if any(k in chunk_lower for k in self.ORG_KEYWORDS):
                if chunk_lower not in seen_values:
                    seen_values.add(chunk_lower)
                    entities.append(Entity(
                        id=str(uuid4()),
                        entity_type=EntityType.ORGANIZATION,
                        value=chunk,
                        source_media_id=media_id,
                        source_memory_id=memory_id,
                        provenance_status=provenance_status,
                        confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
                        confidence_score=0.9,
                        extraction_method="heuristic_org_filter"
                    ))
            elif any(k in chunk_lower for k in self.LOC_KEYWORDS):
                if chunk_lower not in seen_values:
                    seen_values.add(chunk_lower)
                    entities.append(Entity(
                        id=str(uuid4()),
                        entity_type=EntityType.LOCATION,
                        value=chunk,
                        source_media_id=media_id,
                        source_memory_id=memory_id,
                        provenance_status=provenance_status,
                        confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
                        confidence_score=0.9,
                        extraction_method="heuristic_geo_filter"
                    ))

        # 3. Person Names via Honorifics and Patterns
        person_matches = re.findall(
            r"\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|Sir|Lord|Lady)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
            text
        )
        for person in person_matches:
            if person.lower() not in seen_values:
                seen_values.add(person.lower())
                entities.append(Entity(
                    id=str(uuid4()),
                    entity_type=EntityType.PERSON,
                    value=person,
                    source_media_id=media_id,
                    source_memory_id=memory_id,
                    provenance_status=provenance_status,
                    confidence=ConfidenceLevel.SUPPORTED_INFERENCE,
                    confidence_score=0.88,
                    extraction_method="honorific_person_matcher"
                ))

        if memory_id:
            if memory_id not in self._entity_store:
                self._entity_store[memory_id] = []
            self._entity_store[memory_id].extend(entities)

        return entities

    def get_entities_for_memory(self, memory_id: str) -> List[Entity]:
        """Retrieve indexed entities linked to a memory."""
        return self._entity_store.get(memory_id, [])

    def register_user_provided_entities(
        self,
        memory_id: str,
        people: List[str],
        location: Optional[str] = None
    ) -> List[Entity]:
        """Register entities explicitly provided by the user."""
        registered = []
        for person in people:
            registered.append(Entity(
                id=str(uuid4()),
                entity_type=EntityType.PERSON,
                value=person,
                source_memory_id=memory_id,
                provenance_status=ProvenanceStatus.USER_PROVIDED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=1.0,
                extraction_method="user_form_input"
            ))
        if location:
            registered.append(Entity(
                id=str(uuid4()),
                entity_type=EntityType.LOCATION,
                value=location,
                source_memory_id=memory_id,
                provenance_status=ProvenanceStatus.USER_PROVIDED,
                confidence=ConfidenceLevel.VERIFIED,
                confidence_score=1.0,
                extraction_method="user_form_input"
            ))

        if memory_id:
            if memory_id not in self._entity_store:
                self._entity_store[memory_id] = []
            self._entity_store[memory_id].extend(registered)

        return registered


entity_extractor = EntityExtractor()
