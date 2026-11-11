"""World: the shared state every simulation component reads and writes."""
from dataclasses import dataclass, field
from src.features.simulation.domain.entities import SimState
from src.features.simulation.domain.units import Soldier, SoldierStatus, Enemy

STEP = 0.25          # logical seconds per internal step
TOWER_CAPACITY = 3   # max soldiers per tower (occupants + reservations)


@dataclass
class Budget:
    """Money split in available / reserved (pending flights) / spent."""
    available: float
    reserved: float = 0.0
    spent: float = 0.0
    earned: float = 0.0

    def spend(self, amount: float) -> None:
        self.available -= amount
        self.spent += amount

    def reserve(self, amount: float) -> None:
        self.available -= amount
        self.reserved += amount

    def commit(self, amount: float) -> None:
        self.reserved -= amount
        self.spent += amount

    def earn(self, amount: float) -> None:
        self.available += amount
        self.earned += amount


@dataclass
class Tower:
    """A tower chosen by the defense plan."""
    vertex_id: str
    rv: float
    z: float
    xy: tuple[float, float]


@dataclass
class World:
    """Everything that changes while the simulation runs."""
    manager: object
    towers: dict[str, Tower]
    budget: Budget
    clock: float = 0.0
    status: SimState = SimState.IDLE
    end_reason: str = ""
    version: int = 0                                  # bumps when bridges collapse / return
    soldiers: dict[str, Soldier] = field(default_factory=dict)
    enemies: list[Enemy] = field(default_factory=list)
    reserved: dict[str, int] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)

    def log(self, kind: str, text: str) -> None:
        """Record what happened (the UI shows it, so the user knows why)."""
        self.events.append({"t": round(self.clock, 2), "kind": kind, "text": text})
        del self.events[:-150]

    def coords(self, vertex_id: str) -> tuple[float, float]:
        return tuple(self.manager.graph_e.vertices[vertex_id].coords)

    def occupants(self, vertex_id: str) -> int:
        return sum(1 for s in self.soldiers.values()
                   if s.status == SoldierStatus.STATIONED and s.vertex == vertex_id)

    def free_slots(self, vertex_id: str) -> int:
        """Capacity left = 3 - present soldiers - confirmed reservations."""
        return TOWER_CAPACITY - self.occupants(vertex_id) - self.reserved.get(vertex_id, 0)

    def effective_range(self, soldier: Soldier) -> float:
        """R_ef = R_base * (1 + beta * z) using the height of the tower."""
        z = self.towers[soldier.vertex].z
        return soldier.base_range * (1 + self.manager.metadata.beta * z)

    def armed_defenders(self) -> list[tuple]:
        """Stationed soldiers as (x, y, R_ef, damage, frequency) for danger estimates."""
        return [(*s.xy, self.effective_range(s), s.damage, s.frequency)
                for s in self.soldiers.values() if s.status == SoldierStatus.STATIONED]
