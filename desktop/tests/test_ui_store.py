"""The controller of the Pygame client: every operation goes through the Flask API."""
import json

import pytest

from conftest import DOCS, Driver, FlaskTransport
from tardo_ui.api import ApiClient, ApiError, HttpTransport
from tardo_ui.store import SYNC_MS, TICK_MS, Store


def test_starts_empty_and_connected(ui):
    s = ui.store
    assert s.backend_ok and s.scenario is None and s.plan is None and s.sim is None and s.tab == "inicio"


def test_loading_a_json_chosen_by_the_user(ui):
    assert ui.store.load_file(DOCS / "escenario_complejo.json")
    assert "complejo" in ui.store.scenario["metadata"]["title"] and ui.store.validation["has_base"]
    assert ui.store.notice[1] == "ok"


@pytest.mark.parametrize("content,message", [("esto no es json", "JSON válido"), ("{}", "Falta la sección"),
                                              (json.dumps({"metadata": {}, "graph_e": {}, "graph_m": {}, "convoy": {},
                                                           "defenders_config": {}}), "graph_e debe tener")])
def test_a_bad_file_shows_the_reason_and_keeps_the_old_scenario(ui, tmp_path, content, message):
    ui.load()
    title = ui.store.scenario["metadata"]["title"]
    bad = tmp_path / "malo.json"
    bad.write_text(content, encoding="utf-8")
    assert ui.store.load_file(bad) is False
    assert message in ui.store.notice[0] and ui.store.notice[1] == "error"
    assert ui.store.scenario["metadata"]["title"] == title


def test_a_missing_file_is_reported(ui, tmp_path):
    assert ui.store.load_file(tmp_path / "no_existe.json") is False
    assert "No se pudo leer" in ui.store.notice[0]


def test_plan_matches_the_known_numbers(ui):
    ui.load()
    ui.store.calculate_plan()
    plan = ui.store.plan
    assert ui.store.tower_ids == ["V_C1", "V_C2"] and plan["coverage_pct"] == 100.0 and plan["mst"]["total_time"] == 45.0
    assert [round(t["score"], 2) for t in plan["towers"]] == [53.57, 23.53]
    assert ui.store.sim is not None and ui.store.sim["clock"] == 0          # a match is created with the plan


def test_planning_without_scenario_or_after_the_fight_began_explains_why(ui):
    ui.store.calculate_plan()
    assert "carga un escenario" in ui.store.notice[0]
    ui.load()
    ui.store.calculate_plan()
    ui.store.advance(1)
    ui.store.calculate_plan()
    assert "no se pueden reubicar" in ui.store.notice[0]


def test_buying_moving_and_route_consultation(ready):
    s = ready.store
    s.recruit("sniper")
    s.recruit("sniper")
    assert s.sim["budget"]["available"] == 1400
    s.toggle_pick("S1")
    s.dest, s.mode = "V_C1", "walk"
    s.show_route()
    assert s.route_text == "V_BASE > V_T1 > V_C1 (20.0s)"
    s.mode = "moto"
    s.show_route()
    assert s.route_text.endswith("(8.0s)")
    s.send()
    assert s.picked == [] and s.sim["transfers"][0]["mode"] == "moto"


def test_invalid_orders_are_explained_and_change_nothing(ready):
    s = ready.store
    s.recruit("infantry")
    s.recruit("infantry")
    s.picked, s.dest, s.mode = ["S1", "S2"], "V_C1", "walk"
    before = (s.sim["budget"], len(s.sim["transfers"]))
    s.send()
    assert "A pie va 1 soldado" in s.notice[0] and s.notice[1] == "error"
    assert (s.sim["budget"], len(s.sim["transfers"])) == before


def test_only_free_soldiers_can_be_picked(ready):
    s = ready.store
    s.recruit("infantry")
    s.toggle_pick("S1")
    s.dest, s.mode = "V_C1", "moto"
    s.send()
    s.toggle_pick("S1")                                   # on its way: cannot be picked
    assert s.picked == []
    s.toggle_pick("S999")                                 # unknown soldier is ignored
    assert s.picked == []


def test_helicopter_goes_through_the_same_store(ready):
    s = ready.store
    for _ in range(4):
        s.recruit("infantry")
    s.picked, s.dest, s.mode = ["S1", "S2", "S3", "S4"], "V_C1", "air"
    s.send()
    assert s.sim["budget"]["reserved"] == 200 and len(s.sim["flights"]) == 1
