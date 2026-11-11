"""Simulation entities: defender soldiers, enemy machines, transport operations."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from src.features.elevated_graph.domain.entities import EdgeE
from src.features.simulation.domain.entities import EnemyType, SoldierType

# Max HP and reward per machine type (section 6 of the statement)
ENEMY_STATS = {
    EnemyType.TANK: (200, 150),
    EnemyType.TRUCK: (100, 100),
    EnemyType.ROBOT_SOLDIER: (50, 50),
}


class SoldierStatus(str, Enum):
    """Where a soldier is and what it is doing."""
    AT_BASE = "AT_BASE"
    STATIONED = "STATIONED"   # inside a tower, able to attack
    MOVING = "MOVING"         # walking or riding a motorcycle
    WAITING = "WAITING"       # stopped because no route exists
    FLYING = "FLYING"         # aboard a helicopter
    REPAIRING = "REPAIRING"   # at the base, busy rebuilding a bridge


@dataclass
class Soldier:
    """A defender bought with the budget."""
    id: str
    type: SoldierType
    damage: float
    base_range: float
    frequency: float
    vertex: str                       # last vertex where it stood
    xy: tuple[float, float] = (0.0, 0.0)
    status: SoldierStatus = SoldierStatus.AT_BASE
    next_attack: float = 0.0


@dataclass
class Enemy:
    """One machine of the convoy. Position is shared by the whole formation."""
    id: str
    type: EnemyType
    max_hp: float
    hp: float
    reward: int

    @property
    def alive(self) -> bool:
        return self.hp > 0


@dataclass
class Transfer:
    """Ground movement of 1 soldier (walking) or 1-2 soldiers (motorcycle)."""
    id: str
    soldier_ids: list[str]
    mode: str                          # "walk" | "moto"
    dest: str
    vertices: list[str]                # planned route
    edges: list[EdgeE]
    index: int = 0                     # route[index] = last vertex reached
    progress: float = 0.0              # seconds spent on the current edge
    duration: float = 0.0
    on_edge: bool = False
    status: str = "MOVING"             # MOVING | WAITING | DONE
    seen_version: int = 0              # connectivity version when it got blocked


@dataclass
class Flight:
    """Helicopter operation: main leg, surplus legs and return to base."""
    id: str
    aboard: list[str]
    cost: float
    origin_xy: tuple[float, float]
    xy: tuple[float, float]
    target: str = ""
    reserved: int = 0                  # slots reserved at the current target
    progress: float = 0.0
    duration: float = 0.0
    from_xy: tuple[float, float] = (0.0, 0.0)
    visited: set = field(default_factory=set)
    status: str = "FLYING"             # FLYING | DONE
