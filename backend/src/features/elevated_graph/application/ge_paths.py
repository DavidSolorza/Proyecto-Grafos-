"""Dijkstra on the elevated graph (walking or motorcycle time)."""
from typing import Optional
from src.core.structures.min_heap import MinHeap
from src.features.elevated_graph.domain.entities import EdgeE
from src.features.elevated_graph.domain.graph_e import GraphE


def edge_time(edge: EdgeE, mode: str) -> Optional[float]:
    """Time to cross an edge with the given transport ('walk' or 'moto'); None if not allowed."""
    return edge.time_for(mode)


def shortest_path(graph: GraphE, src: str, dst: str, mode: str
                  ) -> Optional[tuple[float, list[str], list[EdgeE]]]:
    """Cheapest route as (total time, vertex ids, edges). None if unreachable.

    Destroyed bridges are skipped, so a collapse changes later searches.
    """
    if src not in graph.vertices or dst not in graph.vertices:
        return None

    best: dict[str, float] = {src: 0.0}
    came_from: dict[str, tuple[str, EdgeE]] = {}
    heap = MinHeap()
    heap.push((0.0, src))

    while heap:
        cost, cur = heap.pop()
        if cost > best.get(cur, float("inf")):
            continue  # stale heap entry
        if cur == dst:
            break
        for edge in graph.adj[cur]:
            step = edge_time(edge, mode)
            if edge.is_destroyed or step is None:
                continue  # collapsed bridge, or this transport may not use the edge
            nxt = edge.v if edge.u == cur else edge.u
            new_cost = cost + step
            if new_cost < best.get(nxt, float("inf")):
                best[nxt] = new_cost
                came_from[nxt] = (cur, edge)
                heap.push((new_cost, nxt))

    if dst not in best:
        return None

    vertices, edges, cur = [dst], [], dst
    while cur != src:
        cur, edge = came_from[cur][0], came_from[cur][1]
        edges.append(edge)
        vertices.append(cur)
    return best[dst], vertices[::-1], edges[::-1]
