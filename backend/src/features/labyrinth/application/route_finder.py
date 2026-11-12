"""Minimum-cost route between two vertices of GM (Dijkstra with the own min-heap)."""
from typing import Optional

from src.core.structures.min_heap import MinHeap
from src.features.labyrinth.domain.graph_m import GraphM


def minimum_route(graph_m: GraphM, source: str, target: str,
                  weights: Optional[dict[str, float]] = None) -> Optional[dict]:
    """Cheapest route as {cost, vertices, corridors}; None when the target is unreachable.

    Without `weights` the cost of a corridor is its travel time t(e) = length / speed,
    which is the cost that applies before any danger is estimated.
    """
    if source not in graph_m.vertices or target not in graph_m.vertices:
        return None
    cost_of = (lambda c: weights[c.id]) if weights else (lambda c: c.base_time)
    best = {source: 0.0}
    came_from: dict = {}
    heap = MinHeap()
    heap.push((0.0, source))
    while heap:
        cost, cur = heap.pop()
        if cost > best.get(cur, float("inf")):
            continue                                  # stale heap entry
        if cur == target:
            break
        for corridor in graph_m.adj[cur]:
            nxt = corridor.v if corridor.u == cur else corridor.u
            new_cost = cost + cost_of(corridor)
            if new_cost < best.get(nxt, float("inf")):
                best[nxt], came_from[nxt] = new_cost, (cur, corridor)
                heap.push((new_cost, nxt))
    if target not in best:
        return None
    vertices, corridors, cur = [target], [], target
    while cur != source:
        cur, corridor = came_from[cur]
        corridors.append(corridor.id)
        vertices.append(cur)
    return {"cost": best[target], "vertices": vertices[::-1], "corridors": corridors[::-1]}
