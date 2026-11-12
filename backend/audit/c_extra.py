"""Audit checks that need a special setup: surplus order with three towers and same-instant priorities."""
import subprocess
import sys
from pathlib import Path

from audit.core import Match, check

ROOT = Path(__file__).resolve().parents[1]


def three_towers(raw):
    """Turn the heliport V_H1 into a third candidate, and add a corridor that only it can watch."""
    heliport = next(v for v in raw["graph_e"]["vertices"] if v["id"] == "V_H1")
    heliport["type"] = "CANDIDATE"
    raw["candidates_meta"].append({"vertex_id": "V_H1", "rv": 12.0})
    raw["graph_m"]["vertices"].append({"id": "M_X", "coords": [90, 45], "is_entry": False, "is_exit": False})
    raw["graph_m"]["edges"].append({"id": "M_C4", "u": "M_N2", "v": "M_X", "length": 40.0, "speed_allowed": 5.0})


@check("§9", "Los excedentes se asignan a las otras torres en orden de distancia euclidiana desde el helicóptero (3 torres)")
def surplus_order(api):
    m = Match(api, edit=three_towers)
    assert sorted(t["vertex_id"] for t in m.state()["towers"]) == ["V_C1", "V_C2", "V_H1"]
    m.buy("infantry", 4)
    m.ok("/transport/helicopter", {"soldier_ids": ["S1", "S2", "S3", "S4"], "dest": "V_C1"})
    towers = {t["vertex_id"]: t["occupants"] for t in m.tick(5)["towers"]}
    # from V_C1 (30,20): V_C2 is 22.4 away and V_H1 is 40 away, so the surplus soldier goes to V_C2
    assert towers == {"V_C1": 3, "V_C2": 1, "V_H1": 0}, towers


@check("§11", "En coincidencias temporales se resuelven primero los ataques, luego la salida y por último el límite de tiempo")
def same_instant_priority(api):
    """The exact instant is built inside the engine, so this runs the unit tests that construct it."""
    run = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_s11_end.py", "-k",
                          "same_instant or before_the_time_limit"], cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 0 and "2 passed" in run.stdout, run.stdout[-200:]
