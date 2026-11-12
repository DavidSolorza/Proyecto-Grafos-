"""End to end: the Pygame client against the real Flask API (over HTTP) and complete matches played with the mouse."""
import json
import socket

import pygame
import pytest

from conftest import DOCS, Driver
from src.features.scenario.application.session import session
from tardo_ui.api import ApiClient, ApiError, HttpTransport
from tardo_ui.launcher import backend_alive, ensure_backend
from tardo_ui.store import Store


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_launcher_starts_flask_and_the_client_plays_a_match_over_real_http():
    session.__init__()
    url = f"http://127.0.0.1:{free_port()}"
    assert backend_alive(url) is False
    server = ensure_backend(url)
    try:
        assert server is not None and backend_alive(url)
        assert ensure_backend(url) is None                         # already running (e.g. next to React): reuse it
        store = Store(ApiClient(HttpTransport(url)))
        store.refresh()
        assert store.backend_ok and store.scenario is None         # starts empty
        assert store.load_file(DOCS / "escenario_general_p_tardo.json")
        store.calculate_plan()
        store.recruit("sniper")
        store.recruit("sniper")
        store.picked, store.dest, store.mode = ["S1", "S2"], "V_C1", "moto"
        store.send()
        store.advance(30)
        assert store.sim["status"] == "VICTORY_ELIMINATION" and store.sim["clock"] == 14.25
        assert store.sim["budget"]["available"] == 1750
    finally:
        server.shutdown()
    assert backend_alive(url) is False


def test_launcher_refuses_to_invent_a_remote_backend():
    with pytest.raises(ApiError, match="solo se puede iniciar uno local"):
        ensure_backend("http://example.invalid:5000")


def test_two_clients_share_one_session_over_http():
    """Pygame and React talk to the same API: what one does, the other sees."""
    session.__init__()
    url = f"http://127.0.0.1:{free_port()}"
    server = ensure_backend(url)
    try:
        pygame_side, web_side = Store(ApiClient(HttpTransport(url))), ApiClient(HttpTransport(url))
        web_side.upload_scenario(json.loads((DOCS / "escenario_general_p_tardo.json").read_text(encoding="utf-8")))
        web_side.create_plan()
        web_side.reset()
        web_side.recruit("infantry", 2)
        pygame_side.refresh()
        assert pygame_side.plan["coverage_pct"] == 100.0 and len(pygame_side.sim["soldiers"]) == 2
        pygame_side.recruit("gunner")
        assert len(web_side.state()["state"]["soldiers"]) == 3
    finally:
        server.shutdown()


def play_victory(d: Driver) -> None:
    d.click("Francotirador")
    d.click("Francotirador")
    d.click("soldado:S1")
    d.click("soldado:S2")
    d.click("dest:V_C1")
    d.click("medio:moto")
    d.click("Enviar")
    d.play_to_end()


def test_victory_by_elimination_played_only_with_the_mouse(ready):
    play_victory(ready)
    sim = ready.store.sim
    assert sim["status"] == "VICTORY_ELIMINATION" and sim["clock"] == 14.25 and sim["budget"]["available"] == 1750
    assert "Jugar de nuevo" in ready.hits
    shots = [e["text"] for e in sim["events"] if e["kind"] == "combat"]
    assert shots and all("SNIPER" in text for text in shots)           # the log explains every hit


def test_defeat_when_nothing_is_bought(ready):
    ready.play_to_end()
    assert ready.store.sim["status"] == "DEFEAT" and ready.store.sim["clock"] == 23.0


def test_victory_by_resistance_with_a_time_limit(tmp_path):
    raw = json.loads((DOCS / "escenario_puentes.json").read_text(encoding="utf-8"))
    raw["metadata"]["time_limit"] = 30
    path = tmp_path / "limite30.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    d = Driver()
    assert d.store.load_file(path)
    d.store.calculate_plan()
    d.go("simulacion")
    d.click("5x")
    d.play_to_end()
    assert d.store.sim["status"] == "VICTORY_RESISTANCE" and d.store.sim["clock"] == 30.0


def test_helicopter_with_surplus_distribution_from_the_interface(ready):
    for _ in range(4):
        ready.click("Infantería")
    for sid in ("S1", "S2", "S3", "S4"):
        ready.click(f"soldado:{sid}")
    ready.click("dest:V_C1")
    ready.click("medio:air")
    assert "Ver ruta" in ready.hits
    ready.click("Enviar")
    assert ready.store.sim["budget"]["reserved"] == 200 and ready.store.sim["budget"]["available"] == 1400
    for _ in range(4):
        ready.click("+1 s")
    towers = {t["vertex_id"]: t["occupants"] for t in ready.store.sim["towers"]}
    assert towers == {"V_C1": 3, "V_C2": 1}
    assert ready.store.sim["budget"]["reserved"] == 0 and ready.store.sim["budget"]["spent"] == 600


def test_complex_scenario_plan_is_shown_with_its_explanation():
    d = Driver()
    d.load("escenario_complejo.json")
    d.go("plan")
    d.click("Calcular plan")
    plan = d.store.plan
    assert d.store.tower_ids == ["V_C4", "V_C3"] and plan["coverage_pct"] == 72.2
    assert plan["unreachable"] == ["V_ISLA"] and plan["mst"]["total_time"] == 85.0 and len(plan["mst"]["edges"]) == 7
    assert [round(t["score"], 2) for t in plan["towers"]] == [73.85, 16.34]
    assert len(plan["steps"]) == 2 and [s["chosen"] for s in plan["steps"]] == ["V_C4", "V_C3"]


def test_scenario_replacement_discards_the_old_match():
    d = Driver()
    d.load()
    d.store.calculate_plan()
    d.store.recruit("infantry")
    d.load("escenario_complejo.json")
    assert d.store.plan is None and d.store.sim is None and d.store.picked == []
    d.go("simulacion")
    assert "ir al plan" in d.hits
