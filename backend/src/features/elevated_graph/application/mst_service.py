"""Custom Kruskal MST over the connected component that contains the base."""
from collections import deque
from dataclasses import dataclass
from src.features.elevated_graph.domain.entities import EdgeE
from src.features.elevated_graph.domain.graph_e import GraphE
from src.features.elevated_graph.application.disjoint_set import DisjointSet


@dataclass
class MstResult:
    """Tree T_E plus the walking distance D_T(B, p) from the base to every vertex."""
    edges: list[EdgeE]
    vertices: set[str]
    total_time: float
    dist_from_base: dict[str, float]


def build_mst(graph: GraphE, base_id: str) -> MstResult:
    """Kruskal using walking time as weight.

    Tie-break: edges with the same time are sorted by id, so the result is
    always the same for the same scenario.
    """
    component = graph.get_connected_component(base_id, walkable_only=True)  # the tree is walked
    usable = [
        e for e in graph.edges.values()
        if e.u in component and e.v in component and not e.is_destroyed
        and e.time_walk is not None
    ]
    usable.sort(key=lambda e: (e.time_walk, e.id))

    sets = DisjointSet(component)
    tree = [e for e in usable if sets.union(e.u, e.v)]
    return MstResult(
        edges=tree,
        vertices=component,
        total_time=sum(e.time_walk for e in tree),
        dist_from_base=_distances_on_tree(tree, component, base_id),
    )


def _distances_on_tree(tree: list[EdgeE], vertices: set[str], base_id: str) -> dict[str, float]:
    """BFS over the tree edges only, summing walking times from the base."""
    adj: dict[str, list[tuple[str, float]]] = {v: [] for v in vertices}
    for e in tree:
        adj[e.u].append((e.v, e.time_walk))
        adj[e.v].append((e.u, e.time_walk))

    dist = {base_id: 0.0}
    queue: deque[str] = deque([base_id])
    while queue:
        cur = queue.popleft()
        for nxt, w in adj[cur]:
            if nxt not in dist:  # in a tree there is exactly one way to reach it
                dist[nxt] = dist[cur] + w
                queue.append(nxt)
    return dist
