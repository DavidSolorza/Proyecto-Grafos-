"""Custom Elevated Graph (GE) structure without external libraries."""
from collections import deque
from typing import Optional
from src.features.elevated_graph.domain.entities import VertexE, EdgeE


class GraphE:
    """Manages the elevated graph infrastructure."""

    def __init__(self) -> None:
        self.vertices: dict[str, VertexE] = {}
        self.edges: dict[str, EdgeE] = {}
        self.adj: dict[str, list[EdgeE]] = {}

    def add_vertex(self, vertex: VertexE) -> None:
        """Add a vertex to the graph."""
        self.vertices[vertex.id] = vertex
        if vertex.id not in self.adj:
            self.adj[vertex.id] = []

    def add_edge(self, edge: EdgeE) -> None:
        """Add an undirected edge or bridge connecting two vertices."""
        if edge.u not in self.vertices or edge.v not in self.vertices:
            raise ValueError(f"Endpoints {edge.u} and {edge.v} must exist.")
        self.edges[edge.id] = edge
        self.adj[edge.u].append(edge)
        self.adj[edge.v].append(edge)

    def get_connected_component(self, start_id: str, walkable_only: bool = False) -> set[str]:
        """Custom BFS to find all accessible vertices from start_id.

        With `walkable_only`, edges where walking is not allowed are ignored.
        """
        if start_id not in self.vertices:
            return set()

        visited: set[str] = {start_id}
        queue: deque[str] = deque([start_id])

        while queue:
            curr = queue.popleft()
            for edge in self.adj.get(curr, []):
                if edge.is_destroyed or (walkable_only and edge.time_walk is None):
                    continue
                neighbor = edge.v if edge.u == curr else edge.u
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return visited

    def get_base_vertex(self) -> Optional[VertexE]:
        """Find the unique base vertex."""
        for v in self.vertices.values():
            if v.type.value == "BASE":
                return v
        return None

