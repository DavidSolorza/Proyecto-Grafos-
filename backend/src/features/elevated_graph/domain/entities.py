"""Elevated Graph (GE) domain entities."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PositionType(str, Enum):
    """Position types for elevated graph vertices."""
    BASE = "BASE"
    CANDIDATE = "CANDIDATE"
    TRANSIT = "TRANSIT"
    HELIPORT = "HELIPORT"


@dataclass
class VertexE:
    """Vertex representing a terrain position in the elevated graph."""
    id: str
    coords: tuple[float, float]
    type: PositionType
    z: float = 0.0


@dataclass
class EdgeE:
    """Edge or bridge connecting two elevated positions."""
    id: str
    u: str
    v: str
    time_walk: Optional[float]           # None = walking is not allowed on this edge
    time_moto: Optional[float]           # None = motorcycles are not allowed on this edge
    bridge_max_hp: Optional[int] = None  # None = plain road: it never wears or collapses
    bridge_current_hp: Optional[int] = None
    is_destroyed: bool = False
    repair_timer: float = 0.0
    occupied_by_repair_units: int = 0    # people busy rebuilding it right now

    @property
    def is_bridge(self) -> bool:
        return self.bridge_max_hp is not None

    def time_for(self, mode: str) -> Optional[float]:
        """Crossing time with 'walk' or 'moto' (None when that transport is not allowed)."""
        return self.time_moto if mode == "moto" else self.time_walk

