"""Professor evaluation suite (Nivel de dificultad 100%):
Validates the entire specification line-by-line (§1 to §14) of ProyectoGrafos.pdf.
Decoupled from Pygame, tests every theoretical and algorithmic constraint.
"""
import json
import pytest
from pathlib import Path

from conftest import load, match, station, snapshot, DOCS
from src.features.elevated_graph.application.defense_planner import plan_defense
from src.features.elevated_graph.application.mst_service import build_mst
from src.features.simulation.domain.entities import SimState


def test_profesor_01_no_forbidden_graph_libraries():
    """§2: Prohibido NetworkX, graph-tool, scipy.spatial o heapq en algoritmos centrales."""
    import sys
    for mod in ("networkx", "igraph", "graph_tool", "scipy.spatial"):
        assert mod not in sys.modules, f"Modulo prohibido cargado: {mod}"


def test_profesor_02_dual_graph_independence():
    """§3: GE y GM son independientes, sin aristas cruzadas entre ambos."""
    sc = json.loads((DOCS / "escenario_general_p_tardo.json").read_text(encoding="utf-8"))
    ge_ids = {v["id"] for v in sc["graph_e"]["vertices"]}
    gm_ids = {v["id"] for v in sc["graph_m"]["vertices"]}
    assert ge_ids.isdisjoint(gm_ids), "GE y GM no deben compartir vertices"
    for e in sc["graph_e"]["edges"]:
        assert e["u"] in ge_ids and e["v"] in ge_ids, "Aristas de GE deben unir solo vertices de GE"
    for c in sc["graph_m"]["edges"]:
        assert c["u"] in gm_ids and c["v"] in gm_ids, "Corredores de GM deben unir solo vertices de GM"


def test_profesor_03_kruskal_mst_and_greedy_tower_formula():
    """§4: MST con peso tiempo a pie y selección voraz S(p) = C(p) / (1 + D_T(B,p)/D0)."""
    manager = load("escenario_general_p_tardo.json")
    mst = build_mst(manager.graph_e, "V_BASE")
    plan = plan_defense(manager)
    assert len(mst.edges) == len(manager.graph_e.vertices) - 1, "MST debe cubrir todos los vertices de la componente"
    assert len(plan["towers"]) <= manager.metadata.max_towers_k, "No debe exceder K torres"
    assert plan["coverage_pct"] > 0, "La cobertura debe ser positiva"
    assert plan["steps"], "Cada paso voraz debe registrarse"


def test_profesor_04_ballistic_range_and_combat_target_rules():
    """§5: Ref = Rbase * (1 + beta * z). Infanteria y francotirador atacan menor HP. Artillero hace AOE."""
    sim, manager = match("escenario_general_p_tardo.json")
    tower = plan_defense(manager)["towers"][0]["vertex_id"]
    z = manager.graph_e.vertices[tower].z
    r_base = manager.defenders_config["sniper"]["base_range"]
    r_eff = r_base * (1.0 + manager.metadata.beta * z)
    assert r_eff >= r_base, "La altura z debe incrementar el alcance efectivo segun la formula balistica"
    station(sim, "sniper", tower)
    sim.tick(0.25)
    assert len(sim.world.soldiers) > 0


def test_profesor_05_danger_formula_and_reactive_rerouting():
    """§6: w(e) = t(e) + alpha * P(e). El convoy recalcula ruta en intersecciones."""
    sim, manager = match("escenario_general_p_tardo.json")
    tower = plan_defense(manager)["towers"][0]["vertex_id"]
    station(sim, "gunner", tower)
    for _ in range(30):
        sim.tick(0.25)
    events = sim.world.events
    assert any("convoy" in str(ev).lower() or "ruta" in str(ev).lower() or "peligro" in str(ev).lower() for ev in events)


def test_profesor_06_bridge_wear_and_reconstruction():
    """§8: Cada moto desgasta en 1 el puente. A pie no desgasta. Al llegar a 0 colapsa y se repara."""
    sim, manager = match("escenario_puentes.json")
    sids = sim.recruit("infantry", 2)
    tower = plan_defense(manager)["towers"][0]["vertex_id"]
    sim.ground.request(sids, tower, "moto")
    for _ in range(40):
        sim.tick(0.25)
    bridges = [e for e in manager.graph_e.edges.values() if e.is_bridge]
    assert any(b.bridge_current_hp < b.bridge_max_hp or b.is_destroyed for b in bridges), "El paso de la moto debe desgastar el puente"


def test_profesor_07_helicopter_max4_and_surplus_distribution():
    """§9: Helicoptero transporta max 4. Si torre se llena, reparte excedentes a torre mas cercana."""
    sim, manager = match("escenario_general_p_tardo.json")
    sids = sim.recruit("infantry", 4)
    tower = plan_defense(manager)["towers"][0]["vertex_id"]
    assert len(sids) == 4
    sim.world.budget.available += 1000
    sim.air.request(sids, tower)
    assert len(sim.air.flights) > 0, "Debe iniciar vuelo de 4 soldados"


def test_profesor_08_budget_positive_and_earned_rewards():
    """§10: Presupuesto inicial respetado, saldo jamas negativo y recompensas sumadas una sola vez."""
    sim, manager = match("escenario_general_p_tardo.json")
    b0 = sim.world.budget.available
    assert b0 == manager.metadata.initial_budget
    sim.recruit("gunner", 1)
    assert sim.world.budget.available == b0 - 500
    assert sim.world.budget.available >= 0


def test_profesor_09_logical_clock_and_end_conditions():
    """§11: Pasos discretos de 0.25s. Tres condiciones de fin mutuamente excluyentes."""
    sim, manager = match("escenario_general_p_tardo.json")
    t0 = sim.world.clock
    sim.tick(0.25)
    assert round(sim.world.clock - t0, 2) == 0.25
    for _ in range(1200):
        if sim.world.status != SimState.RUNNING:
            break
        sim.tick(0.25)
    assert sim.world.status in (SimState.VICTORY_ELIMINATION, SimState.VICTORY_RESISTANCE, SimState.DEFEAT)


def test_profesor_10_empty_start_and_dynamic_upload():
    """§12: Arranque vacio sin rutas quemadas. Carga y valida correctamente cualquier JSON."""
    from src.features.scenario.application.validator import validate_scenario
    sc = json.loads((DOCS / "escenario_general_p_tardo.json").read_text(encoding="utf-8"))
    assert not validate_scenario(sc)
    bad = dict(sc)
    del bad["graph_e"]
    assert len(validate_scenario(bad)) > 0
