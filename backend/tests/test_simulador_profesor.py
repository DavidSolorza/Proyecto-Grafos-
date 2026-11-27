"""Cross-section review suite: one end-to-end check per main rule of the statement.

The detailed cases of every section live in the test_s*.py and test_corrections.py files.
"""
import json
import re

import pytest

from conftest import DOCS, load, match, slow_convoy, station
from src.features.elevated_graph.application.defense_planner import plan_defense
from src.features.elevated_graph.application.mst_service import build_mst
from src.features.scenario.application.validator import validate_scenario
from src.features.simulation.domain.entities import SimState


def _raw(name="escenario_general_p_tardo.json"):
    return json.loads((DOCS / name).read_text(encoding="utf-8"))


def test_profesor_01_no_forbidden_graph_libraries():
    """Section 2: no graph libraries and no heapq anywhere in the backend sources."""
    banned = re.compile(r"^\s*(import|from)\s+(networkx|igraph|graph_tool|scipy|heapq)\b", re.M)
    sources = (DOCS.parent / "backend" / "src").rglob("*.py")
    assert [p.name for p in sources if banned.search(p.read_text(encoding="utf-8"))] == []


def test_profesor_02_dual_graph_independence():
    """Section 3: every edge joins two vertices of its own graph."""
    raw = _raw()
    ge = {v["id"] for v in raw["graph_e"]["vertices"]}
    gm = {v["id"] for v in raw["graph_m"]["vertices"]}
    assert ge.isdisjoint(gm)
    assert all(e["u"] in ge and e["v"] in ge for e in raw["graph_e"]["edges"])
    assert all(c["u"] in gm and c["v"] in gm for c in raw["graph_m"]["edges"])


def test_profesor_03_kruskal_and_greedy_tower_formula():
    """Section 4: spanning tree of the base component and S(p) = C(p) / (1 + D_T / D0)."""
    manager = load()
    tree = build_mst(manager.graph_e, "V_BASE")
    plan = plan_defense(manager)
    assert len(tree.edges) == len(tree.vertices) - 1
    assert 0 < len(plan["towers"]) <= manager.metadata.max_towers_k
    for tower in plan["towers"]:
        assert tower["score"] == pytest.approx(tower["gain"] / (1 + tower["dt"] / manager.metadata.d0))


def test_profesor_04_effective_range_uses_the_tower_height():
    """Section 5: R_ef = R_base * (1 + beta * z), as computed by the simulation."""
    sim, manager = match()
    tower = next(iter(sim.world.towers))
    (sid,) = station(sim, "sniper", tower)
    expected = 20 * (1 + manager.metadata.beta * manager.graph_e.vertices[tower].z)
    assert sim.world.effective_range(sim.world.soldiers[sid]) == pytest.approx(expected)


def test_profesor_05_danger_raises_the_weight_of_the_corridors():
    """Section 6: w(e) = t(e) + alpha * P(e) with the active defenders."""
    sim, manager = match()
    calm = sim.convoy.refresh_weights()
    station(sim, "gunner", next(iter(sim.world.towers)))
    danger = sim.convoy.refresh_weights()
    assert any(danger[cid] > calm[cid] for cid in calm)
    for c in manager.graph_m.corridors.values():
        assert danger[c.id] == pytest.approx(c.base_time + manager.metadata.alpha * c.current_danger)


def test_profesor_06_motorcycle_wear_collapse_and_repair():
    """Section 8: one point per motorcycle crossing; the bridge returns with full strength."""
    sim, manager = match("escenario_puentes.json")
    slow_convoy(manager)
    sim.recruit("infantry", 2)                              # S2 stays at the base to rebuild
    sim.ground.request(["S1"], "V_C1", "moto")
    sim.tick(8)
    first, second = manager.graph_e.edges["E_E1"], manager.graph_e.edges["E_E2"]
    assert first.bridge_current_hp == first.bridge_max_hp - 1 and second.is_destroyed
    sim.tick(manager.metadata.bridge_repair_time)
    assert not second.is_destroyed and second.bridge_current_hp == second.bridge_max_hp


def test_profesor_07_helicopter_four_seats_and_surplus():
    """Section 9: at most four soldiers; the surplus goes to the next tower."""
    sim, manager = match()
    slow_convoy(manager)
    sim.world.budget.available += 1000
    sids = sim.recruit("infantry", 5)
    with pytest.raises(Exception, match="1 a 4"):
        sim.air.request(sids, "V_C1")
    sim.air.request(sids[:4], "V_C1")
    sim.tick(30)
    assert sorted(sim.world.occupants(t) for t in sim.world.towers) == [1, 3]


def test_profesor_08_budget_never_negative():
    """Section 10: purchases are charged and an unaffordable one is rejected."""
    sim, manager = match()
    start = sim.world.budget.available
    sim.recruit("gunner", 1)
    assert sim.world.budget.available == start - 500
    with pytest.raises(Exception, match="insuficiente"):
        sim.recruit("gunner", 20)
    assert sim.world.budget.available == start - 500


def test_profesor_09_logical_clock_and_end_conditions():
    """Section 11: fixed logical steps and a final state that no longer changes."""
    sim, _ = match()
    sim.tick(0.25)
    assert sim.world.clock == 0.25
    sim.tick(400)
    assert sim.world.status in (SimState.VICTORY_ELIMINATION, SimState.VICTORY_RESISTANCE,
                                SimState.DEFEAT)
    stopped = sim.world.clock
    sim.tick(10)
    assert sim.world.clock == stopped


def test_profesor_10_the_file_is_validated():
    """Section 12: a valid scenario passes and an incomplete one is explained."""
    raw = _raw()
    assert validate_scenario(raw) == []
    del raw["graph_e"]
    assert any("graph_e" in error for error in validate_scenario(raw))
