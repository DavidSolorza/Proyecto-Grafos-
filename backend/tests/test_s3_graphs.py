"""Section 3: representation of GE and GM."""
from itertools import permutations

from conftest import load, match, slow_convoy
from src.features.labyrinth.application.router import distances_to
from src.features.simulation.domain.units import ENEMY_STATS  # noqa: F401  (import sanity)


def test_ge_edges_are_undirected_and_keep_identity():
    manager = load()
    g = manager.graph_e
    for e in g.edges.values():
        assert e in g.adj[e.u] and e in g.adj[e.v]          # stored at both ends
    assert set(g.edges) == {"E_E1", "E_E2", "E_E3", "E_E4"}


def test_exactly_one_base_and_base_component():
    g = load("escenario_complejo.json").graph_e
    assert sum(1 for v in g.vertices.values() if v.type.value == "BASE") == 1
    comp = g.get_connected_component(g.get_base_vertex().id)
    assert "V_ISLA" not in comp and len(comp) == 8


def test_destroyed_bridge_keeps_its_data_and_disappears_from_searches():
    sim, manager = match()
    e = manager.graph_e.edges["E_E2"]
    before = (e.id, e.u, e.v, e.time_walk, e.time_moto, e.bridge_max_hp)
    e.is_destroyed = True
    assert (e.id, e.u, e.v, e.time_walk, e.time_moto, e.bridge_max_hp) == before
    assert "V_C1" not in manager.graph_e.get_connected_component("V_BASE")  # BFS ignores it
    e.is_destroyed = False
    assert "V_C1" in manager.graph_e.get_connected_component("V_BASE")


def test_corridor_time_is_length_over_speed():
    g = load().graph_m
    assert g.corridors["M_C1"].base_time == 40.0 / 5.0
    assert g.corridors["M_C2"].base_time == 35.0 / 5.0


def test_initial_path_exists_and_is_the_cheapest_one():
    """Dijkstra from the exit must equal a brute-force search over every simple path."""
    g = load("escenario_complejo.json").graph_m
    weights = {c.id: c.base_time for c in g.corridors.values()}
    entry, exit_ = g.get_entry().id, g.get_exit().id

    def cost_of(path):
        total = 0.0
        for a, b in zip(path, path[1:]):
            edge = [c for c in g.adj[a] if {c.u, c.v} == {a, b}]
            if not edge:
                return None
            total += weights[edge[0].id]
        return total

    middle = [v for v in g.vertices if v not in (entry, exit_)]
    best = float("inf")
    for r in range(len(middle) + 1):
        for mid in permutations(middle, r):
            c = cost_of([entry, *mid, exit_])
            if c is not None:
                best = min(best, c)
    assert abs(distances_to(g, exit_, weights)[entry] - best) < 1e-9
    assert g.verify_initial_path()


def test_convoy_only_moves_through_existing_corridors():
    """Every decision of the convoy must use a corridor that touches the current vertex."""
    sim, manager = match("escenario_complejo.json")
    graph = manager.graph_m
    seen = 0
    for _ in range(400):
        sim.tick(1.0)
        d = sim.convoy.decision
        if d and d["time"] >= seen:
            c = graph.corridors[d["chosen"]["corridor"]]
            assert d["at"] in (c.u, c.v)
            seen = d["time"]
        if sim.world.status.value != "RUNNING":
            break
    assert sim.world.status.value == "DEFEAT"  # no defenders were bought
