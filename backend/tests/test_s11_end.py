"""Section 11: consistency and end conditions (with the tie-break priorities)."""
from conftest import match, slow_convoy, station
from src.features.simulation.domain.entities import SimState


def _near_exit(sim):
    """Place the convoy on the last corridor, half a step away from the exit."""
    c = sim.convoy
    c.corridor = sim.world.manager.graph_m.corridors["M_C3"]
    c.from_v, c.to_v, c.vertex = "M_N2", "M_SALIDA", None
    c.progress = c.corridor.length - c.corridor.speed_allowed * 0.1
    c.previous = "M_N1"


def test_defeat_when_a_living_machine_reaches_the_exit():
    sim, _ = match()
    sim.tick(100)
    assert sim.world.status == SimState.DEFEAT
    assert 22.9 < sim.world.clock < 23.3                    # 8 + 7 + 8 seconds of corridors


def test_victory_by_resistance_at_the_time_limit():
    sim, manager = match()
    slow_convoy(manager)
    manager.metadata.time_limit = 20.0
    sim.tick(19.75)
    assert sim.world.status == SimState.RUNNING
    sim.tick(0.25)
    assert sim.world.status == SimState.VICTORY_RESISTANCE and sim.world.clock == 20.0


def test_victory_by_elimination_when_everything_is_destroyed():
    sim, _ = match()
    station(sim, "gunner", "V_C1", 3)
    sim.convoy.update = lambda dt: None
    sim.convoy.xy = sim.world.coords("V_C1")
    sim.tick(20)
    assert sim.world.status == SimState.VICTORY_ELIMINATION


def test_same_instant_attacks_are_resolved_before_the_exit_check():
    sim, _ = match()
    sim.world.enemies = sim.world.enemies[3:]               # only one robot left
    sim.world.enemies[0].hp = 10
    (sid,) = station(sim, "sniper", "V_C2")
    sim.world.soldiers[sid].base_range = 100.0              # reaches the exit from the tower
    _near_exit(sim)
    sim.tick(0.25)                                          # arrival and the killing blow coincide
    assert sim.world.status == SimState.VICTORY_ELIMINATION


def test_exit_arrival_is_checked_before_the_time_limit():
    sim, _ = match()
    sim.world.manager.metadata.time_limit = 30.0
    sim.world.clock = 29.75
    _near_exit(sim)
    sim.tick(0.25)                                          # exit and time limit in the same instant
    assert sim.world.status == SimState.DEFEAT


def test_updates_stop_when_the_match_ends():
    sim, _ = match()
    sim.tick(100)
    clock, events, state = sim.world.clock, len(sim.world.events), sim.world.status
    sim.tick(10)
    assert (sim.world.clock, len(sim.world.events), sim.world.status) == (clock, events, state)


def test_a_dead_machine_gets_no_more_attacks_or_rewards():
    sim, _ = match()
    station(sim, "gunner", "V_C1", 1)
    sim.convoy.update = lambda dt: None
    sim.convoy.xy = sim.world.coords("V_C1")
    sim.tick(60)
    earned = sim.world.budget.earned
    assert earned == 150 + 100 + 50 * 2                     # exactly one reward per machine
    hits = [e for e in sim.world.events if e["kind"] == "combat"]
    assert all("-100" in e["text"] for e in hits)
    assert not any(e.alive for e in sim.world.enemies)


def test_a_unit_is_never_in_two_places_at_once():
    sim, manager = match()
    slow_convoy(manager)
    sim.world.budget.available += 1000
    sim.recruit("infantry", 3)
    sim.ground.request(["S1"], "V_C1", "walk")
    sim.air.request(["S2", "S3"], "V_C2")
    for _ in range(80):
        sim.tick(0.25)
        in_transfer = {sid for t in sim.ground.transfers if t.status != "DONE" for sid in t.soldier_ids}
        in_flight = {sid for f in sim.air.flights if f.status == "FLYING" for sid in f.aboard}
        assert not (in_transfer & in_flight)
        assert all(sid not in in_flight for sid in in_transfer)
