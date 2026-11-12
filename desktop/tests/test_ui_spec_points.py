"""Statement points that the interface must show: the initial cheapest route (3) and the watched corridors (4)."""
import pygame

from conftest import Driver
from tardo_ui import theme as t


def test_graphs_screen_shows_and_highlights_the_initial_cheapest_route(ui):
    ui.load()
    ui.go("grafos")
    area = ui.app.ui.viewport.rect
    text = " ".join(ui.texts())
    assert "M_ENTRADA > M_N1 > M_N2 > M_SALIDA  (t = 23s)" in text
    assert ui.count_color(t.OCHRE, area) > 300                  # the route band is drawn under the corridors
    ui.click("Camino inicial")
    assert ui.count_color(t.OCHRE, area) == 0
    ui.click("Camino inicial")
    ui.click("Red elevada GE")                                   # corridors belong to GM: the route disappears with them
    assert ui.count_color(t.OCHRE, area) == 0


def test_home_summary_includes_the_route_and_its_cost(ui):
    ui.load("escenario_complejo.json")
    route = ui.store.scenario["initial_route"]
    assert any(f"t = {round(route['cost'], 2):g}s" in line and "M_ENTRADA" in line for line in ui.texts())


def test_plan_screen_lists_the_watched_corridors_and_total_coverage(ui):
    ui.load()
    ui.go("plan")
    ui.click("Calcular plan")
    text = " | ".join(ui.texts())
    assert "Corredores vigilados: 3 de 3 (115 de 115 u. de longitud)" in text
    assert "M_C1, M_C2, M_C3" in text
    assert "Iteración 1: gana V_C1  ·  vigila ahora: M_C1, M_C2" in text          # C = 40 + 35 = 75
    assert "Iteración 2: gana V_C2  ·  vigila ahora: M_C3" in text                 # only the corridor still uncovered


def test_plan_of_the_complex_scenario_reports_partial_coverage():
    d = Driver()
    d.load("escenario_complejo.json")
    d.go("plan")
    d.click("Calcular plan")
    plan, total = d.store.plan, len(d.store.scenario["graph_m"]["corridors"])
    head = f"Corredores vigilados: {len(plan['covered_corridors'])} de {total}"
    assert any(head in line for line in d.texts()) and len(plan["covered_corridors"]) < total   # 72.2 %: not everything is watched
