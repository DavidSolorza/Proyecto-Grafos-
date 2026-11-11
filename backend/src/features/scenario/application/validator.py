"""Validation of the raw scenario JSON (statement sections 3 and 12).

Everything is checked BEFORE building the graphs, so a bad file never
reaches the algorithms. Messages are in Spanish because the user reads them.
"""
from math import isfinite
from src.features.elevated_graph.domain.entities import PositionType
from src.features.scenario.application.validator_params import check_parameters


def is_num(x) -> bool:
    """True for finite numbers (bool is not accepted even though it is an int)."""
    return isinstance(x, (int, float)) and not isinstance(x, bool) and isfinite(x)


def _coords_ok(c, positive: bool) -> bool:
    return (isinstance(c, list) and len(c) == 2 and all(is_num(v) for v in c)
            and (not positive or all(v > 0 for v in c)))


def _ids(items, label, errors) -> set:
    """Collect ids and report missing or repeated ones."""
    seen: set = set()
    for item in items:
        iid = item.get("id") if isinstance(item, dict) else None
        if not isinstance(iid, str) or not iid:
            errors.append(f"{label}: hay un elemento sin id válido")
        elif iid in seen:
            errors.append(f"{label}: el id '{iid}' está repetido")
        else:
            seen.add(iid)
    return seen


def _check_ge(ge: dict, errors: list) -> set:
    verts, edges = ge.get("vertices"), ge.get("edges")
    if not isinstance(verts, list) or not isinstance(edges, list):
        errors.append("graph_e debe tener las listas 'vertices' y 'edges'")
        return set()
    ids = _ids(verts, "GE vértices", errors)
    for v in verts:
        if not _coords_ok(v.get("coords"), positive=True):
            errors.append(f"GE {v.get('id')}: las coordenadas deben ser dos números finitos positivos")
        if v.get("type") not in PositionType.__members__:
            errors.append(f"GE {v.get('id')}: tipo inválido (BASE, CANDIDATE, TRANSIT o HELIPORT)")
        if not is_num(v.get("z", 0.0)) or v.get("z", 0.0) < 0:
            errors.append(f"GE {v.get('id')}: la altura z debe ser un número >= 0")
    if sum(1 for v in verts if v.get("type") == "BASE") != 1:
        errors.append("GE: debe haber exactamente una BASE")

    _ids(edges, "GE aristas", errors)
    for e in edges:
        if e.get("u") not in ids or e.get("v") not in ids or e.get("u") == e.get("v"):
            errors.append(f"GE {e.get('id')}: une vértices que no existen o un vértice consigo mismo")
        times = [e.get(key) for key in ("time_walk", "time_moto")]
        for key, t in zip(("time_walk", "time_moto"), times):
            if t is not None and (not is_num(t) or t <= 0):          # null = transport not allowed
                errors.append(f"GE {e.get('id')}: {key} debe ser positivo (o null si el medio no se permite)")
        if all(t is None for t in times):
            errors.append(f"GE {e.get('id')}: debe permitir al menos un medio (time_walk o time_moto)")
        if e.get("bridge_max_hp") is not None or e.get("bridge_current_hp") is not None:   # it is a bridge
            mx = e.get("bridge_max_hp")
            cur = e.get("bridge_current_hp", mx)
            if not (isinstance(mx, int) and isinstance(cur, int) and 0 < cur <= mx):
                errors.append(f"GE {e.get('id')}: la resistencia del puente debe ser entera, positiva y actual <= máxima")
    return ids


def _check_gm(gm: dict, errors: list) -> None:
    verts, cors = gm.get("vertices"), gm.get("edges")
    if not isinstance(verts, list) or not isinstance(cors, list):
        errors.append("graph_m debe tener las listas 'vertices' y 'edges'")
        return
    ids = _ids(verts, "GM vértices", errors)
    for v in verts:
        if not _coords_ok(v.get("coords"), positive=False):
            errors.append(f"GM {v.get('id')}: las coordenadas deben ser dos números finitos")
    entries = [v for v in verts if v.get("is_entry")]
    exits = [v for v in verts if v.get("is_exit")]
    if len(entries) != 1 or len(exits) != 1:
        errors.append("GM: debe haber exactamente una entrada y una salida")
    elif entries[0].get("id") == exits[0].get("id"):
        errors.append("GM: la entrada y la salida deben ser vértices diferentes")

    _ids(cors, "GM corredores", errors)
    for c in cors:
        if c.get("u") not in ids or c.get("v") not in ids or c.get("u") == c.get("v"):
            errors.append(f"GM {c.get('id')}: une vértices que no existen o un vértice consigo mismo")
        for key in ("length", "speed_allowed"):
            if not is_num(c.get(key)) or c[key] <= 0:
                errors.append(f"GM {c.get('id')}: {key} debe ser positivo")


def validate_scenario(raw) -> list[str]:
    """Return every problem found (empty list = valid scenario)."""
    if not isinstance(raw, dict):
        return ["El JSON debe ser un objeto con graph_e, graph_m, convoy..."]
    errors: list[str] = []
    for key in ("metadata", "graph_e", "graph_m", "convoy", "defenders_config"):
        if not isinstance(raw.get(key), dict):
            errors.append(f"Falta la sección '{key}'")
    if errors:
        return errors
    ge_ids = _check_ge(raw["graph_e"], errors)
    _check_gm(raw["graph_m"], errors)
    check_parameters(raw, ge_ids, errors)
    return errors
