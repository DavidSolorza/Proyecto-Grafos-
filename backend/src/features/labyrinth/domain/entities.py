"""Labyrinth Graph (GM) domain entities."""
from dataclasses import dataclass


@dataclass
class VertexM:
    """Vertex representing a node in the lower labyrinth."""
    id: str
    coords: tuple[float, float]
    is_entry: bool = False
    is_exit: bool = False


@dataclass
class CorridorM:
    """Corridor connecting nodes in the lower labyrinth."""
    id: str
    u: str
    v: str
    length: float
    speed_allowed: float
    current_danger: float = 0.0
    current_weight: float = 0.0

    @property
    def base_time(self) -> float:
        """Calculate base transit time t(e) = length / speed."""
        if self.speed_allowed <= 0:
            return float("inf")
        return self.length / self.speed_allowed

