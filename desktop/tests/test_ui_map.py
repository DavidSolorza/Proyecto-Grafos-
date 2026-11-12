"""The map: one viewport fits both graphs, vertices can be picked, and the layers draw the right things."""
import json

import pygame

from conftest import DOCS, Driver
from tardo_ui import theme as t
from tardo_ui.map.view import Viewport

SCENARIO = json.loads(__import__("pathlib").Path(DOCS / "escenario_general_p_tardo.json").read_text(encoding="utf-8"))


def scenario_dict():
    """Same shape the API returns for the active scenario."""
    return {"graph_e": {"vertices": SCENARIO["graph_e"]["vertices"]}, "graph_m": {"vertices": SCENARIO["graph_m"]["vertices"]}}


def test_every_vertex_of_both_graphs_is_inside_the_rect():
    rect = pygame.Rect(40, 60, 700, 400)
    vp = Viewport(rect, scenario_dict())
    for graph in ("graph_e", "graph_m"):
        for v in SCENARIO[graph]["vertices"]:
            x, y = vp.to_screen(v["coords"])
            assert rect.collidepoint(x, y)


def test_aspect_ratio_is_preserved_and_content_is_centered():
    for rect in (pygame.Rect(0, 0, 1000, 200), pygame.Rect(0, 0, 200, 1000), pygame.Rect(0, 0, 600, 600)):
        vp = Viewport(rect, scenario_dict())
        a, b = vp.to_screen([0, 0]), vp.to_screen([100, 0])
        c = vp.to_screen([0, 100])
        assert abs((b[0] - a[0]) - (c[1] - a[1])) <= 2             # same scale on both axes
        assert vp.scale > 0


def test_pick_returns_the_nearest_vertex_within_reach_only():
    vp = Viewport(pygame.Rect(0, 0, 900, 500), scenario_dict())
    x, y = vp.to_screen([50, 10])                                    # V_C2
    assert vp.pick(scenario_dict(), "both", (x + 5, y - 4))[1]["id"] == "V_C2"
    assert vp.pick(scenario_dict(), "both", (x + 60, y + 60)) is None
    assert vp.pick(scenario_dict(), "gm", (x, y)) is None                # V_C2 is not pickable in the GM layer


def test_layers_show_only_what_was_asked():
    d = Driver()
    d.load()
    d.go("grafos")
    area = d.app.ui.viewport.rect
    d.click("Red elevada GE")
    only_ge_rust = d.count_color(t.RUST, area)
    d.click("Laberinto GM")
    only_gm_rust, gm_soldier_base = d.count_color(t.RUST, area), d.count_color((240, 231, 214), area)
    d.click("Ambas capas")
    assert only_ge_rust == 0 and only_gm_rust > 300                    # corridors exist only in the GM layer
    assert gm_soldier_base == 0                                        # the base square belongs to GE


def test_the_convoy_and_soldiers_are_drawn_during_the_match(ready):
    area = lambda: ready.app.ui.viewport.rect  # noqa: E731
    assert ready.count_color(t.HOT, area()) > 200                      # convoy marker on the entry
    before = ready.count_color(t.LEAF, area())                          # only the labyrinth entry marker is leaf-green
    ready.click("Infantería")
    assert ready.count_color(t.LEAF, area()) - before > 100              # a soldier appeared at the base


def test_corridor_danger_turns_the_corridors_hotter(ready):
    ready.click("Francotirador")
    ready.click("soldado:S1")
    ready.click("dest:V_C1")
    ready.click("medio:moto")
    ready.click("Enviar")
    for _ in range(9):
        ready.click("+1 s")
    danger = {c["id"]: c["danger"] for c in ready.store.sim["corridors"]}
    assert danger["M_C1"] > 0                                            # the sniper now covers the first corridor
    assert ready.count_color(t.heat(danger["M_C1"] / max(danger.values())), ready.app.ui.viewport.rect) > 20


def test_map_without_scenario_says_so(ui):
    ui.go("grafos")
    assert ui.app.ui.viewport is None                                  # no scenario: no map drawn
    assert "ir a inicio" in ui.hits


def test_bridge_labels_tell_health_repair_time_and_missing_crew():
    from tardo_ui.map.layers import bridge_label
    ok = {"destroyed": False, "hp": 2, "max_hp": 3}
    assert bridge_label(ok) == ("2/3", t.MAP_TEXT)
    down = {"destroyed": True, "repair_left": 29.5, "waiting_crew": False}
    assert bridge_label(down) == ("X 29.5s", t.HOT)
    assert bridge_label({**down, "waiting_crew": True}) == ("X sin cuadrilla", t.HOT)
