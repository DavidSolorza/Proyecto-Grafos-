"""Simulation engine: logical clock that coordinates every component."""
from src.core.errors.handlers import AppError
from src.features.simulation.application.air import AirTransport
from src.features.simulation.application.bridges import BridgeManager
from src.features.simulation.application.combat import CombatResolver
from src.features.simulation.application.convoy import Convoy
from src.features.simulation.application.ground import GroundTransport
from src.features.simulation.domain.entities import EnemyType, SimState, SoldierType
from src.features.simulation.domain.units import ENEMY_STATS, Enemy, Soldier
from src.features.simulation.domain.world import STEP, Budget, Tower, World

FINISHED = (SimState.VICTORY_ELIMINATION, SimState.VICTORY_RESISTANCE, SimState.DEFEAT)
CONVOY_KEYS = {"tanks": EnemyType.TANK, "trucks": EnemyType.TRUCK,
               "robot_soldiers": EnemyType.ROBOT_SOLDIER}


class Simulation:
    """One match: built from a scenario and the towers chosen by the plan."""

    def __init__(self, manager, plan: dict) -> None:
        graph_e = manager.graph_e
        towers = {t["vertex_id"]: Tower(t["vertex_id"], t["rv"], graph_e.vertices[t["vertex_id"]].z,
                                        tuple(graph_e.vertices[t["vertex_id"]].coords))
                  for t in plan["towers"]}
        self.world = World(manager, towers, Budget(manager.metadata.initial_budget))
        self.bridges = BridgeManager(self.world)
        self.ground = GroundTransport(self.world, self.bridges)
        self.air = AirTransport(self.world)
        self.combat = CombatResolver(self.world)
        self.convoy = Convoy(self.world)
        self._soldier_counter = 0
        for key, kind in CONVOY_KEYS.items():
            hp, reward = ENEMY_STATS[kind]
            for i in range(int(manager.convoy_config.get(key, 0))):
                self.world.enemies.append(Enemy(f"{kind.value}-{i + 1}", kind, hp, hp, reward))
        self.world.log("system", "Simulación lista. Compra soldados y envíalos a las torres antes de iniciar.")

    def recruit(self, kind: str, count: int) -> list[str]:
        """Buy soldiers; they appear at the base. Never leaves a negative budget."""
        w = self.world
        cfg = w.manager.defenders_config.get(kind.lower())
        if cfg is None or kind.upper() not in SoldierType.__members__:
            raise AppError("Tipo de soldado inválido")
        if count < 1 or count > 20:
            raise AppError("Cantidad inválida")
        total = cfg["cost"] * count
        if w.budget.available < total:
            raise AppError(f"Presupuesto insuficiente: cuesta ${total} y hay ${w.budget.available:.0f}")
        base = w.manager.graph_e.get_base_vertex()
        w.budget.spend(total)
        ids = []
        for _ in range(count):
            self._soldier_counter += 1
            s = Soldier(f"S{self._soldier_counter}", SoldierType[kind.upper()], cfg["damage"],
                        cfg["base_range"], cfg["frequency"], base.id, tuple(base.coords))
            w.soldiers[s.id] = s
            ids.append(s.id)
        w.log("buy", f"Compraste {count} × {kind} por ${total}. Aparecen en la base ({', '.join(ids)}).")
        return ids

    def tick(self, dt: float) -> None:
        """Advance the logical clock by dt seconds, in internal steps of STEP."""
        w = self.world
        if w.status in FINISHED:
            return
        if w.status == SimState.IDLE:
            w.log("system", "¡Comienza el enfrentamiento! Las torres ya no se pueden reubicar.")
        w.status = SimState.RUNNING
        for _ in range(max(1, round(dt / STEP))):
            self._step()
            if w.status in FINISHED:
                break

    def _step(self) -> None:
        w = self.world
        w.clock += STEP
        self.bridges.update(STEP)
        self.air.update(STEP)
        self.ground.update(STEP)
        self.convoy.update(STEP)
        self.combat.update(self.convoy.xy)
        # Same-instant priority: attacks, then machines at the exit, then time limit
        if not any(e.alive for e in w.enemies):
            self._finish(SimState.VICTORY_ELIMINATION, "Todas las máquinas fueron destruidas.")
        elif self.convoy.at_exit():
            self._finish(SimState.DEFEAT, "Una máquina viva llegó a la salida.")
        elif w.clock >= w.manager.metadata.time_limit:
            self._finish(SimState.VICTORY_RESISTANCE, f"Se resistió {w.manager.metadata.time_limit:.0f}s sin llegada enemiga.")

    def _finish(self, state: SimState, reason: str) -> None:
        self.world.status, self.world.end_reason = state, reason
        self.world.log("end", reason)
