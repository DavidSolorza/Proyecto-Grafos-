"""Checks again the five defects found in the first review (docs/informe_estado_requisitos.md).

Run from the repository root:  python docs/evidencia_estado/verificar_correcciones.py
Uses an in-process Flask app and an off-screen Pygame surface; it changes no project file.
"""
import json
import logging
import os
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "desktop" / "tests"), str(ROOT / "desktop"), str(ROOT / "backend")]

import tardo_ui.filepicker as filepicker  # noqa: E402
from conftest import Driver  # noqa: E402
from src.features.scenario.application.loader import ScenarioLoader  # noqa: E402
from src.features.scenario.application.session import session  # noqa: E402
from src.features.simulation.application.engine import Simulation  # noqa: E402

logging.disable(logging.CRITICAL)
SIMPLE = ROOT / "docs" / "escenario_general_p_tardo.json"


def raw_simple() -> dict:
    return json.loads(SIMPLE.read_text(encoding="utf-8"))


def started() -> Driver:
    d = Driver()
    d.load()
    d.store.calculate_plan()
    d.go("simulacion")
    return d


FAILED = []


def report(name: str, ok: bool, detail: str) -> None:
    print(f"{'OK   ' if ok else 'FALLA'} {name}: {detail}")
    if not ok:
        FAILED.append(name)


def cancel_dialog() -> None:
    filepicker.choose_native = lambda start=None: (True, None)     # same as pressing "Cancel"
    d = Driver()
    try:
        d.click("Seleccionar archivo")
        d.frame()
        report("H1 cancel file dialog", d.app.picker is None, "closed without errors")
    except Exception as exc:
        report("H1 cancel file dialog", False, f"CRASH {type(exc).__name__}: {exc}")


def actions_after_end() -> None:
    d = started()
    while not d.store.finished:
        d.store.advance(1)
    before = session.simulation.world.budget.available
    res = d.client.post("/api/units/recruit", json={"type": "infantry", "count": 1})
    after = session.simulation.world.budget.available
    report(f"H2 buy after {d.store.sim['status']}", res.status_code == 409 and before == after,
           f"HTTP {res.status_code}, budget {before:.0f} -> {after:.0f}")


def late_replanning() -> None:
    def vertex(i, x, kind):
        return {"id": i, "coords": [x, 10], "type": kind, "z": 0}

    def edge(i, u, v, t, hp=None):
        bridge = {"bridge_max_hp": hp, "bridge_current_hp": hp} if hp else {}
        return {"id": i, "u": u, "v": v, "time_walk": t, "time_moto": t, **bridge}

    raw = raw_simple()
    raw["graph_e"] = {
        "vertices": [vertex("B", 10, "BASE"), vertex("M1", 20, "TRANSIT"),
                     vertex("M2", 30, "TRANSIT"), vertex("T", 40, "CANDIDATE")],
        "edges": [edge("e1", "B", "M1", 5), edge("e2", "M1", "M2", 5),
                  edge("e3", "M2", "T", 5, 1), edge("e4", "M1", "T", 12)]}
    raw["candidates_meta"] = [{"vertex_id": "T", "rv": 1000}]
    manager = ScenarioLoader.load_from_dict(raw)
    for corridor in manager.graph_m.corridors.values():
        corridor.speed_allowed = 0.001                      # freeze the convoy
    sim = Simulation(manager, {"towers": [{"vertex_id": "T", "rv": 1000}]})
    sim.recruit("infantry", 1)
    sim.ground.request(["S1"], "T", "walk")
    sim.tick(1)
    bridge = manager.graph_e.edges["e3"]
    bridge.is_destroyed, bridge.repair_timer = True, 1000
    sim.world.version += 1
    while sim.world.soldiers["S1"].status.value != "STATIONED" and sim.world.clock < 100:
        sim.tick(0.25)
    report("H3 bridge collapses ahead", sim.world.clock == 17,
           f"arrives at t={sim.world.clock:g}s (expected 17s)")


def malformed_json() -> None:
    d = Driver()
    raw = raw_simple()
    raw["graph_e"]["vertices"].append(5)
    res = d.client.post("/api/scenario/upload", json=raw)
    report("H4 vertex that is not an object", res.status_code == 400, f"HTTP {res.status_code} (expected 400)")


def too_many_soldiers() -> None:
    d = started()
    for _ in range(14):
        d.store.recruit("infantry")
    d.frame()
    seen = set()
    for _ in range(3):                                      # walk through every page
        seen |= {k for k in d.hits if k.startswith("soldado:")}
        if "soldados:next" in d.hits:
            d.click("soldados:next")
    bought = len(d.store.sim["soldiers"])
    report("H5 Pygame soldiers", len(seen) == bought, f"{bought} bought, {len(seen)} selectable")


if __name__ == "__main__":
    for check in (cancel_dialog, actions_after_end, late_replanning, malformed_json, too_many_soldiers):
        check()
    raise SystemExit(1 if FAILED else 0)
