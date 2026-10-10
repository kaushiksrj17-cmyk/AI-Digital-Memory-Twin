"""Neo4j Knowledge Graph Adapter."""

from typing import List, Dict, Any, Optional
from database.graph.base import BaseGraphDatabase, GraphNode, GraphRelationship


class Neo4jGraphDatabase(BaseGraphDatabase):
    """Production Neo4j adapter with unconfigured status detection."""

    def __init__(
        self,
        uri: Optional[str] = "bolt://localhost:7687",
        user: Optional[str] = "neo4j",
        password: Optional[str] = None
    ):
        self.uri = uri
        self.user = user
        self.password = password
        self.is_connected = False

    async def add_node(self, node: GraphNode) -> bool:
        if not self.is_connected:
            raise RuntimeError("Neo4j provider is unconfigured or not connected.")
        return True

    async def add_relationship(self, rel: GraphRelationship) -> bool:
        if not self.is_connected:
            raise RuntimeError("Neo4j provider is unconfigured or not connected.")
        return True

    async def get_neighbors(
        self,
        node_id: str,
        relation_types: Optional[List[str]] = None,
        max_depth: int = 1
    ) -> List[Dict[str, Any]]:
        if not self.is_connected:
            raise RuntimeError("Neo4j provider is unconfigured or not connected.")
        return []

    async def find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 3
    ) -> List[List[str]]:
        if not self.is_connected:
            raise RuntimeError("Neo4j provider is unconfigured or not connected.")
        return []

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "Neo4j",
            "status": "ready" if self.is_connected else "unconfigured",
            "uri": self.uri,
            "user": self.user
        }
