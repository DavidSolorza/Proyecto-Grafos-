"""Section 3: besides checking that entry and exit are connected, the cheapest route must be calculated."""
import itertools

import pytest

from conftest import match, load
from src.features.labyrinth.application.route_finder import minimum_route
from src.features.simulation.domain.entities import SimState


def all_simple_costs(graph, source, target):
    """Brute force: cost of every simple path from source to target."""
    costs = []

    def walk(cur, seen, cost):
        if cur == target:
            costs.append(cost)
            return
        for c in graph.adj[cur]:
            nxt = c.v if c.u == cur else c.u
            if nxt not in seen:
                walk(nxt, seen | {nxt}, cost + c.base_time)
    walk(source, {source}, 0.0)
    return costs


@pytest.mark.parametrize("name", ["escenario_general_p_tardo.json", "escenario_complejo.json",
                                  "escenario_puentes.json", "escenario_cuadrilla.json"])
def test_initial_route_is_the_cheapest_of_all_simple_paths(name):
    manager = load(name)
    route = manager.initial_route
    entry, exit_v = manager.graph_m.get_entry().id, manager.graph_m.get_exit().id
    assert route["cost"] == pytest.approx(min(all_simple_costs(manager.graph_m, entry, exit_v)))
    assert route["vertices"][0] == entry and route["vertices"][-1] == exit_v
    corridors = [manager.graph_m.corridors[c] for c in route["corridors"]]
    assert sum(c.base_time for c in corridors) == pytest.approx(route["cost"])
    for (a, b), c in zip(itertools.pairwise(route["vertices"]), corridors):       # consecutive vertices are joined by that corridor
        assert {c.u, c.v} == {a, b}


def test_known_route_of_the_simple_scenario():
    route = load().initial_route
    assert route["vertices"] == ["M_ENTRADA", "M_N1", "M_N2", "M_SALIDA"]
    assert route["corridors"] == ["M_C1", "M_C2", "M_C3"] and route["cost"] == 8.0 + 7.0 + 8.0


@pytest.mark.parametrize("name", ["escenario_general_p_tardo.json", "escenario_complejo.json"])
def test_undefended_convoy_takes_exactly_the_initial_route(name):
    """With no defenders danger is zero, so the reactive convoy must reach the exit in the route's time."""
    sim, manager = match(name)
    sim.tick(400)
    assert sim.world.status == SimState.DEFEAT
    assert 0 <= sim.world.clock - manager.initial_route["cost"] <= 0.25            # quantized to the 0.25 s step


def test_minimum_route_edge_cases():
    manager = load()
    graph = manager.graph_m
    assert minimum_route(graph, "M_N1", "M_N1")["cost"] == 0.0
    assert minimum_route(graph, "M_ENTRADA", "NOPE") is None
    custom = {c: 100.0 for c in graph.corridors}
    custom["M_C1"] = 1.0
    assert minimum_route(graph, "M_ENTRADA", "M_N1", custom)["cost"] == 1.0         # explicit weights override t(e)


def test_route_is_none_when_entry_and_exit_are_not_connected():
    manager = load(edit=lambda raw: raw["graph_m"]["edges"].pop())
    assert manager.initial_route is None and manager.validate_initial_state()["labyrinth_path_exists"] is False
