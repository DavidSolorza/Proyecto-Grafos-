"""Ground transport: soldiers walking or riding motorcycles along GE."""
from src.core.errors.handlers import AppError
from src.features.elevated_graph.application.ge_paths import shortest_path, edge_time
from src.features.simulation.application.bridges import BridgeManager
from src.features.simulation.domain.units import SoldierStatus, Transfer
from src.features.simulation.domain.world import World

MOVABLE = (SoldierStatus.AT_BASE, SoldierStatus.STATIONED)


class GroundTransport:
    """Validates requests and advances every active transfer."""

    def __init__(self, world: World, bridges: BridgeManager) -> None:
        self.world = world
        self.bridges = bridges
        self.transfers: list[Transfer] = []
        self._counter = 0

    def request(self, soldier_ids: list[str], dest: str, mode: str) -> Transfer:
        """Check everything first; the state is modified only if all checks pass."""
        w = self.world
        graph = w.manager.graph_e
        if mode not in ("walk", "moto"):
            raise AppError("Medio de transporte inválido (walk o moto)")
        if not soldier_ids or len(set(soldier_ids)) != len(soldier_ids):
            raise AppError("Selecciona al menos un soldado (sin repetir)")
        if any(sid not in w.soldiers for sid in soldier_ids):
            raise AppError("Algún soldado no existe")
        group = [w.soldiers[sid] for sid in soldier_ids]
        origin = group[0].vertex
        if any(s.vertex != origin for s in group):
            raise AppError("Los soldados deben estar en el mismo origen")
        if any(s.status not in MOVABLE for s in group):
            raise AppError("Algún soldado está ocupado (en tránsito o reconstruyendo un puente) y no puede recibir órdenes")
        if len(group) > (2 if mode == "moto" else 1):
            raise AppError("A pie va 1 soldado; en moto pueden ir 1 o 2")
        if dest not in graph.vertices:
            raise AppError("El destino no existe")
        if dest != w.manager.graph_e.get_base_vertex().id and dest not in w.towers:
            raise AppError("El destino debe ser una torre del plan o la base")
        if dest == origin:
            raise AppError("El origen y el destino son el mismo vértice")
        if dest in w.towers and w.free_slots(dest) < len(group):
            raise AppError(f"La torre {dest} no tiene capacidad libre (ocupantes + reservas)")
        route = shortest_path(graph, origin, dest, mode)
        if route is None:
            raise AppError("No existe una ruta válida (puentes destruidos o desconectado)")

        # All checks passed: now change the state
        self._counter += 1
        _, vertices, edges = route
        t = Transfer(f"T{self._counter}", soldier_ids, mode, dest, vertices, edges)
        if dest in w.towers:
            w.reserved[dest] = w.reserved.get(dest, 0) + len(group)
        for s in group:
            s.status = SoldierStatus.MOVING
        self.transfers.append(t)
        total = sum(edge_time(e, mode) for e in edges)
        w.log("move", f"{', '.join(soldier_ids)} salen de {origin} hacia {dest} "
                      f"({'moto' if mode == 'moto' else 'a pie'}, ruta {' → '.join(vertices)}, {total:.0f}s).")
        return t

    def update(self, dt: float) -> None:
        for t in self.transfers:
            if t.status != "DONE":
                self._advance(t, dt)

    def _advance(self, t: Transfer, dt: float) -> None:
        w = self.world
        if t.status == "WAITING":
            if t.seen_version == w.version or not self._replan(t):
                return  # nothing changed in connectivity, keep waiting
        if not t.on_edge and not self._start_edge(t):
            return
        t.progress += dt
        self._place(t)
        if t.progress >= t.duration:
            self._finish_edge(t)

    def _start_edge(self, t: Transfer) -> bool:
        edge = t.edges[t.index]
        if edge.is_destroyed:  # collapsed before entering: search again from here
            if not self._replan(t):
                return False
            edge = t.edges[t.index]
        t.on_edge, t.progress, t.duration = True, 0.0, edge_time(edge, t.mode)
        return True

    def _replan(self, t: Transfer) -> bool:
        w = self.world
        here = t.vertices[t.index]
        route = shortest_path(w.manager.graph_e, here, t.dest, t.mode)
        if route is None:
            t.status, t.seen_version = "WAITING", w.version
            for sid in t.soldier_ids:
                w.soldiers[sid].status = SoldierStatus.WAITING
            w.log("move", f"{', '.join(t.soldier_ids)} quedan detenidos en {here}: no hay ruta a {t.dest}.")
            return False
        _, t.vertices, t.edges = route
        t.index, t.status = 0, "MOVING"
        for sid in t.soldier_ids:
            w.soldiers[sid].status = SoldierStatus.MOVING
        return True

    def _place(self, t: Transfer) -> None:
        """Interpolate the position of the soldiers along the current edge."""
        a, b = self.world.coords(t.vertices[t.index]), self.world.coords(t.vertices[t.index + 1])
        f = min(1.0, t.progress / t.duration)
        for sid in t.soldier_ids:
            self.world.soldiers[sid].xy = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)

    def _finish_edge(self, t: Transfer) -> None:
        w = self.world
        edge = t.edges[t.index]
        t.on_edge = False
        t.index += 1
        if t.mode == "moto":
            self.bridges.wear(edge)  # only motorcycles wear the bridge, once per crossing
        here = t.vertices[t.index]
        for sid in t.soldier_ids:
            w.soldiers[sid].vertex, w.soldiers[sid].xy = here, w.coords(here)
        if t.index < len(t.edges):
            return
        t.status = "DONE"
        if t.dest in w.towers:
            w.reserved[t.dest] -= len(t.soldier_ids)
        for sid in t.soldier_ids:
            s = w.soldiers[sid]
            s.status = SoldierStatus.STATIONED if t.dest in w.towers else SoldierStatus.AT_BASE
            s.next_attack = w.clock + 0.25  # may attack from the next combat update
        w.log("move", f"{', '.join(t.soldier_ids)} llegaron a {t.dest}.")
