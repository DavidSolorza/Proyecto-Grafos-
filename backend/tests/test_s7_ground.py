"""Sections 7 and 8: ground transport and dynamic bridges."""
import pytest

from conftest import match, slow_convoy, snapshot, station
from src.core.errors.handlers import AppError
from src.features.simulation.domain.units import SoldierStatus


def _ready(name="escenario_general_p_tardo.json", n=3, kind="infantry"):
    sim, manager = match(name)
    slow_convoy(manager)
    sim.recruit(kind, n)
    return sim, manager


@pytest.mark.parametrize("ids,dest,mode", [
    (["S1"], "V_NOPE", "walk"),            # destination does not exist
    (["S9"], "V_C1", "walk"),              # soldier does not exist
    (["S1", "S2"], "V_C1", "walk"),        # walking carries one soldier
    (["S1", "S2", "S3"], "V_C1", "moto"),  # a motorcycle carries at most two
    (["S1"], "V_T1", "walk"),              # transit vertex is not a tower
    (["S1"], "V_BASE", "walk"),            # origin == destination
    (["S1"], "V_C1", "jet"),               # unknown transport
    ([], "V_C1", "walk"),                  # nobody selected
    (["S1", "S1"], "V_C1", "moto"),        # same soldier twice
])
def test_invalid_requests_are_rejected_without_touching_the_state(ids, dest, mode):
    sim, _ = _ready()
    before = snapshot(sim)
    with pytest.raises(AppError):
        sim.ground.request(ids, dest, mode)
    assert snapshot(sim) == before


def test_request_fails_without_valid_route_and_changes_nothing():
    sim, manager = _ready()
    manager.graph_e.edges["E_E1"].is_destroyed = True       # the base is cut off
    before = snapshot(sim)
    with pytest.raises(AppError, match="ruta"):
        sim.ground.request(["S1"], "V_C1", "walk")
    assert snapshot(sim) == before


def test_soldier_in_transit_cannot_receive_new_orders():
    sim, _ = _ready()
    sim.ground.request(["S1"], "V_C1", "walk")
    with pytest.raises(AppError, match="tránsito"):
        sim.ground.request(["S1"], "V_C2", "walk")


def test_soldiers_must_start_from_the_same_place():
    sim, _ = _ready()
    station(sim, "infantry", "V_C1")                        # S4 is in a tower, S1 at the base
    with pytest.raises(AppError, match="mismo origen"):
        sim.ground.request(["S1", "S4"], "V_C2", "moto")


def test_full_tower_counts_present_soldiers_and_reservations():
    sim, _ = _ready(n=3)
    station(sim, "infantry", "V_C1", 2)                     # 2 present
    sim.ground.request(["S1"], "V_C1", "walk")              # 1 reserved -> full
    before = snapshot(sim)
    with pytest.raises(AppError, match="capacidad"):
        sim.ground.request(["S2"], "V_C1", "walk")
    assert snapshot(sim) == before


def test_walking_and_motorcycle_times_match_the_edges():
    sim, manager = _ready(n=2)
    sim.ground.request(["S1"], "V_C1", "walk")              # 12 + 8 = 20 s
    sim.ground.request(["S2"], "V_C1", "moto")              # 5 + 3 = 8 s
    arrival = {}
    for _ in range(120):
        sim.tick(0.25)
        for sid in ("S1", "S2"):
            if sim.world.soldiers[sid].status == SoldierStatus.STATIONED and sid not in arrival:
                arrival[sid] = sim.world.clock
    assert arrival == {"S1": 20.0, "S2": 8.0}


def test_walking_never_wears_bridges_but_motorcycles_do_once_per_crossing():
    sim, manager = _ready(n=3)
    sim.ground.request(["S1"], "V_C1", "walk")
    sim.tick(25)
    assert all(e.bridge_current_hp == 10 for e in manager.graph_e.edges.values())
    sim.ground.request(["S2", "S3"], "V_C2", "moto")        # two riders, one motorcycle
    sim.tick(25)
    used = [manager.graph_e.edges[i] for i in ("E_E1", "E_E2", "E_E3")]
    assert [e.bridge_current_hp for e in used] == [9, 9, 9]  # -1 per bridge, not -2


def test_bridge_collapse_blocks_new_crossings_but_lets_started_ones_finish():
    sim, manager = _ready(n=2)
    edge = manager.graph_e.edges["E_E1"]
    edge.bridge_current_hp = 1
    sim.ground.request(["S1"], "V_C1", "moto")
    sim.tick(2)                                             # S1 is already crossing E_E1
    sim.bridges.wear(edge)                                  # something else collapses it meanwhile
    assert edge.is_destroyed
    with pytest.raises(AppError):                           # no new crossing can start
        sim.ground.request(["S2"], "V_C1", "moto")
    sim.tick(20)
    assert sim.world.soldiers["S1"].status == SoldierStatus.STATIONED   # the started one finished


def test_soldier_recomputes_route_when_a_bridge_ahead_collapses():
    """BASE -> V_C3 on foot: planned BASE-C4 (E03, 20s) then C4-C3 (E08, 15s)."""
    sim, manager = _ready("escenario_complejo.json", n=1)
    t = sim.ground.request(["S1"], "V_C3", "walk")
    assert t.vertices == ["V_BASE", "V_C4", "V_C3"]
    sim.tick(1)                                             # already walking on E03
    e08 = manager.graph_e.edges["E08"]
    e08.is_destroyed, e08.repair_timer = True, 500          # the bridge AHEAD collapses
    sim.world.version += 1
    sim.tick(30)
    assert sim.world.soldiers["S1"].status == SoldierStatus.MOVING   # it did not stop: it re-planned
    assert t.vertices[0] == "V_C4" and "E08" not in [e.id for e in t.edges]
    sim.tick(40)                                            # 20 s to C4 + 34 s by C1 or C2
    assert sim.world.soldiers["S1"].status == SoldierStatus.STATIONED
    assert sim.world.soldiers["S1"].vertex == "V_C3"


def test_blocked_soldier_resumes_when_connectivity_returns():
    sim, manager = _ready(n=1)
    sim.ground.request(["S1"], "V_C1", "walk")
    sim.tick(1)
    e2 = manager.graph_e.edges["E_E2"]
    e2.is_destroyed, e2.repair_timer = True, 40
    sim.tick(15)
    assert sim.world.soldiers["S1"].status == SoldierStatus.WAITING
    assert sim.world.reserved["V_C1"] == 1                  # its slot stays reserved
    sim.tick(60)                                            # bridge repaired -> retries by itself
    assert sim.world.soldiers["S1"].status == SoldierStatus.STATIONED
    assert sim.world.reserved["V_C1"] == 0


def test_bridge_is_rebuilt_after_the_configured_time_with_full_hp():
    sim, manager = _ready()
    edge = manager.graph_e.edges["E_E3"]
    edge.bridge_current_hp = 1
    sim.bridges.wear(edge)
    assert edge.is_destroyed and edge.bridge_current_hp == 0 and edge.repair_timer == 30.0
    version = sim.world.version
    sim.tick(29)
    assert edge.is_destroyed
    sim.tick(2)
    assert not edge.is_destroyed and edge.bridge_current_hp == edge.bridge_max_hp
    assert sim.world.version > version                      # waiting soldiers are notified
