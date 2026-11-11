"""Sections 9 and 10: helicopters, surplus distribution, budget."""
from math import dist

import pytest

from conftest import match, slow_convoy, snapshot, station
from src.core.errors.handlers import AppError
from src.features.simulation.domain.units import SoldierStatus


def _air(name="escenario_general_p_tardo.json", n=4, money=0):
    sim, manager = match(name)
    slow_convoy(manager)
    sim.recruit("infantry", n)
    sim.world.budget.available += money
    return sim


def test_helicopter_requests_are_validated_without_side_effects():
    sim = _air(n=5)
    for ids, dest in ((["S1", "S2", "S3", "S4", "S5"], "V_C1"),   # more than 4
                      (["S9"], "V_C1"), (["S1"], "V_H1"), (["S1"], "V_BASE"), ([], "V_C1")):
        before = snapshot(sim)
        with pytest.raises(AppError):
            sim.air.request(ids, dest)
        assert snapshot(sim) == before


def test_flight_needs_budget_and_has_a_limited_number_of_uses():
    sim = _air()
    sim.world.budget.available = 199                        # flight costs 200
    before = snapshot(sim)
    with pytest.raises(AppError, match="Presupuesto"):
        sim.air.request(["S1"], "V_C1")
    assert snapshot(sim) == before
    sim.world.budget.available = 10_000
    for i in range(3):                                      # max_uses = 3
        sim.air.request([f"S{i + 1}"], "V_C1" if i < 2 else "V_C2")
    with pytest.raises(AppError, match="usos"):
        sim.air.request(["S4"], "V_C2")


def test_flight_duration_is_euclidean_distance_over_speed():
    sim = _air(money=1000)
    sim.air.request(["S1"], "V_C1")
    expected = dist((10, 10), (30, 20)) / sim.air.speed
    flight = sim.air.flights[0]
    assert abs(flight.duration - expected) < 1e-9
    sim.tick(expected - 0.5)
    assert flight.status == "FLYING"
    sim.tick(1.0)
    assert sim.world.soldiers["S1"].status == SoldierStatus.STATIONED


def test_soldiers_on_board_are_in_transit_and_do_not_attack():
    sim = _air(money=1000)
    sim.air.request(["S1"], "V_C1")
    assert sim.world.soldiers["S1"].status == SoldierStatus.FLYING
    assert sim.world.armed_defenders() == []


def test_money_is_reserved_during_the_flight_and_spent_after_landing_once():
    sim = _air(money=1000)
    start = sim.world.budget.available
    sim.air.request(["S1", "S2"], "V_C1")
    b = sim.world.budget
    assert (b.available, b.reserved, b.spent) == (start - 200, 200, 400 + 0)
    sim.tick(30)
    assert (b.available, b.reserved, b.spent) == (start - 200, 0, 400 + 200)


def test_surplus_goes_to_nearest_tower_with_room():
    sim = _air(money=1000)
    station(sim, "infantry", "V_C1", 2)                    # V_C1 already has 2 -> 1 free slot
    sim.air.request(["S1", "S2", "S3", "S4"], "V_C1")
    sim.tick(40)
    assert sim.world.occupants("V_C1") == 3                # only ONE of the four fits there
    assert sim.world.occupants("V_C2") == 3                # the other three go to the next tower
    assert not any(s.status == SoldierStatus.FLYING for s in sim.world.soldiers.values())


def test_partial_distribution_then_return_to_base():
    sim = _air(money=1000)
    station(sim, "infantry", "V_C1", 2)                    # 1 free
    station(sim, "infantry", "V_C2", 2)                    # 1 free
    sim.air.request(["S1", "S2", "S3", "S4"], "V_C1")      # 1 + 1 fit, 2 must go home
    sim.tick(80)
    assert sim.world.occupants("V_C1") == 3 and sim.world.occupants("V_C2") == 3
    home = [s for s in sim.world.soldiers.values() if s.vertex == "V_BASE"]
    assert len(home) == 2 and all(s.status == SoldierStatus.AT_BASE for s in home)


def test_leftovers_return_to_base_when_every_tower_is_full():
    sim = _air(n=2, money=1000)
    station(sim, "infantry", "V_C1", 3)
    station(sim, "infantry", "V_C2", 3)
    sim.air.request(["S1", "S2"], "V_C1")                  # destination is already full
    sim.tick(60)
    for sid in ("S1", "S2"):
        s = sim.world.soldiers[sid]
        assert s.vertex == "V_BASE" and s.status == SoldierStatus.AT_BASE
    assert sim.air.max_uses - sim.air.uses == 2            # the whole trip used ONE flight
    assert sim.world.budget.reserved == 0


def test_simultaneous_flights_never_overfill_a_tower():
    sim = _air(n=6, money=2000)
    sim.air.request(["S1", "S2", "S3"], "V_C1")
    sim.air.request(["S4", "S5", "S6"], "V_C1")            # both want the same tower
    for _ in range(200):
        sim.tick(0.25)
        for t in sim.world.towers:
            assert sim.world.occupants(t) + sim.world.reserved.get(t, 0) <= 3
    assert sim.world.occupants("V_C1") == 3 and sim.world.occupants("V_C2") == 3


def test_budget_never_goes_negative_and_purchases_are_checked_first():
    sim, _ = match()
    before = snapshot(sim)
    with pytest.raises(AppError, match="Presupuesto"):
        sim.recruit("gunner", 5)                           # 5 * 500 > 2000
    assert snapshot(sim) == before
    sim.recruit("gunner", 4)                               # exactly 2000
    assert sim.world.budget.available == 0
    with pytest.raises(AppError):
        sim.recruit("infantry", 1)
    assert sim.world.budget.available >= 0


def test_bought_soldiers_appear_at_the_base_with_scenario_stats():
    sim, manager = match()
    ids = sim.recruit("sniper", 2)
    for sid in ids:
        s = sim.world.soldiers[sid]
        assert s.vertex == "V_BASE" and s.status == SoldierStatus.AT_BASE
        assert (s.damage, s.base_range, s.frequency) == (50, 20.0, 0.5)
    assert sim.world.budget.available == manager.metadata.initial_budget - 600
