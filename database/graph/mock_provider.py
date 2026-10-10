"""In-memory Knowledge Graph provider for local testing and zero-dependency operation."""

from typing import List, Dict, Any, Optional
from collections import defaultdict, deque
from database.graph.base import BaseGraphDatabase, GraphNode, GraphRelationship


class MockGraphDatabase(BaseGraphDatabase):
    """In-memory adjacency graph implementation."""

    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        # adjacency: source_id -> list of (target_id, relation_type, properties)
        self._adj: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # reverse adjacency: target_id -> list of (source_id, relation_type, properties)
        self._rev_adj: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    async def add_node(self, node: GraphNode) -> bool:
        self._nodes[node.id] = node
        return True

    async def add_relationship(self, rel: GraphRelationship) -> bool:
        self._adj[rel.source_id].append({
            "target_id": rel.target_id,
            "relation_type": rel.relation_type,
            "properties": rel.properties
        })
        self._rev_adj[rel.target_id].append({
            "source_id": rel.source_id,
            "relation_type": rel.relation_type,
            "properties": rel.properties
        })
        return True

    async def get_neighbors(
        self,
        node_id: str,
        relation_types: Optional[List[str]] = None,
        max_depth: int = 1
    ) -> List[Dict[str, Any]]:
        neighbors: List[Dict[str, Any]] = []
        for edge in self._adj.get(node_id, []):
            if relation_types and edge["relation_type"] not in relation_types:
                continue
            target_node = self._nodes.get(edge["target_id"])
            neighbors.append({
                "relation": edge["relation_type"],
                "target": target_node.model_dump() if target_node else {"id": edge["target_id"]},
                "direction": "outgoing"
            })

        for edge in self._rev_adj.get(node_id, []):
            if relation_types and edge["relation_type"] not in relation_types:
                continue
            src_node = self._nodes.get(edge["source_id"])
            neighbors.append({
                "relation": edge["relation_type"],
                "source": src_node.model_dump() if src_node else {"id": edge["source_id"]},
                "direction": "incoming"
            })

        return neighbors

    async def find_paths(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 3
    ) -> List[List[str]]:
        if start_node_id not in self._nodes or end_node_id not in self._nodes:
            return []

        queue = deque([[start_node_id]])
        paths: List[List[str]] = []

        while queue:
            current_path = queue.popleft()
            if len(current_path) > max_depth + 1:
                continue

            last_node = current_path[-1]
            if last_node == end_node_id:
                paths.append(current_path)
                continue

            for edge in self._adj.get(last_node, []):
                next_node = edge["target_id"]
                if next_node not in current_path:
                    queue.append(current_path + [next_node])

        return paths

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": "MockGraphDatabase (In-Memory)",
            "status": "ready",
            "nodes_count": len(self._nodes),
            "edges_count": sum(len(edges) for edges in self._adj.values())
        }
