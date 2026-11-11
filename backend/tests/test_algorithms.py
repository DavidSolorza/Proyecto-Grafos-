"""Algorithm tests. They run without Flask or any UI: `python -m pytest backend/tests`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.core.errors.handlers import AppError
from src.features.elevated_graph.application.defense_planner import plan_defense
from src.features.elevated_graph.application.disjoint_set import DisjointSet
from src.features.elevated_graph.application.ge_paths import shortest_path
from src.features.scenario.application.loader import ScenarioLoader
from src.features.simulation.application.engine import Simulation
from src.features.simulation.domain.entities import SimState

EXAMPLE = Path(__file__).resolve().parents[2] / "docs" / "escenario_general_p_tardo.json"


def new_match():
    manager = ScenarioLoader.load_from_file(EXAMPLE)
    return Simulation(manager, plan_defense(manager)), manager


def run(sim, seconds):
    sim.tick(seconds)


def slow_convoy(manager):
    """Keep the match alive so a test can look at bridges and transport only."""
    for c in manager.graph_m.corridors.values():
        c.speed_allowed = 0.01


def test_disjoint_set_detects_cycles():
    ds = DisjointSet(["a", "b", "c"])
    assert ds.union("a", "b") and ds.union("b", "c")
    assert not ds.union("a", "c")


def test_mst_and_greedy_towers_on_example():
    manager = ScenarioLoader.load_from_file(EXAMPLE)
    plan = plan_defense(manager)
    assert len(plan["mst"]["edges"]) == len(manager.graph_e.vertices) - 1
    assert plan["mst"]["dist_from_base"]["V_C1"] == 20.0
    assert [t["vertex_id"] for t in plan["towers"]] == ["V_C1", "V_C2"]
    assert plan["coverage_pct"] == 100.0


def test_walk_and_moto_paths_use_different_times():
    _, manager = new_match()
    assert shortest_path(manager.graph_e, "V_BASE", "V_C1", "walk")[0] == 20.0
    assert shortest_path(manager.graph_e, "V_BASE", "V_C1", "moto")[0] == 8.0


def test_failed_request_does_not_change_state():
    sim, _ = new_match()
    sim.recruit("infantry", 3)
    before = sim.world.budget.available
    with pytest.raises(AppError):
        sim.ground.request(["S1", "S2"], "V_C1", "walk")   # walking carries only one
    assert sim.world.budget.available == before
    assert sim.world.reserved == {} and sim.ground.transfers == []


def test_tower_capacity_counts_reservations():
    sim, _ = new_match()
    sim.recruit("infantry", 4)
    for sid in ("S1", "S2", "S3"):
        sim.ground.request([sid], "V_C1", "walk")
    with pytest.raises(AppError):
        sim.ground.request(["S4"], "V_C1", "walk")  # 3 reservations already fill the tower


def test_defeat_without_defenders():
    sim, _ = new_match()
    run(sim, 120)
    assert sim.world.status == SimState.DEFEAT


def test_victory_by_elimination_and_single_reward():
    sim, _ = new_match()
    sim.recruit("sniper", 3)
    for sid in ("S1", "S2", "S3"):
        sim.ground.request([sid], "V_C1", "moto")
    run(sim, 200)
    assert sim.world.status == SimState.VICTORY_ELIMINATION
    assert sim.world.budget.earned == 150 + 100 + 50 * 2  # each machine pays once


def test_motorcycles_wear_and_collapse_bridge_then_repair():
    sim, manager = new_match()
    slow_convoy(manager)
    edge = manager.graph_e.edges["E_E1"]
    edge.bridge_current_hp = 1
    sim.recruit("infantry", 1)
    sim.ground.request(["S1"], "V_C1", "moto")
    run(sim, 6)  # E_E1 takes 5s by motorcycle
    assert edge.is_destroyed
    run(sim, manager.metadata.bridge_repair_time + 1)
    assert not edge.is_destroyed and edge.bridge_current_hp == edge.bridge_max_hp


def test_blocked_soldier_waits_and_resumes():
    sim, manager = new_match()
    slow_convoy(manager)
    sim.recruit("infantry", 1)
    sim.ground.request(["S1"], "V_C1", "walk")
    run(sim, 1)
    manager.graph_e.edges["E_E2"].is_destroyed = True  # collapse right in front of it
    manager.graph_e.edges["E_E2"].repair_timer = 30
    run(sim, 14)
    assert sim.world.soldiers["S1"].status.value == "WAITING"
    run(sim, 30)  # repaired -> connectivity version changed -> retries
    assert sim.world.soldiers["S1"].status.value == "STATIONED"


def test_helicopter_distributes_surplus_and_charges_once():
    sim, manager = new_match()
    slow_convoy(manager)
    sim.recruit("infantry", 4)
    sim.world.budget.available += 1000
    before = sim.world.budget.available
    sim.air.request(["S1", "S2", "S3", "S4"], "V_C1")
    run(sim, 30)
    stationed = {s.id: s.vertex for s in sim.world.soldiers.values()}
    assert sorted(stationed.values()).count("V_C1") == 3
    assert sorted(stationed.values()).count("V_C2") == 1   # surplus goes to the next tower
    assert sim.world.budget.available == before - sim.air.cost
    assert sim.world.budget.reserved == 0


def test_complex_scenario_tree_ties_and_unreachable_candidate():
    path = EXAMPLE.with_name("escenario_complejo.json")
    manager = ScenarioLoader.load_from_file(path)
    plan = plan_defense(manager)
    assert len(plan["mst"]["edges"]) == 7           # 8 reachable vertices -> 7 tree edges
    assert plan["unreachable"] == ["V_ISLA"]         # outside the base component
    assert "V_ISLA" not in [t["vertex_id"] for t in plan["towers"]]
    assert plan["towers"][0]["vertex_id"] == "V_C4"  # best S(p) in the first iteration
