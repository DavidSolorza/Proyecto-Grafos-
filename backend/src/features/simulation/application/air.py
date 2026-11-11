"""Air transport: helicopters carry up to 4 soldiers and spread the surplus."""
from math import dist as euclid
from src.core.errors.handlers import AppError
from src.features.simulation.domain.units import Flight, SoldierStatus
from src.features.simulation.domain.world import World

HELI_CAPACITY = 4


class AirTransport:
    """Authorizes flights and moves helicopters leg by leg."""

    def __init__(self, world: World) -> None:
        self.world = world
        cfg = world.manager.helicopter_config
        self.speed, self.cost, self.max_uses = float(cfg["speed"]), float(cfg["cost"]), int(cfg["max_uses"])
        self.uses = 0
        self.flights: list[Flight] = []

    def request(self, soldier_ids: list[str], dest: str) -> Flight:
        """Authorize a flight: helicopter, budget, soldiers present and valid positions."""
        w = self.world
        if self.uses >= self.max_uses:
            raise AppError("No quedan usos de helicóptero")
        if not soldier_ids or len(soldier_ids) > HELI_CAPACITY:
            raise AppError(f"Un helicóptero lleva de 1 a {HELI_CAPACITY} soldados")
        if any(sid not in w.soldiers for sid in soldier_ids) or len(set(soldier_ids)) != len(soldier_ids):
            raise AppError("Soldados inválidos")
        group = [w.soldiers[sid] for sid in soldier_ids]
        origin = group[0].vertex
        if any(s.vertex != origin or s.status not in (SoldierStatus.AT_BASE, SoldierStatus.STATIONED)
               for s in group):
            raise AppError("Los soldados deben estar presentes en el mismo punto de recogida")
        if dest not in w.towers or dest == origin:
            raise AppError("El destino debe ser una torre del plan distinta al origen")
        if w.budget.available < self.cost:
            raise AppError("Presupuesto insuficiente para el vuelo")

        # Authorized: reserve money, use the helicopter, take the soldiers on board
        w.budget.reserve(self.cost)
        self.uses += 1
        flight = Flight(f"H{self.uses}", list(soldier_ids), self.cost, w.coords(origin), w.coords(origin))
        for s in group:
            s.status = SoldierStatus.FLYING
        self._set_target(flight, dest)
        self.flights.append(flight)
        w.log("air", f"Helicóptero {flight.id} despega de {origin} hacia {dest} con {len(group)} soldado(s). "
                     f"Costo reservado: ${self.cost:.0f}.")
        return flight

    def _set_target(self, f: Flight, target: str) -> None:
        """Start a leg and reserve the free slots of the target tower."""
        w = self.world
        f.target, f.progress, f.from_xy = target, 0.0, f.xy
        f.visited.add(target)
        f.reserved = max(0, min(w.free_slots(target), len(f.aboard))) if target in w.towers else len(f.aboard)
        if target in w.towers:
            w.reserved[target] = w.reserved.get(target, 0) + f.reserved
        end = w.coords(target)
        f.duration = max(euclid(f.from_xy, end) / self.speed, 0.25)

    def update(self, dt: float) -> None:
        w = self.world
        for f in self.flights:
            if f.status != "FLYING":
                continue
            f.progress += dt
            a, b, k = f.from_xy, w.coords(f.target), min(1.0, f.progress / f.duration)
            f.xy = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
            for sid in f.aboard:
                w.soldiers[sid].xy = f.xy
            if f.progress >= f.duration:
                self._land(f)

    def _land(self, f: Flight) -> None:
        """Drop as many soldiers as the reservation allows, then route the surplus."""
        w = self.world
        is_tower = f.target in w.towers
        if is_tower:
            w.reserved[f.target] -= f.reserved
        dropped, f.aboard = f.aboard[:f.reserved], f.aboard[f.reserved:]
        for sid in dropped:
            s = w.soldiers[sid]
            s.vertex, s.xy = f.target, w.coords(f.target)
            s.status = SoldierStatus.STATIONED if is_tower else SoldierStatus.AT_BASE
            s.next_attack = w.clock + 0.25
        w.log("air", f"{f.id} aterrizó en {f.target}: bajan {len(dropped)}, quedan {len(f.aboard)} a bordo.")
        if not f.aboard:
            f.status = "DONE"
            w.budget.commit(f.cost)  # reserved money becomes spent
            return
        # Surplus: nearest enabled tower with free room (ties by id), else back to base
        options = sorted(
            (euclid(f.xy, t.xy), tid) for tid, t in w.towers.items()
            if tid not in f.visited and w.free_slots(tid) > 0
        )
        base = w.manager.graph_e.get_base_vertex().id
        self._set_target(f, options[0][1] if options else base)
        w.log("air", f"{f.id} lleva {len(f.aboard)} excedente(s) hacia {f.target}.")
