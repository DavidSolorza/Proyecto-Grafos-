"""Elevated Graph (GE) domain entities."""
from dataclasses import dataclass, field
from enum import Enum


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
    time_walk: float
    time_moto: float
    bridge_max_hp: int = 10
    bridge_current_hp: int = 10
    is_destroyed: bool = False
    repair_timer: float = 0.0
    occupied_by_repair_units: int = 0

