"""Dynamic bridges: wear when a motorcycle crosses, collapse, timed repair by a crew of N people."""
from src.features.elevated_graph.domain.entities import EdgeE
from src.features.simulation.domain.units import SoldierStatus
from src.features.simulation.domain.world import World


class BridgeManager:
    """Keeps bridge health, the repair timers and the crews busy with repairs.

    A repair needs `bridge_repair_crew` (N) soldiers waiting at the base. While it
    lasts they are occupied: they cannot attack, move or board a helicopter. If
    fewer than N are free, the repair waits (its timer does not run) until they are.
    """

    def __init__(self, world: World) -> None:
        self.world = world
        self.crews: dict[str, list[str]] = {}   # edge id -> soldiers rebuilding it
        self.waiting: set[str] = set()          # destroyed edges still without a crew

    def wear(self, edge: EdgeE) -> None:
        """A motorcycle finished crossing: -1 HP. At 0 the bridge collapses. Plain roads never wear."""
        if edge.is_destroyed or not edge.is_bridge:
            return
        edge.bridge_current_hp -= 1
        w = self.world
        if edge.bridge_current_hp <= 0:
            edge.bridge_current_hp = 0
            edge.is_destroyed = True
            edge.repair_timer = w.manager.metadata.bridge_repair_time
            w.version += 1  # connectivity changed: blocked soldiers will retry
            need = w.manager.metadata.bridge_repair_crew
            w.log("bridge", f"El puente {edge.id} ({edge.u}-{edge.v}) colapsó. Reconstrucción: "
                            f"{edge.repair_timer:.0f}s" + (f" con {need} persona(s) de la base." if need else "."))

    def update(self, dt: float) -> None:
        """Hire crews, count down repairs and enable bridges again."""
        for edge in self.world.manager.graph_e.edges.values():
            if not edge.is_destroyed or (edge.id not in self.crews and not self._hire(edge)):
                continue
            edge.repair_timer -= dt
            if edge.repair_timer <= 0:
                self._rebuild(edge)

    def _hire(self, edge: EdgeE) -> bool:
        """Take N free soldiers from the base. False (and wait) if there are not enough."""
        w = self.world
        need = w.manager.metadata.bridge_repair_crew
        free = sorted(s.id for s in w.soldiers.values() if s.status == SoldierStatus.AT_BASE)
        if len(free) < need:
            if edge.id not in self.waiting:
                self.waiting.add(edge.id)
                w.log("bridge", f"La reconstrucción de {edge.id} espera: necesita {need} persona(s) "
                                f"en la base y hay {len(free)}.")
            return False
        crew = free[:need]
        for sid in crew:
            w.soldiers[sid].status = SoldierStatus.REPAIRING
        self.crews[edge.id] = crew
        self.waiting.discard(edge.id)
        edge.occupied_by_repair_units = need
        if need:
            w.log("bridge", f"{', '.join(crew)} empiezan a reconstruir {edge.id} y quedan ocupados.")
        return True

    def _rebuild(self, edge: EdgeE) -> None:
        w = self.world
        edge.repair_timer, edge.is_destroyed = 0.0, False
        edge.bridge_current_hp = edge.bridge_max_hp
        edge.occupied_by_repair_units = 0
        for sid in self.crews.pop(edge.id):
            w.soldiers[sid].status = SoldierStatus.AT_BASE   # the crew is free again
        w.version += 1
        w.log("bridge", f"El puente {edge.id} fue reconstruido y vuelve a estar habilitado.")
