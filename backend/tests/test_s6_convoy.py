"""Section 6: convoy composition, danger estimate and reactive navigation."""
from math import dist

from conftest import match, station
from src.features.labyrinth.application.danger import damage_rate, update_weights
from src.features.labyrinth.application.router import choose_next
from src.features.labyrinth.domain.entities import CorridorM, VertexM
from src.features.labyrinth.domain.graph_m import GraphM


def test_convoy_composition_hp_and_rewards_come_from_the_json():
    sim, _ = match("escenario_complejo.json")          # 2 tanks, 2 trucks, 4 robots
    stats = {}
    for e in sim.world.enemies:
        stats.setdefault(e.type.value, []).append((e.max_hp, e.reward))
    assert stats["TANK"] == [(200, 150)] * 2
    assert stats["TRUCK"] == [(100, 100)] * 2
    assert stats["ROBOT_SOLDIER"] == [(50, 50)] * 4
    assert len({e.id for e in sim.world.enemies}) == 8  # each machine has its own identity


def test_danger_rate_adds_damage_times_frequency_of_soldiers_in_range():
    defenders = [(0, 0, 10.0, 50, 0.5), (0, 0, 10.0, 10, 1.0), (100, 0, 10.0, 100, 0.2)]
    assert damage_rate((5, 0), defenders) == 50 * 0.5 + 10 * 1.0     # third one is too far
    assert damage_rate((50, 50), defenders) == 0
    assert damage_rate((10, 0), defenders) == 35                     # distance == range counts


def test_corridor_weight_formula_with_three_sample_points():
    sim, manager = match()
    (sid,) = station(sim, "sniper", "V_C1")                # tower at (30, 20), R_ef = 28
    graph, alpha = manager.graph_m, manager.metadata.alpha
    update_weights(graph, sim.world.armed_defenders(), alpha)
    c = graph.corridors["M_C1"]                            # (0,0) -> (30,15)
    points = [(0, 0), (15, 7.5), (30, 15)]
    rates = [25.0 if dist((30, 20), p) <= 28 else 0.0 for p in points]   # 50 dmg * 0.5/s
    expected_p = (sum(rates) / 3) * c.base_time
    assert abs(c.current_danger - expected_p) < 1e-9
    assert abs(c.current_weight - (c.base_time + alpha * expected_p)) < 1e-9


def test_artillery_counts_once_per_soldier_in_the_estimate():
    defenders = [(0, 0, 50.0, 100, 0.2)]                  # one gunner -> 20 dmg/s, however many targets
    assert damage_rate((1, 1), defenders) == 20.0


def test_convoy_avoids_the_defended_branch():
    """A strong defender next to the upper branch must push the route to the lower one."""
    _, manager = match("escenario_complejo.json")
    graph, alpha = manager.graph_m, manager.metadata.alpha
    calm = {c.id: c.base_time for c in graph.corridors.values()}
    first = choose_next(graph, "M_ENTRADA", None, "M_SALIDA", calm)["chosen"]["corridor"]
    # Defender right on the end of the corridor the convoy would take (30,60) / (30,40)
    spot = graph.vertices["M_A" if first == "MC1" else "M_B"].coords
    weights = update_weights(graph, [(spot[0], spot[1], 12.0, 50, 0.5)], alpha)
    decision = choose_next(graph, "M_ENTRADA", None, "M_SALIDA", weights)
    assert decision["chosen"]["corridor"] != first
    assert weights[first] > calm[first]                        # danger raised that corridor


def _line_graph():
    """X -- P (previous) and X -- Y. Y is a dead end unless `exit_beyond` is added."""
    g = GraphM()
    for vid, xy in (("P", (0, 0)), ("X", (10, 0)), ("Y", (20, 0)), ("E", (10, 10))):
        g.add_vertex(VertexM(vid, xy, is_exit=(vid == "E")))
    g.add_corridor(CorridorM("PX", "P", "X", 10, 1))
    g.add_corridor(CorridorM("XY", "X", "Y", 10, 1))
    g.add_corridor(CorridorM("PE", "P", "E", 10, 1))      # the exit is reachable only through P
    g.add_corridor(CorridorM("YE", "Y", "E", 40, 1))      # a long alternative through Y
    return g


def test_backtrack_is_replaced_by_a_different_first_move_when_possible():
    g = _line_graph()
    w = {c.id: c.base_time for c in g.corridors.values()}
    decision = choose_next(g, "X", "P", "E", w)           # best: X->P->E (20) but that goes back
    assert decision["chosen"]["to"] == "Y"                # alternative first move exists (X->Y->E)
    assert "retroceder" in decision["note"].lower()


def test_backtrack_is_allowed_when_there_is_no_other_route():
    g = _line_graph()
    del g.corridors["YE"], g.adj["Y"][1], g.adj["E"][1]    # Y becomes a real dead end
    w = {c.id: c.base_time for c in g.corridors.values()}
    decision = choose_next(g, "X", "P", "E", w)
    # Y only leads back to X, which is a loop; with no route avoiding P the convoy goes back
    assert decision["chosen"]["to"] == "P"


def test_convoy_does_not_change_corridor_in_the_middle_of_it():
    sim, manager = match()
    sim.tick(1.0)                                          # it leaves the entry
    corridor = sim.convoy.corridor
    assert corridor is not None
    station(sim, "sniper", "V_C1", 3)                      # the defense changes while it travels
    for _ in range(8):
        if sim.convoy.corridor is None:
            break
        assert sim.convoy.corridor.id == corridor.id
        sim.tick(0.25)
