"""One test per defect of the status report: closed match, re-planning, landing, ties, destinations."""
import pytest

from conftest import match, slow_convoy, snapshot, station
from src.core.errors.handlers import AppError
from src.features.scenario.application.loader import ScenarioLoader
from src.features.simulation.application.engine import Simulation
from src.features.simulation.domain.entities import SimState
from src.features.simulation.domain.units import SoldierStatus
from src.features.simulation.domain.world import natural_key


def _ready(n=2, name="escenario_general_p_tardo.json"):
    sim, manager = match(name)
    slow_convoy(manager)
    sim.world.budget.available += 5000
    sim.recruit("infantry", n)
    return sim, manager


@pytest.mark.parametrize("state", [SimState.DEFEAT, SimState.VICTORY_ELIMINATION,
                                   SimState.VICTORY_RESISTANCE])
def test_a_finished_match_accepts_no_orders(state):
    sim, _ = _ready()
    sim.world.status = state
    before = snapshot(sim)
    for order in (lambda: sim.recruit("infantry", 1),
                  lambda: sim.ground.request(["S1"], "V_C1", "walk"),
                  lambda: sim.air.request(["S1"], "V_C1")):
        with pytest.raises(AppError, match="terminó") as error:
            order()
        assert error.value.status_code == 409
    assert snapshot(sim) == before


def test_a_collapse_further_ahead_is_replanned_at_the_next_vertex():
    def vertex(i, x, kind):
        return {"id": i, "coords": [x, 10], "type": kind, "z": 0}

    def edge(i, u, v, seconds):
        return {"id": i, "u": u, "v": v, "time_walk": seconds, "time_moto": seconds,
                "bridge_max_hp": 5, "bridge_current_hp": 5}

    def diamond(raw):
        raw["graph_e"] = {"vertices": [vertex("B", 10, "BASE"), vertex("M1", 20, "TRANSIT"),
                                       vertex("M2", 30, "TRANSIT"), vertex("T", 40, "CANDIDATE")],
                          "edges": [edge("e1", "B", "M1", 5), edge("e2", "M1", "M2", 5),
                                    edge("e3", "M2", "T", 5), edge("e4", "M1", "T", 12)]}
        raw["candidates_meta"] = [{"vertex_id": "T", "rv": 1000}]

    _, manager = match(edit=diamond)
    slow_convoy(manager)
    sim = Simulation(manager, {"towers": [{"vertex_id": "T", "rv": 1000}]})
    sim.recruit("infantry", 1)
    transfer = sim.ground.request(["S1"], "T", "walk")
    sim.tick(1)                                               # walking e1; e3 collapses further on
    ahead = manager.graph_e.edges["e3"]
    ahead.is_destroyed, ahead.repair_timer = True, 1000
    sim.world.version += 1
    sim.tick(16)
    assert transfer.vertices == ["M1", "T"]                   # re-planned at M1, not at M2
    assert sim.world.clock == 17 and sim.world.soldiers["S1"].status == SoldierStatus.STATIONED
    assert any("recalculan por un puente caído desde M1" in ev["text"] for ev in sim.world.events)


def test_landing_uses_the_room_that_is_free_at_that_moment():
    sim, _ = _ready(n=7)
    guards = station(sim, "infantry", "V_C1", 2)              # one free slot at take-off
    sim.air.request(["S1", "S2", "S3"], "V_C1")
    sim.world.soldiers[guards[0]].status = SoldierStatus.AT_BASE   # a slot frees up in flight
    sim.world.soldiers[guards[0]].vertex = "V_BASE"
    sim.tick(30)
    assert sim.world.occupants("V_C1") == 3 and sim.world.reserved["V_C1"] == 0
    inside = [s for s in ("S1", "S2", "S3") if sim.world.soldiers[s].vertex == "V_C1"]
    assert len(inside) == 2


def test_ties_follow_the_identification_order_with_ten_or_more_units():
    ids = ["ROBOT_SOLDIER-10", "ROBOT_SOLDIER-2", "ROBOT_SOLDIER-1"]
    assert sorted(ids, key=natural_key) == ["ROBOT_SOLDIER-1", "ROBOT_SOLDIER-2", "ROBOT_SOLDIER-10"]
    sim, _ = _ready(n=1)
    template = sim.world.enemies[0]
    sim.world.enemies = [type(template)(i, template.type, 50, 50, 50) for i in ids[:2]]
    station(sim, "sniper", "V_C1")
    sim.combat.update(sim.world.coords("V_C1"))
    assert [e.id for e in sim.world.enemies if e.hp < e.max_hp] == ["ROBOT_SOLDIER-2"]


@pytest.mark.parametrize("mode", ["walk", "moto"])
def test_soldiers_can_move_to_any_position_and_only_attack_from_towers(mode):
    sim, _ = _ready()
    sim.ground.request(["S1"], "V_T1", mode)
    sim.tick(60)
    soldier = sim.world.soldiers["S1"]
    assert (soldier.vertex, soldier.status) == ("V_T1", SoldierStatus.DEPLOYED)
    assert sim.world.armed_defenders() == []
    sim.ground.request(["S1"], "V_C1", mode)                  # and it can receive new orders
    sim.tick(60)
    assert soldier.status == SoldierStatus.STATIONED


def test_a_heliport_is_a_landing_pad_and_a_pickup_point():
    sim, _ = _ready()
    sim.air.request(["S1", "S2"], "V_H1")
    sim.tick(60)
    assert all(sim.world.soldiers[s].status == SoldierStatus.DEPLOYED for s in ("S1", "S2"))
    sim.air.request(["S1", "S2"], "V_C1")
    sim.tick(60)
    assert sim.world.occupants("V_C1") == 2


@pytest.mark.parametrize("edit,message", [
    (lambda r: r["defenders_config"]["sniper"].update(damage=60), "tabla del enunciado"),
    (lambda r: r["metadata"].update(time_limit=450), "300 segundos"),
    (lambda r: r.pop("helicopter"), "helicopter"),
])
def test_a_scenario_cannot_change_the_rules_of_the_statement(edit, message):
    with pytest.raises(AppError, match=message):
        match(edit=edit)


def test_every_delivered_scenario_follows_the_rules():
    from conftest import DOCS
    paths = sorted(DOCS.glob("escenario_*.json"))
    assert len(paths) >= 2
    for path in paths:
        manager = ScenarioLoader.load_from_file(path)
        assert manager.metadata.time_limit == 300 and manager.metadata.bridge_repair_crew >= 1
