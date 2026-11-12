"""The four screens, driven only with simulated mouse clicks and key presses (like a user would)."""
import pygame
import pytest

from conftest import Driver
from tardo_ui import theme as t


@pytest.mark.parametrize("size", [(1360, 820), (1180, 700), (1920, 1080)])
def test_every_screen_draws_at_several_window_sizes(size):
    d = Driver(size)
    d.load("escenario_complejo.json")
    d.store.calculate_plan()
    d.store.recruit("sniper")
    for tab in ("inicio", "grafos", "plan", "simulacion"):
        d.go(tab)
        d.frame()
        assert d.store.tab == tab


def test_empty_start_guides_the_user_to_load_a_scenario(ui):
    for tab in ("grafos", "plan", "simulacion"):
        ui.go(tab)
        assert "ir a inicio" in ui.hits                       # placeholder with a way back
    ui.click("ir a inicio")
    assert ui.store.tab == "inicio" and "Seleccionar archivo" in ui.hits


def test_tabs_and_layer_buttons(ui):
    ui.load()
    ui.go("grafos")
    for key, label in (("ge", "Red elevada GE"), ("gm", "Laberinto GM"), ("both", "Ambas capas")):
        ui.click(label)
        assert ui.store.layers == key


def test_clicking_a_vertex_on_the_map_selects_it(ui):
    ui.load()
    ui.go("grafos")
    vp = ui.app.ui.viewport
    ui.click_at(vp.to_screen([30, 20]))                      # V_C1
    assert ui.store.selected == {"network": "GE", "id": "V_C1"}
    ui.click_at(vp.to_screen([90, 0]))                       # M_SALIDA, a vertex of the other graph
    assert ui.store.selected == {"network": "GM", "id": "M_SALIDA"}
    ui.click_at((vp.rect.x + 4, vp.rect.y + 4))              # empty corner of the map
    assert ui.store.selected is None
    ui.click("Red elevada GE")
    ui.click_at(vp.to_screen([90, 0]))                       # GM vertices cannot be picked while hidden
    assert ui.store.selected is None


def test_plan_screen_buttons(ui):
    ui.load()
    ui.go("plan")
    assert ui.hits["Árbol"] and ui.store.plan is None
    ui.click("Calcular plan")
    assert ui.store.plan and ui.store.sim
    ui.click("Árbol")
    assert ui.store.show_tree is False
    ui.click("Radios")
    assert ui.store.show_radii is False
    ui.click("Árbol")
    assert ui.store.show_tree is True


def test_plan_draws_tree_radii_and_towers(ui):
    ui.load()
    ui.go("plan")
    ui.click("Calcular plan")
    area = ui.app.ui.viewport.rect
    gold, leaf = ui.count_color(t.GOLD, area), ui.count_color(t.LEAF, area)
    assert leaf > 300 and gold > 500                                          # green tree and gold towers
    inside = ui.app.ui.viewport.to_screen([40, 30])                           # 14 units from V_C1, inside Rv = 25
    tinted = tuple(ui.surface.get_at(inside))                                 # the radius tints the stage background
    ui.click("Árbol")
    ui.click("Radios")
    # the entry marker of the labyrinth is also leaf-green (about 110 px), so compare with that baseline
    assert leaf - ui.count_color(t.LEAF, area) > 200                          # tree and covered-corridor dots hidden
    assert tuple(ui.surface.get_at(inside)) != tinted                         # the translucent radius is gone too


def test_simulation_needs_a_plan_first(ui):
    ui.load()
    ui.go("simulacion")
    assert "ir al plan" in ui.hits
    ui.click("ir al plan")
    assert ui.store.tab == "plan"
