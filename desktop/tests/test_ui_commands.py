"""Buying, ordering transports and the clock, using only mouse clicks and key presses."""
import pygame
import pytest

from conftest import Driver
from tardo_ui import theme as t

def test_full_command_flow_with_the_mouse(ready):
    ready.click("Francotirador")
    ready.click("Francotirador")
    assert ready.store.sim["budget"]["available"] == 1400
    ready.click("soldado:S1")
    ready.click("soldado:S2")
    ready.click("dest:V_C1")
    ready.click("medio:moto")
    ready.click("Ver ruta")
    assert ready.store.route_text.endswith("(8.0s)")
    ready.click("Enviar")
    assert ready.store.sim["transfers"] and ready.store.picked == []
    ready.click("+1 s")
    assert ready.store.sim["clock"] == 1.0


def test_buttons_are_disabled_when_the_action_makes_no_sense(ready):
    before = ready.store.sim["budget"]["available"]
    ready.click("Enviar")                                     # nothing picked
    ready.click("Ver ruta")
    assert ready.store.sim["transfers"] == [] and ready.store.sim["budget"]["available"] == before
    for _ in range(4):
        ready.click("Artillero")                              # 4 x 500 = 2000: the fifth purchase is impossible
    ready.click("Artillero")
    assert ready.store.sim["budget"]["available"] == 0 and len(ready.store.sim["soldiers"]) == 4


def test_invalid_order_shows_an_error_toast_and_changes_nothing(ready):
    ready.click("Infantería")
    ready.click("Infantería")
    ready.click("soldado:S1")
    ready.click("soldado:S2")
    ready.click("dest:V_C1")
    ready.click("medio:walk")
    ready.click("Enviar")
    assert ready.store.notice[1] == "error" and "A pie va 1 soldado" in ready.store.notice[0]
    assert ready.store.sim["transfers"] == []


def test_speed_buttons_and_space_bar_control_the_clock(ready):
    ready.click("5x")
    assert ready.store.speed == 5
    ready.key(pygame.K_SPACE)
    assert ready.store.running is True
    clock = ready.store.sim["clock"]
    ready.frame(advance=250)
    assert ready.store.sim["clock"] == pytest.approx(clock + 1.25)
    ready.key(pygame.K_SPACE)
    assert ready.store.running is False


def test_end_banner_buttons(ready):
    ready.play_to_end()
    assert ready.store.sim["status"] == "DEFEAT" and "Jugar de nuevo" in ready.hits
    ready.click("Ver mapa")
    assert "Jugar de nuevo" not in ready.hits
    ready.click("Reiniciar")
    assert ready.store.sim["clock"] == 0 and ready.store.running is False
    ready.play_to_end()
    ready.click("Jugar de nuevo")
    assert ready.store.sim["status"] == "IDLE"


def test_bottom_panel_switches_between_log_and_corridors(ready):
    ready.click("pestaña:corredores")
    assert ready.store.bottom_tab == "corredores"
    ready.click("pestaña:bitacora")
    ready.wheel((300, 700), -5)                               # scrolling the log must not crash
    ready.wheel((300, 700), 10)
    assert ready.store.log_scroll >= 0


def test_destroyed_bridge_and_repair_crew_are_visible():
    d = Driver()
    d.load("escenario_cuadrilla.json")
    d.store.calculate_plan()
    d.go("simulacion")
    for _ in range(3):
        d.click("Infantería")
    d.click("soldado:S1")
    d.click("dest:V_C1")
    d.click("medio:moto")
    d.click("Enviar")
    for _ in range(9):
        d.click("+1 s")                                       # the bridge E_E2 collapses at 8 s
    st = {s["id"]: s["status"] for s in d.store.sim["soldiers"]}
    assert st["S2"] == st["S3"] == "REPAIRING"
    assert d.count_color(t.HOT, pygame.Rect(0, 160, 800, 400)) > 100       # the collapsed bridge is drawn in red
    chips = [k for k in d.hits if k.startswith("soldado:")]
    assert len(chips) == 3


def test_a_modal_blocks_the_screen_behind_it(ui):
    ui.load()
    ui.click("Seleccionar archivo")
    assert ui.app.picker is not None
    ui.go("grafos")                                            # the tab buttons must be ignored while the dialog is open
    assert ui.store.tab == "inicio"
    ui.key(pygame.K_ESCAPE)
    assert ui.app.picker is None
    ui.go("grafos")
    assert ui.store.tab == "grafos"


def test_clicking_the_end_banner_does_not_select_vertices_behind_it(ready):
    ready.play_to_end()
    vp = ready.app.ui.viewport
    x, y = vp.to_screen([30, 20])                                # V_C1 lies under the banner
    assert pygame.Rect(0, 0, 520, 210).move(vp.rect.centerx - 260, vp.rect.centery - 105).collidepoint(x, y)
    ready.click_at((x, y))
    assert ready.store.selected is None
    ready.click("Ver mapa")
    ready.click_at((x, y))
    assert ready.store.selected == {"network": "GE", "id": "V_C1"}      # without the banner it can be picked


def test_a_disabled_button_never_reports_a_click(ready):
    ready.click("Iniciar")                                          # now running: +1 s is disabled
    assert ready.store.running
    clock = ready.store.sim["clock"]
    ready.click("+1 s")
    assert ready.store.sim["clock"] == clock
    from tardo_ui.ui import Ui
    ui = Ui(ready.surface)
    ui.click = (10, 10)
    assert ui.button((0, 0, 50, 30), "x", enabled=False) is False
    assert ui.button((0, 0, 50, 30), "x", enabled=True) is True


def test_loading_another_scenario_clears_selection_route_and_play_state(ready):
    ready.click_at(ready.app.ui.viewport.to_screen([30, 20]))
    ready.store.route_text = "V_BASE > V_C1 (20.0s)"
    ready.store.running = True
    ready.load("escenario_complejo.json")
    s = ready.store
    assert s.selected is None and s.route_text == "" and s.running is False
