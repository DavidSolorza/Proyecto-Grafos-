"""Validation of scalar parameters: metadata, candidates, convoy, defenders, helicopter."""


def _num(x) -> bool:
    from math import isfinite
    return isinstance(x, (int, float)) and not isinstance(x, bool) and isfinite(x)


def check_parameters(raw: dict, ge_ids: set, errors: list) -> None:
    meta = raw["metadata"]
    # (key, minimum, strictly greater than minimum?)
    for key, low, strict in (("D0", 0, True), ("alpha", 0, False), ("beta", 0, False),
                             ("initial_budget", 0, False), ("bridge_repair_time", 0, True),
                             ("time_limit", 0, True)):
        if key in meta and (not _num(meta[key]) or (meta[key] <= low if strict else meta[key] < low)):
            errors.append(f"metadata.{key} debe ser {'mayor que' if strict else 'mayor o igual a'} {low}")
    crew = meta.get("bridge_repair_crew", 0)
    if not isinstance(crew, int) or isinstance(crew, bool) or crew < 0:
        errors.append("metadata.bridge_repair_crew debe ser un entero >= 0")
    k = meta.get("max_towers_K", 3)
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        errors.append("metadata.max_towers_K debe ser un entero positivo")

    types = {v.get("id"): v.get("type") for v in raw["graph_e"].get("vertices", []) if isinstance(v, dict)}
    for m in raw.get("candidates_meta", []):
        vid = m.get("vertex_id") if isinstance(m, dict) else None
        if types.get(vid) != "CANDIDATE":
            errors.append(f"candidates_meta: '{vid}' no es un vértice CANDIDATE")
        if not _num(m.get("rv")) or m["rv"] <= 0:
            errors.append(f"candidates_meta: el radio rv de '{vid}' debe ser positivo")

    convoy = raw["convoy"]
    counts = [convoy.get(k, 0) for k in ("tanks", "trucks", "robot_soldiers")]
    if any(not isinstance(c, int) or isinstance(c, bool) or c < 0 for c in counts):
        errors.append("convoy: las cantidades deben ser enteros >= 0")
    elif sum(counts) == 0:
        errors.append("convoy: debe tener al menos una máquina")

    for kind in ("infantry", "sniper", "gunner"):
        cfg = raw["defenders_config"].get(kind)
        if not isinstance(cfg, dict):
            errors.append(f"defenders_config: falta '{kind}'")
            continue
        for key in ("cost", "damage", "base_range", "frequency"):
            if not _num(cfg.get(key)) or cfg[key] <= 0:
                errors.append(f"defenders_config.{kind}.{key} debe ser positivo")

    heli = raw.get("helicopter", {})
    if not isinstance(heli, dict) or any(
            key in heli and (not _num(heli[key]) or heli[key] < 0) for key in ("speed", "cost", "max_uses")):
        errors.append("helicopter: speed, cost y max_uses deben ser números >= 0")
    elif "speed" in heli and heli["speed"] == 0:
        errors.append("helicopter.speed debe ser mayor que 0")
