"""Convoy: one compact formation that moves along GM and re-plans at each vertex."""
from typing import Optional
from src.features.labyrinth.application.danger import update_weights
from src.features.labyrinth.application.router import choose_next
from src.features.simulation.domain.world import World


class Convoy:
    """Shared position and route of all living machines."""

    def __init__(self, world: World) -> None:
        self.world = world
        self.graph_m = world.manager.graph_m
        self.entry = self.graph_m.get_entry()
        self.exit = self.graph_m.get_exit()
        self.vertex: Optional[str] = self.entry.id   # None while crossing a corridor
        self.previous: Optional[str] = None
        self.corridor = None
        self.from_v = self.to_v = ""
        self.progress = 0.0
        self.xy = tuple(self.entry.coords)
        self.decision: Optional[dict] = None         # last choice, shown in the UI

    def refresh_weights(self) -> dict[str, float]:
        """Recompute w(e) = t(e) + alpha * P(e) with the defenders active right now."""
        return update_weights(self.graph_m, self.world.armed_defenders(), self.world.manager.metadata.alpha)

    def at_exit(self) -> bool:
        return self.vertex == self.exit.id

    def update(self, dt: float) -> None:
        if not any(e.alive for e in self.world.enemies):
            return
        if self.corridor is None and not self.at_exit():
            self._decide()
        if self.corridor is None:
            return
        self.progress += self.corridor.speed_allowed * dt
        a, b = self.graph_m.vertices[self.from_v].coords, self.graph_m.vertices[self.to_v].coords
        k = min(1.0, self.progress / self.corridor.length)
        self.xy = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        if self.progress >= self.corridor.length:  # reached the next intersection
            self.previous, self.vertex, self.corridor = self.from_v, self.to_v, None
            if self.at_exit():
                self.world.log("convoy", f"El convoy llegó a la salida {self.vertex}.")

    def _decide(self) -> None:
        w = self.world
        weights = self.refresh_weights()
        decision = choose_next(self.graph_m, self.vertex, self.previous, self.exit.id, weights)
        if decision is None:
            return
        self.decision = {"at": self.vertex, "time": round(w.clock, 2), **decision}
        chosen = decision["chosen"]
        self.corridor = self.graph_m.corridors[chosen["corridor"]]
        self.from_v, self.to_v, self.progress, self.vertex = self.vertex, chosen["to"], 0.0, None
        w.log("convoy", f"En {self.from_v} el convoy toma {chosen['corridor']} hacia {self.to_v} "
                        f"(costo estimado {chosen['cost']:.1f}). {decision['note']}.")
