"""Custom Labyrinth Graph (GM) structure without external libraries."""
from collections import deque
from typing import Optional
from src.features.labyrinth.domain.entities import VertexM, CorridorM


class GraphM:
    """Manages the lower labyrinth corridors where the convoy moves."""

    def __init__(self) -> None:
        self.vertices: dict[str, VertexM] = {}
        self.corridors: dict[str, CorridorM] = {}
        self.adj: dict[str, list[CorridorM]] = {}

    def add_vertex(self, vertex: VertexM) -> None:
        """Add a vertex to the labyrinth."""
        self.vertices[vertex.id] = vertex
        if vertex.id not in self.adj:
            self.adj[vertex.id] = []

    def add_corridor(self, corridor: CorridorM) -> None:
        """Add an undirected corridor connecting two labyrinth nodes."""
        if corridor.u not in self.vertices or corridor.v not in self.vertices:
            raise ValueError(f"Endpoints {corridor.u} / {corridor.v} must exist.")
        self.corridors[corridor.id] = corridor
        self.adj[corridor.u].append(corridor)
        self.adj[corridor.v].append(corridor)

    def get_entry(self) -> Optional[VertexM]:
        """Retrieve the designated entry vertex."""
        return next((v for v in self.vertices.values() if v.is_entry), None)

    def get_exit(self) -> Optional[VertexM]:
        """Retrieve the designated exit vertex."""
        return next((v for v in self.vertices.values() if v.is_exit), None)

    def verify_initial_path(self) -> bool:
        """Custom BFS to verify that a reachable path exists from entry to exit."""
        entry = self.get_entry()
        exit_v = self.get_exit()
        if not entry or not exit_v:
            return False

        visited: set[str] = {entry.id}
        queue: deque[str] = deque([entry.id])

        while queue:
            curr = queue.popleft()
            if curr == exit_v.id:
                return True
            for corridor in self.adj.get(curr, []):
                neighbor = corridor.v if corridor.u == curr else corridor.u
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return False

