"""Combat resolver: each stationed soldier attacks when its cooldown is over."""
from math import dist as euclid
from src.features.simulation.domain.entities import SoldierType
from src.features.simulation.domain.units import SoldierStatus
from src.features.simulation.domain.world import World


class CombatResolver:
    """Applies attacks of soldiers inside towers to the convoy."""

    def __init__(self, world: World) -> None:
        self.world = world

    def update(self, convoy_xy: tuple[float, float]) -> None:
        w = self.world
        for sid in sorted(w.soldiers):  # fixed order keeps the simulation deterministic
            s = w.soldiers[sid]
            if s.status != SoldierStatus.STATIONED or w.clock < s.next_attack:
                continue
            alive = [e for e in w.enemies if e.alive]
            in_range = [e for e in alive if euclid(s.xy, convoy_xy) <= w.effective_range(s)]
            if not in_range:
                continue  # nobody to shoot: keep the weapon ready
            if s.type == SoldierType.GUNNER:
                targets = in_range                                    # area damage
            else:
                targets = [min(in_range, key=lambda e: (e.hp, e.id))]  # weakest first
            for e in targets:
                self._hit(s, e)
            s.next_attack = w.clock + 1 / s.frequency

    def _hit(self, soldier, enemy) -> None:
        w = self.world
        enemy.hp = max(0.0, enemy.hp - soldier.damage)
        msg = f"{soldier.id} ({soldier.type.value}) golpea a {enemy.id}: -{soldier.damage:.0f} HP → {enemy.hp:.0f}."
        if not enemy.alive:  # a reward is given only once because the unit dies only once
            w.budget.earn(enemy.reward)
            msg += f" ¡Destruido! +${enemy.reward}."
        w.log("combat", msg)
