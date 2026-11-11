"""Shared helpers for the requirement tests (one test file per section of the statement)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.core.config.settings import settings
from src.features.elevated_graph.application.defense_planner import plan_defense
from src.features.scenario.application.loader import ScenarioLoader
from src.features.simulation.application.engine import Simulation

DOCS = settings.ROOT_PROJECT_DIR / "docs"


def load(name: str = "escenario_general_p_tardo.json", edit=None):
    """Load a scenario from docs/. `edit(raw)` can modify the JSON first."""
    raw = json.loads((DOCS / name).read_text(encoding="utf-8"))
    if edit:
        edit(raw)
    return ScenarioLoader.load_from_dict(raw)


def match(name: str = "escenario_general_p_tardo.json", edit=None):
    """Return (simulation, manager) with the plan already calculated."""
    manager = load(name, edit)
    return Simulation(manager, plan_defense(manager)), manager


def slow_convoy(manager, speed: float = 0.001):
    """Freeze the convoy so a test can study transport and bridges alone."""
    for c in manager.graph_m.corridors.values():
        c.speed_allowed = speed


def station(sim, kind: str, tower: str, n: int = 1):
    """Buy soldiers and place them in a tower instantly (skips the trip)."""
    from src.features.simulation.domain.units import SoldierStatus
    ids = sim.recruit(kind, n)
    for sid in ids:
        s = sim.world.soldiers[sid]
        s.vertex, s.xy = tower, sim.world.coords(tower)
        s.status = SoldierStatus.STATIONED
        s.next_attack = 0.0
    return ids


def snapshot(sim):
    """Everything a failed request must leave untouched."""
    w = sim.world
    return (w.budget.available, w.budget.reserved, dict(w.reserved),
            {i: (s.status, s.vertex) for i, s in w.soldiers.items()},
            len(sim.ground.transfers), len(sim.air.flights), sim.air.uses)


@pytest.fixture
def simple():
    return match()


@pytest.fixture
def complex_():
    return match("escenario_complejo.json")


def edit_edge(eid, **changes):
    def apply(raw):
        for e in raw["graph_e"]["edges"]:
            if e["id"] == eid:
                e.update(changes)
    return apply


def crew_match(crew=2, edit=None):
    def apply(raw):
        raw["metadata"]["bridge_repair_crew"] = crew
        if edit:
            edit(raw)
    sim, manager = match("escenario_cuadrilla.json", apply)
    slow_convoy(manager)                        # keep the match alive: only bridges matter here
    return sim, manager


def collapse(sim, eid="E_E2"):
    edge = sim.world.manager.graph_e.edges[eid]
    edge.bridge_current_hp = 1
    sim.bridges.wear(edge)
    assert edge.is_destroyed
    return edge
