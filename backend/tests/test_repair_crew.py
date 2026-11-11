"""Section 3 and 8: rebuilding a bridge keeps N people busy (bridge_repair_crew)."""
import pytest

from conftest import collapse, crew_match, match, station
from src.core.errors.handlers import AppError
from src.features.simulation.application.serializer import simulation_to_dict
from src.features.simulation.domain.units import SoldierStatus


# ---- the crew of N people ---------------------------------------------------------------------

def test_without_free_people_at_the_base_the_repair_waits_and_the_timer_does_not_run():
    sim, _ = crew_match(crew=2)
    edge = collapse(sim)
    sim.tick(60)                                             # twice the repair time
    assert edge.is_destroyed and edge.repair_timer == 30.0
    assert simulation_to_dict(sim)["bridges"][1]["waiting_crew"] is True
    assert sum("espera" in e["text"] for e in sim.world.events) == 1   # explained once, not every step


def test_one_person_is_not_enough_for_a_crew_of_two():
    sim, _ = crew_match(crew=2)
    sim.world.budget.available += 500
    sim.recruit("infantry", 1)
    edge = collapse(sim)
    sim.tick(40)
    assert edge.is_destroyed and edge.occupied_by_repair_units == 0


def test_a_full_crew_gets_busy_rebuilds_the_bridge_and_is_released():
    sim, _ = crew_match(crew=2)
    sim.world.budget.available += 500
    ids = sim.recruit("infantry", 3)                         # S1, S2, S3 at the base
    edge = collapse(sim)
    sim.tick(1)
    st = {i: sim.world.soldiers[i].status for i in ids}
    assert [st[i] for i in ids] == [SoldierStatus.REPAIRING, SoldierStatus.REPAIRING, SoldierStatus.AT_BASE]
    assert edge.occupied_by_repair_units == 2 and sim.bridges.crews["E_E2"] == ["S1", "S2"]
    sim.tick(28.5)
    assert edge.is_destroyed                                 # 29.5 s of 30 s
    sim.tick(1)
    assert not edge.is_destroyed and edge.bridge_current_hp == edge.bridge_max_hp
    assert all(sim.world.soldiers[i].status == SoldierStatus.AT_BASE for i in ids)
    assert edge.occupied_by_repair_units == 0


def test_people_rebuilding_cannot_receive_orders_attack_or_fly():
    sim, _ = crew_match(crew=2)
    sim.world.budget.available += 1000
    sim.recruit("infantry", 2)
    collapse(sim)
    sim.tick(1)
    with pytest.raises(AppError, match="ocupado"):
        sim.ground.request(["S1"], "V_C1", "walk")
    with pytest.raises(AppError):
        sim.air.request(["S1", "S2"], "V_C1")
    assert sim.world.soldiers["S1"].status == SoldierStatus.REPAIRING


def test_the_crew_comes_only_from_the_base_never_from_towers():
    sim, _ = crew_match(crew=1)
    (guard,) = station(sim, "infantry", "V_C1")
    collapse(sim)
    sim.tick(40)
    assert sim.world.soldiers[guard].status == SoldierStatus.STATIONED     # still guarding
    assert sim.world.manager.graph_e.edges["E_E2"].is_destroyed            # nobody free at the base


def test_two_collapsed_bridges_need_two_different_crews():
    sim, _ = crew_match(crew=1)
    sim.world.budget.available += 1000
    sim.recruit("infantry", 1)                               # only one person at the base
    first, second = collapse(sim, "E_E2"), collapse(sim, "E_E1")
    sim.tick(1)
    assert sorted(sim.bridges.crews) == ["E_E1"] and second.occupied_by_repair_units == 1
    assert first.occupied_by_repair_units == 0               # E_E1 is processed first (edge order)
    sim.tick(30)
    assert not second.is_destroyed
    sim.tick(31)
    assert not first.is_destroyed                            # the same person then rebuilt the second one


def test_without_a_crew_requirement_nothing_changes_and_nobody_is_busy():
    sim, _ = crew_match(crew=0)
    edge = collapse(sim)
    sim.tick(30)
    assert not edge.is_destroyed and edge.occupied_by_repair_units == 0


def test_a_restart_clears_crews_and_waiting_repairs():
    from src.features.scenario.application.session import session
    session.load(match("escenario_cuadrilla.json")[1])
    session.calculate_plan()
    sim = session.new_simulation()
    collapse(sim)
    sim.tick(1)
    fresh = session.new_simulation()
    assert fresh.bridges.crews == {} and fresh.bridges.waiting == set()
    assert not any(e.is_destroyed for e in fresh.world.manager.graph_e.edges.values())
