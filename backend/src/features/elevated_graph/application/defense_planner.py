"""Defense planning use case: MST first, then greedy tower selection."""
from src.core.errors.handlers import AppError
from src.features.elevated_graph.application.mst_service import build_mst
from src.features.elevated_graph.application.tower_selector import select_towers


def plan_defense(manager) -> dict:
    """Run the whole planning phase and return a JSON-friendly result."""
    base = manager.graph_e.get_base_vertex()
    if base is None:
        raise AppError("El escenario no tiene base", 400)

    mst = build_mst(manager.graph_e, base.id)
    rv = {m["vertex_id"]: float(m["rv"]) for m in manager.candidates_meta}
    meta = manager.metadata
    selection = select_towers(manager.graph_e, manager.graph_m, mst, rv,
                              meta.max_towers_k, meta.d0)

    unreachable = sorted(set(manager.graph_e.vertices) - mst.vertices)
    return {
        "base": base.id,
        "mst": {
            "edges": [{"id": e.id, "u": e.u, "v": e.v, "time_walk": e.time_walk}
                      for e in mst.edges],
            "total_time": mst.total_time,
            "dist_from_base": mst.dist_from_base,
        },
        "unreachable": unreachable,  # outside the base component: cannot be towers
        **selection,
    }
