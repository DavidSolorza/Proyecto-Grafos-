"""Reactive navigation for the convoy (Dijkstra written from scratch)."""
from typing import Optional
from src.core.structures.min_heap import MinHeap
from src.features.labyrinth.domain.graph_m import GraphM


def distances_to(graph_m: GraphM, target: str, weights: dict[str, float],
                 banned: Optional[str] = None) -> dict[str, float]:
    """Dijkstra from the exit. The graph is undirected, so it works for any start.

    `banned` is a vertex the routes may not pass through (used so that a route
    never comes back to the vertex where the decision is being made).
    """
    best = {target: 0.0}
    heap = MinHeap()
    heap.push((0.0, target))
    while heap:
        cost, cur = heap.pop()
        if cost > best.get(cur, float("inf")):
            continue
        for c in graph_m.adj[cur]:
            nxt = c.v if c.u == cur else c.u
            if nxt == banned:
                continue
            new_cost = cost + weights[c.id]
            if new_cost < best.get(nxt, float("inf")):
                best[nxt] = new_cost
                heap.push((new_cost, nxt))
    return best


def choose_next(graph_m: GraphM, current: str, previous: Optional[str],
                exit_id: str, weights: dict[str, float]) -> Optional[dict]:
    """Pick the first corridor of the best route from `current` to the exit.

    Returns the decision with every option, so the UI can explain the choice.
    If the best route goes back to `previous`, a different first move is
    preferred when one exists; otherwise going back is allowed.
    """
    # Routes are simple paths: they never pass again through `current`
    dist = distances_to(graph_m, exit_id, weights, banned=current)
    options = []
    for c in graph_m.adj[current]:
        nxt = c.v if c.u == current else c.u
        if nxt in dist:
            options.append({"corridor": c.id, "to": nxt,
                            "cost": weights[c.id] + dist[nxt]})
    if not options:
        return None

    options.sort(key=lambda o: (round(o["cost"], 9), o["corridor"]))
    best, note = options[0], "Mejor ruta hacia la salida"
    if best["to"] == previous:
        others = [o for o in options if o["to"] != previous]
        if others:
            best, note = others[0], "Evita retroceder: existe otra ruta con primer paso distinto"
        else:
            note = "Retrocede: no hay otra ruta posible"
    return {"chosen": best, "options": options, "note": note}
