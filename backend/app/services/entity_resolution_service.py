"""Conservative Entity Resolution Service for ECHO.

Identifies potential duplicate entities across heterogeneous multimodal evidence
without destructive, unverified data merges.

CRITICAL RULE:
NEVER silently merge entities merely because names appear similar.
Candidate matches are registered as unconfirmed aliases/possible duplicates
for explicit user or guardian verification.
"""

from typing import List, Dict, Any, Optional
import re
from uuid import uuid4
from datetime import datetime, timezone
import difflib

from models.entity_alias import EntityAlias
from models.graph import GraphNodeModel


class EntityResolutionService:
    """Conservative entity matching, title normalization, and duplicate identification."""

    # Honorific titles and salutations to normalize
    TITLES = {"dr", "dr.", "prof", "prof.", "mr", "mr.", "mrs", "mrs.", "ms", "ms.", "shri", "smt"}

    def __init__(self):
        self._aliases: Dict[str, EntityAlias] = {}

    def normalize_name(self, name: str) -> str:
        """Strip honorifics, normalize punctuation and whitespace."""
        if not name:
            return ""
        tokens = name.strip().split()
        filtered = [
            t for t in tokens
            if t.lower() not in self.TITLES
        ]
        norm = " ".join(filtered).strip().lower()
        # Remove trailing/leading punctuation
        norm = re.sub(r"[^\w\s]", "", norm)
        return norm

    def calculate_similarity(self, name_a: str, name_b: str) -> float:
        """Calculate string and token-level similarity ratio [0.0, 1.0]."""
        norm_a = self.normalize_name(name_a)
        norm_b = self.normalize_name(name_b)

        if not norm_a or not norm_b:
            return 0.0

        # Exact match after title stripping
        if norm_a == norm_b:
            return 1.0

        # Substring / token subset match (e.g. "Arun Kumar" vs "Arun")
        tokens_a = set(norm_a.split())
        tokens_b = set(norm_b.split())
        if tokens_a and tokens_b and (tokens_a.issubset(tokens_b) or tokens_b.issubset(tokens_a)):
            return 0.85

        # Sequence matcher ratio
        return difflib.SequenceMatcher(None, norm_a, norm_b).ratio()

    def find_potential_matches(
        self,
        candidate_name: str,
        existing_nodes: List[GraphNodeModel],
        threshold: float = 0.75
    ) -> List[Dict[str, Any]]:
        """Identify potential duplicate nodes in the knowledge graph.
        
        Does NOT merge nodes. Returns ranked candidates with similarity scores.
        """
        matches = []
        for node in existing_nodes:
            sim = self.calculate_similarity(candidate_name, node.name)
            if sim >= threshold:
                matches.append({
                    "canonical_node_id": node.id,
                    "canonical_name": node.name,
                    "candidate_name": candidate_name,
                    "similarity_score": round(sim, 3),
                    "is_exact_after_normalization": self.normalize_name(candidate_name) == self.normalize_name(node.name)
                })

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches

    def register_alias(
        self,
        canonical_entity_id: str,
        canonical_name: str,
        alias_name: str,
        memorial_profile_id: str = "default-profile-001",
        is_confirmed: bool = False,
        notes: Optional[str] = None
    ) -> EntityAlias:
        """Explicitly record an alias mapping without destructive node deletion."""
        sim = self.calculate_similarity(canonical_name, alias_name)
        alias = EntityAlias(
            id=str(uuid4()),
            memorial_profile_id=memorial_profile_id,
            canonical_entity_id=canonical_entity_id,
            canonical_name=canonical_name,
            alias_name=alias_name,
            similarity_score=sim,
            is_confirmed=is_confirmed,
            is_possible_duplicate=not is_confirmed,
            notes=notes or f"Similarity score: {sim:.2f}",
            created_at=datetime.now(timezone.utc)
        )
        self._aliases[alias.id] = alias
        return alias

    def get_aliases_for_entity(self, canonical_entity_id: str) -> List[EntityAlias]:
        return [
            a for a in self._aliases.values()
            if a.canonical_entity_id == canonical_entity_id
        ]
