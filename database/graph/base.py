"""Knowledge Graph Database Abstraction Interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str  # e.g., "Person", "Event", "Location", "Memory"
    properties: Dict[str, Any]


class GraphRelationship(BaseModel):
    source_id: str
    target_id: str
    relation_type: str  # e.g., "ATTENDED", "SPOUSE_OF", "HAPPENED_AT", "MENTIONS"
    properties: Dict[str, Any] = {}


class BaseGraphDatabase(ABC):
    """Abstract interface for knowledge graph queries and relationship traversal."""

    @abstractmethod
    async def add_node(self, node: GraphNode) -> bool:
        """Add or update an entity node in the graph."""
        pass

    @abstractmethod
    async def add_relationship(self, rel: GraphRelationship) -> bool:
        """Add or update an edge between two entities."""
        pass

    @abstractmethod
    async def get_neighbors(
        self,
        node_id: str,
        relation_types: Optional[List[str]] = None,
        max_depth: int = 1
    ) -> List[Dict[str, Any]]:
        """Retrieve connected entities and relations up to max_depth."""
        pass

    @abstractmethod
    async def find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 3
    ) -> List[List[str]]:
        """Find relationship paths connecting two entities."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return graph connection status."""
        pass
