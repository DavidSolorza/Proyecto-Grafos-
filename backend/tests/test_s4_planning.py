"""Section 4: minimum spanning tree and tower selection."""
from itertools import combinations

from conftest import load
from src.features.elevated_graph.application.defense_planner import plan_defense
from src.features.elevated_graph.application.mst_service import build_mst
from src.features.elevated_graph.application.tower_selector import select_towers
from src.features.elevated_graph.domain.entities import PositionType, VertexE, EdgeE
from src.features.elevated_graph.domain.graph_e import GraphE
from src.features.labyrinth.domain.entities import CorridorM, VertexM
from src.features.labyrinth.domain.graph_m import GraphM


def test_mst_weight_is_the_true_minimum():
    """Compare Kruskal against every possible set of V-1 edges (brute force)."""
    g = load("escenario_complejo.json").graph_e
    comp = g.get_connected_component("V_BASE")
    edges = [e for e in g.edges.values() if e.u in comp and e.v in comp]

    def spans(subset):
        reach, changed = {"V_BASE"}, True
        while changed:
            changed = False
            for e in subset:
                if (e.u in reach) != (e.v in reach):
                    reach |= {e.u, e.v}
                    changed = True
        return reach == comp

    best = min(sum(e.time_walk for e in s) for s in combinations(edges, len(comp) - 1) if spans(s))
    assert build_mst(g, "V_BASE").total_time == best


def test_mst_covers_component_only_and_keeps_other_edges_in_graph():
    manager = load("escenario_complejo.json")
    mst = build_mst(manager.graph_e, "V_BASE")
    assert mst.vertices == manager.graph_e.get_connected_component("V_BASE")
    assert "V_ISLA" not in mst.vertices
    assert len(mst.edges) == len(mst.vertices) - 1
    assert len(manager.graph_e.edges) == 11          # the tree does not delete edges


def test_tree_distance_follows_tree_edges_not_shortcuts():
    manager = load("escenario_complejo.json")
    mst = build_mst(manager.graph_e, "V_BASE")
    # V_C4 is joined to the base by E03 (20s) in the graph, but the tree does not use it
    ids = {e.id for e in mst.edges}
    assert "E03" not in ids
    # exact value: BASE -E01-> T1 (14) -E04-> C1 (12) -E06-> C4 (12) = 38
    assert mst.dist_from_base["V_C4"] == 38.0


def test_mst_is_deterministic_with_equal_weights():
    manager = load("escenario_complejo.json")
    first = [e.id for e in build_mst(manager.graph_e, "V_BASE").edges]
    for _ in range(5):
        assert [e.id for e in build_mst(manager.graph_e, "V_BASE").edges] == first


def test_towers_respect_k_component_and_stop_when_no_new_coverage():
    manager = load("escenario_complejo.json")
    manager.metadata.max_towers_k = 1
    assert len(plan_defense(manager)["towers"]) == 1
    manager.metadata.max_towers_k = 10               # more than useful candidates
    plan = plan_defense(manager)
    ids = [t["vertex_id"] for t in plan["towers"]]
    assert len(ids) < 10 and "V_ISLA" not in ids and len(set(ids)) == len(ids)
    assert all(t["gain"] > 0 for t in plan["towers"])  # each tower adds coverage


def _tiny_world(rv):
    """Base + 2 candidates and 2 corridors, built by hand to force ties."""
    ge, gm = GraphE(), GraphM()
    ge.add_vertex(VertexE("B", (1.0, 1.0), PositionType.BASE))
    ge.add_vertex(VertexE("P1", (50.0, 0.0), PositionType.CANDIDATE))
    ge.add_vertex(VertexE("P2", (0.0, 50.0), PositionType.CANDIDATE))
    ge.add_edge(EdgeE("e1", "B", "P1", 30.0, 1.0))
    ge.add_edge(EdgeE("e2", "B", "P2", 10.0, 1.0))
    for vid, xy in (("a", (50, 0)), ("b", (50, 20)), ("c", (0, 50)), ("d", (0, 60))):
        gm.add_vertex(VertexM(vid, xy))
    gm.add_corridor(CorridorM("c1", "a", "b", 60.0, 1.0))   # midpoint (50, 10)
    gm.add_corridor(CorridorM("c2", "c", "d", 30.0, 1.0))   # midpoint (0, 55)
    return ge, gm, build_mst(ge, "B"), {"P1": rv, "P2": rv}


def test_tie_in_score_goes_to_smaller_tree_distance_then_id():
    ge, gm, mst, rv = _tiny_world(rv=15.0)
    # P1: C=60, D_T=30 -> 60/(1+30/10)=15 ; P2: C=30, D_T=10 -> 30/(1+10/10)=15  (tie)
    plan = select_towers(ge, gm, mst, rv, k=1, d0=10.0)
    assert plan["towers"][0]["vertex_id"] == "P2"           # smaller D_T wins the tie


def test_tie_in_score_and_distance_goes_to_lexicographic_id():
    ge, gm, mst, rv = _tiny_world(rv=15.0)
    ge.edges["e1"].time_walk = 10.0                        # now both at D_T = 10
    mst = build_mst(ge, "B")
    gm.corridors["c1"].length = 30.0                       # both gain 30 -> equal scores
    plan = select_towers(ge, gm, mst, rv, k=1, d0=10.0)
    assert plan["towers"][0]["vertex_id"] == "P1"           # "P1" < "P2"


def test_corridor_is_watched_when_midpoint_distance_equals_rv():
    ge, gm, mst, _ = _tiny_world(rv=0)
    # P1 -> midpoint of c1 is exactly 10 away, so Rv = 10 must include it
    plan = select_towers(ge, gm, mst, {"P1": 10.0, "P2": 0.0}, k=2, d0=10.0)
    assert [t["vertex_id"] for t in plan["towers"]] == ["P1"]
    assert plan["covered_corridors"] == ["c1"]
    assert plan["coverage_pct"] == round(100 * 60 / 90, 1)
