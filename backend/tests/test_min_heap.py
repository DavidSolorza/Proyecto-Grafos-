"""The priority queue is ours (no heapq): check it alone and inside both Dijkstra searches."""
import random
import re

import pytest

from conftest import DOCS
from src.core.config.settings import settings
from src.core.structures.min_heap import MinHeap
from src.features.elevated_graph.application.ge_paths import edge_time, shortest_path
from src.features.elevated_graph.domain.entities import EdgeE, PositionType, VertexE
from src.features.elevated_graph.domain.graph_e import GraphE
from src.features.labyrinth.application.router import distances_to
from src.features.labyrinth.domain.entities import CorridorM, VertexM
from src.features.labyrinth.domain.graph_m import GraphM


def test_pops_in_ascending_order_like_sorted():
    rng = random.Random(7)
    values = [rng.randint(0, 50) for _ in range(500)]        # many repeated values
    heap = MinHeap()
    for v in values:
        heap.push(v)
    assert len(heap) == 500
    assert [heap.pop() for _ in range(500)] == sorted(values)
    assert not heap and len(heap) == 0


def test_ties_are_broken_by_the_second_element():
    heap = MinHeap()
    for entry in [(2.0, "b"), (1.0, "z"), (2.0, "a"), (1.0, "c"), (0.5, "m")]:
        heap.push(entry)
    assert [heap.pop() for _ in range(5)] == [(0.5, "m"), (1.0, "c"), (1.0, "z"), (2.0, "a"), (2.0, "b")]


def test_peek_does_not_remove_and_empty_heap_raises():
    heap = MinHeap()
    with pytest.raises(IndexError):
        heap.pop()
    with pytest.raises(IndexError):
        heap.peek()
    heap.push(5)
    heap.push(3)
    assert heap.peek() == 3 and len(heap) == 2


def test_mixing_pushes_and_pops_keeps_the_heap_property():
    """Interleaved operations (what Dijkstra does) against a sorted-list oracle."""
    rng = random.Random(11)
    heap, oracle = MinHeap(), []
    for _ in range(2000):
        if oracle and rng.random() < 0.4:
            oracle.sort()
            assert heap.pop() == oracle.pop(0)
        else:
            x = (rng.randint(0, 30), rng.choice("abcdef"))
            heap.push(x)
            oracle.append(x)
        assert len(heap) == len(oracle)


def test_the_source_code_does_not_use_heapq():
    """Requirement: the priority queue is written by us."""
    offenders = [p.name for p in (settings.ROOT_PROJECT_DIR / "backend" / "src").rglob("*.py")
                 if re.search(r"\bheapq\b", p.read_text(encoding="utf-8"))]
    assert offenders == []


# ---- Dijkstra with the new heap against an independent oracle (Bellman-Ford) ----------------

def _random_ge(rng, n):
    g = GraphE()
    for i in range(n):
        g.add_vertex(VertexE(f"v{i}", (i + 1.0, 1.0), PositionType.TRANSIT))
    for i in range(1, n):                                    # a chain keeps most nodes connected...
        if rng.random() < 0.85:
            _add_ge_edge(g, rng, f"c{i}", f"v{i - 1}", f"v{i}")
    for k in range(n * 2):                                   # ...and random extras create cycles
        a, b = rng.sample(range(n), 2)
        _add_ge_edge(g, rng, f"x{k}", f"v{a}", f"v{b}")
    return g


def _add_ge_edge(g, rng, eid, u, v):
    edge = EdgeE(eid, u, v, rng.randint(1, 9), rng.randint(1, 5))
    edge.is_destroyed = rng.random() < 0.15                  # collapsed bridges must be ignored
    g.add_edge(edge)


def _bellman_ford(vertices, links, src):
    """links: (u, v, cost) undirected. Independent of any priority queue."""
    dist = {v: float("inf") for v in vertices}
    dist[src] = 0.0
    for _ in range(len(vertices)):
        for u, v, c in links:
            if dist[u] + c < dist[v]:
                dist[v] = dist[u] + c
            if dist[v] + c < dist[u]:
                dist[u] = dist[v] + c
    return dist


@pytest.mark.parametrize("mode", ["walk", "moto"])
def test_ge_dijkstra_matches_bellman_ford_on_random_graphs(mode):
    rng = random.Random(3)
    for _ in range(40):
        g = _random_ge(rng, rng.randint(3, 12))
        links = [(e.u, e.v, edge_time(e, mode)) for e in g.edges.values() if not e.is_destroyed]
        oracle = _bellman_ford(list(g.vertices), links, "v0")
        for dst in g.vertices:
            found = shortest_path(g, "v0", dst, mode)
            if oracle[dst] == float("inf"):
                assert found is None
            else:
                cost, vertices, edges = found
                assert cost == oracle[dst] and vertices[0] == "v0" and vertices[-1] == dst
                assert sum(edge_time(e, mode) for e in edges) == cost
                assert not any(e.is_destroyed for e in edges)


def test_gm_dijkstra_matches_bellman_ford_on_random_graphs():
    rng = random.Random(5)
    for _ in range(40):
        n = rng.randint(3, 12)
        g = GraphM()
        for i in range(n):
            g.add_vertex(VertexM(f"m{i}", (float(i), 0.0)))
        weights = {}
        for k in range(n * 2):
            a, b = rng.sample(range(n), 2)
            c = CorridorM(f"k{k}", f"m{a}", f"m{b}", 10.0, 1.0)
            g.add_corridor(c)
            weights[c.id] = rng.choice([0.5, 1, 2, 2, 3.5, 7])        # repeated weights = ties
        links = [(c.u, c.v, weights[c.id]) for c in g.corridors.values()]
        banned = rng.choice([None, f"m{rng.randint(1, n - 1)}"])
        usable = [l for l in links if banned not in l[:2]]
        oracle = _bellman_ford([v for v in g.vertices if v != banned], usable, "m0")
        got = distances_to(g, "m0", weights, banned=banned)
        assert {v: d for v, d in oracle.items() if d != float("inf")} == got


def test_scenario_files_still_give_the_known_paths():
    from src.features.scenario.application.loader import ScenarioLoader
    manager = ScenarioLoader.load_from_file(DOCS / "escenario_complejo.json")
    assert shortest_path(manager.graph_e, "V_BASE", "V_ISLA", "walk") is None   # isolated vertex
    assert shortest_path(manager.graph_e, "V_BASE", "V_C4", "walk") is not None
