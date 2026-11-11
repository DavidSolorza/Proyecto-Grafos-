"""Danger estimation for labyrinth corridors: w(e) = t(e) + alpha * P(e)."""
from math import dist as euclid
from src.features.labyrinth.domain.graph_m import GraphM

# A defender as seen by the convoy: (x, y, effective range, damage, frequency)
Defender = tuple[float, float, float, float, float]


def damage_rate(point: tuple[float, float], defenders: list[Defender]) -> float:
    """D(q): sum of damage * frequency of every soldier that reaches point q."""
    return sum(d * f for x, y, ref, d, f in defenders if euclid((x, y), point) <= ref)


def update_weights(graph_m: GraphM, defenders: list[Defender], alpha: float) -> dict[str, float]:
    """Recompute danger P(e) and weight w(e) of every corridor; return {id: w}."""
    weights: dict[str, float] = {}
    for c in graph_m.corridors.values():
        a = graph_m.vertices[c.u].coords
        b = graph_m.vertices[c.v].coords
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        # Three sample points per corridor: start, middle and end
        rates = [damage_rate(p, defenders) for p in (a, mid, b)]
        potential = (sum(rates) / 3) * c.base_time      # P(e)
        c.current_danger = potential
        c.current_weight = c.base_time + alpha * potential
        weights[c.id] = c.current_weight
    return weights
