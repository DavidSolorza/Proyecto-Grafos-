"""Section 3 and 8 details: transports that are not allowed, plain roads, and the repair crew of N people."""
import copy
import json

import pytest

from conftest import DOCS, collapse, crew_match, edit_edge, match
from src.core.errors.handlers import AppError
from src.features.elevated_graph.application.defense_planner import plan_defense
from src.features.elevated_graph.application.ge_paths import shortest_path
from src.features.scenario.application.loader import ScenarioLoader
from src.features.simulation.application.serializer import simulation_to_dict
from src.features.simulation.domain.units import SoldierStatus

RAW = json.loads((DOCS / "escenario_cuadrilla.json").read_text(encoding="utf-8"))


# ---- validation -----------------------------------------------------------------------------

def test_the_new_scenario_is_valid():
    assert all(ScenarioLoader.load_from_dict(copy.deepcopy(RAW)).validate_initial_state().values())


@pytest.mark.parametrize("name,edit,text", [
    ("sin ningún medio", edit_edge("E_E4", time_walk=None, time_moto=None), "al menos un medio"),
    ("medio con tiempo 0", edit_edge("E_E4", time_moto=0), "time_moto"),
    ("medio con texto", edit_edge("E_E4", time_moto="rápido"), "time_moto"),
    ("puente sin resistencia máxima", edit_edge("E_E1", bridge_max_hp=None), "puente"),
    ("cuadrilla negativa", lambda r: r["metadata"].update(bridge_repair_crew=-1), "bridge_repair_crew"),
    ("cuadrilla decimal", lambda r: r["metadata"].update(bridge_repair_crew=1.5), "bridge_repair_crew"),
])
def test_invalid_variants_are_rejected(name, edit, text):
    raw = copy.deepcopy(RAW)
    edit(raw)
    with pytest.raises(AppError) as err:
        ScenarioLoader.load_from_dict(raw)
    assert text in err.value.message


# ---- a transport that is not allowed on an edge -----------------------------------------------

def test_walking_never_uses_a_moto_only_edge_but_motorcycles_do():
    _, manager = match("escenario_cuadrilla.json")
    g = manager.graph_e
    assert shortest_path(g, "V_BASE", "V_H1", "walk") is None
    cost, vertices, _ = shortest_path(g, "V_BASE", "V_H1", "moto")
    assert vertices[-1] == "V_H1" and cost == 5 + 3 + 6 + 4


def test_a_walk_only_edge_is_skipped_by_motorcycles():
    _, manager = match("escenario_cuadrilla.json", edit_edge("E_E3", time_moto=None))
    assert shortest_path(manager.graph_e, "V_BASE", "V_C2", "moto") is None
    assert shortest_path(manager.graph_e, "V_BASE", "V_C2", "walk")[0] == 12 + 8 + 15


def test_the_tree_is_walked_so_vertices_behind_a_moto_only_edge_are_outside_it():
    sim, manager = match("escenario_cuadrilla.json")
    plan = plan_defense(manager)
    assert plan["unreachable"] == ["V_H1"]
    assert plan["mst"]["total_time"] == 12 + 8 + 15 and len(plan["mst"]["edges"]) == 3


def test_a_candidate_behind_a_moto_only_edge_cannot_become_a_tower():
    def edit(raw):
        edit_edge("E_E3", time_walk=None)(raw)               # now V_C2 is not walkable from the base
    _, manager = match("escenario_cuadrilla.json", edit)
    plan = plan_defense(manager)
    assert [t["vertex_id"] for t in plan["towers"]] == ["V_C1"] and "V_C2" in plan["unreachable"]


# ---- plain roads and bridges ------------------------------------------------------------------

def test_a_plain_road_never_wears_out():
    sim, manager = crew_match()
    road = manager.graph_e.edges["E_E3"]
    assert not road.is_bridge
    for _ in range(25):
        sim.bridges.wear(road)
    assert not road.is_destroyed and road.bridge_current_hp is None


def test_only_bridges_are_reported_as_bridges():
    sim, _ = crew_match()
    assert [b["id"] for b in simulation_to_dict(sim)["bridges"]] == ["E_E1", "E_E2"]


def test_motorcycles_wear_bridges_but_not_roads_on_the_same_trip():
    sim, manager = crew_match(crew=0)
    sim.world.budget.available += 1000
    (sid,) = sim.recruit("infantry", 1)
    sim.ground.request([sid], "V_C2", "moto")
    sim.tick(20)                                             # crosses E_E1, E_E2 (bridges) and E_E3 (road)
    g = manager.graph_e
    assert (g.edges["E_E1"].bridge_current_hp, g.edges["E_E3"].bridge_current_hp) == (2, None)
    assert g.edges["E_E2"].is_destroyed


def test_a_moto_only_shortcut_between_walkable_vertices_is_ignored_by_kruskal():
    def add_shortcut(raw):
        raw["graph_e"]["edges"].append({"id": "E_X", "u": "V_BASE", "v": "V_C1", "time_walk": None,
                                        "time_moto": 1.0})
    _, manager = match("escenario_cuadrilla.json", add_shortcut)
    plan = plan_defense(manager)
    assert plan["mst"]["total_time"] == 12 + 8 + 15
    assert "E_X" not in [e["id"] for e in plan["mst"]["edges"]]
    assert shortest_path(manager.graph_e, "V_BASE", "V_C1", "moto")[0] == 1.0     # but motorcycles take it
