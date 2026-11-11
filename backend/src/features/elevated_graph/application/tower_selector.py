"""Greedy tower selection: S(p) = C(p) / (1 + D_T(B,p) / D0)."""
from math import dist as euclid
from src.features.elevated_graph.application.mst_service import MstResult
from src.features.elevated_graph.domain.entities import PositionType
from src.features.elevated_graph.domain.graph_e import GraphE
from src.features.labyrinth.domain.graph_m import GraphM


def corridor_midpoint(graph_m: GraphM, corridor) -> tuple[float, float]:
    """Middle point of a corridor, computed from its two end vertices."""
    a = graph_m.vertices[corridor.u].coords
    b = graph_m.vertices[corridor.v].coords
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def select_towers(graph_e: GraphE, graph_m: GraphM, mst: MstResult,
                  rv_by_vertex: dict[str, float], k: int, d0: float) -> dict:
    """Pick up to k candidates, one per iteration, recomputing the uncovered length."""
    corridors = graph_m.corridors
    mids = {cid: corridor_midpoint(graph_m, c) for cid, c in corridors.items()}

    # Only candidates inside the base component can be chosen
    candidates = [
        v for v in graph_e.vertices.values()
        if v.type == PositionType.CANDIDATE and v.id in mst.vertices
    ]
    watches = {  # candidate -> corridors whose midpoint is inside its radius Rv
        v.id: {cid for cid, m in mids.items() if euclid(v.coords, m) <= rv_by_vertex.get(v.id, 0.0)}
        for v in candidates
    }

    uncovered = set(corridors)
    chosen: list[dict] = []
    steps: list[dict] = []

    while len(chosen) < k:
        taken = {t["vertex_id"] for t in chosen}
        scores = []
        for v in candidates:
            if v.id in taken:
                continue
            gain = sum(corridors[cid].length for cid in watches[v.id] & uncovered)
            dt = mst.dist_from_base[v.id]
            scores.append({"vertex_id": v.id, "gain": gain, "dt": dt,
                           "score": gain / (1 + dt / d0)})

        positive = [s for s in scores if s["score"] > 0]
        if not positive:
            break  # no candidate adds new coverage
        # Highest score; ties -> smaller tree distance -> smaller id
        best = min(positive, key=lambda s: (-round(s["score"], 9), s["dt"], s["vertex_id"]))
        new = sorted(watches[best["vertex_id"]] & uncovered)
        uncovered -= set(new)
        chosen.append({**best, "rv": rv_by_vertex[best["vertex_id"]], "new_corridors": new})
        steps.append({"iteration": len(chosen), "scores": scores,
                      "chosen": best["vertex_id"], "new_corridors": new})

    covered = sorted(set(corridors) - uncovered)
    total = sum(c.length for c in corridors.values())
    covered_len = sum(corridors[cid].length for cid in covered)
    return {
        "towers": chosen,
        "steps": steps,
        "covered_corridors": covered,
        "covered_length": covered_len,
        "total_length": total,
        "coverage_pct": round(100 * covered_len / total, 1) if total else 0.0,
    }
