"""Section 12 + REST contract: scenario upload from the UI and the simulation endpoints."""
import io
import json

import pytest

from conftest import DOCS, load
from src.app import create_app
from src.features.scenario.application.session import session


@pytest.fixture
def api():
    session.load(load())                                   # clean state for every test
    return create_app().test_client()


def upload(client, content, name="esc.json"):
    return client.post("/api/scenario/upload", data={"file": (io.BytesIO(content), name)},
                       content_type="multipart/form-data")


def test_health_and_current_scenario(api):
    assert api.get("/api/health").get_json()["status"] == "healthy"
    data = api.get("/api/scenario/current").get_json()
    assert data["success"] and data["validation"]["has_base"]
    assert len(data["data"]["graph_e"]["vertices"]) == 5


def test_the_user_chooses_the_json_and_it_replaces_the_scenario(api):
    raw = (DOCS / "escenario_complejo.json").read_bytes()
    res = upload(api, raw)
    assert res.status_code == 200 and "complejo" in res.get_json()["message"]
    assert "complejo" in api.get("/api/scenario/current").get_json()["data"]["metadata"]["title"]


def test_json_body_is_also_accepted(api):
    raw = json.loads((DOCS / "escenario_complejo.json").read_text(encoding="utf-8"))
    assert api.post("/api/scenario/upload", json=raw).status_code == 200


@pytest.mark.parametrize("content,text", [
    (b"esto no es json", "JSON válido"),
    (b"[1, 2, 3]", "objeto"),
    (b"{}", "Falta la sección"),
])
def test_invalid_uploads_get_a_clear_400_and_keep_the_old_scenario(api, content, text):
    res = upload(api, content)
    assert res.status_code == 400 and text in res.get_json()["error"]
    assert "General P. Tardo" in api.get("/api/scenario/current").get_json()["data"]["metadata"]["title"]


def test_upload_without_file_is_rejected(api):
    assert api.post("/api/scenario/upload").status_code == 400


def test_cannot_simulate_before_planning(api):
    assert api.post("/api/simulation/reset").status_code == 409
    assert api.get("/api/simulation/state").status_code == 409


def test_full_flow_through_the_api(api):
    plan = api.post("/api/defense/plan").get_json()["plan"]
    assert [t["vertex_id"] for t in plan["towers"]] == ["V_C1", "V_C2"]
    assert api.get("/api/defense/plan").get_json()["plan"]["coverage_pct"] == 100.0
    assert api.post("/api/simulation/reset").status_code == 200
    r = api.post("/api/units/recruit", json={"type": "sniper", "count": 2}).get_json()
    assert r["state"]["budget"]["available"] == 1400
    r = api.post("/api/transport/move", json={"soldier_ids": ["S1", "S2"], "dest": "V_C1", "mode": "moto"})
    assert r.status_code == 200
    path = api.get("/api/transport/path?src=V_BASE&dst=V_C1&mode=walk").get_json()["path"]
    assert path["time"] == 20.0 and path["vertices"] == ["V_BASE", "V_T1", "V_C1"]
    state = api.post("/api/simulation/tick", json={"dt": 10}).get_json()["state"]
    assert state["clock"] == 10.0 and state["status"] == "RUNNING"
    assert {t["vertex_id"]: t["occupants"] for t in state["towers"]}["V_C1"] == 2


def test_plan_is_locked_once_the_fight_started(api):
    api.post("/api/defense/plan")
    api.post("/api/simulation/reset")
    api.post("/api/simulation/tick", json={"dt": 1})
    res = api.post("/api/defense/plan")
    assert res.status_code == 409 and "reubicar" in res.get_json()["error"]


def test_restart_gives_a_clean_match_with_repaired_bridges(api):
    api.post("/api/defense/plan")
    api.post("/api/simulation/reset")
    session.simulation.world.manager.graph_e.edges["E_E1"].is_destroyed = True
    state = api.post("/api/simulation/reset").get_json()["state"]
    assert state["clock"] == 0 and not any(b["destroyed"] for b in state["bridges"])


@pytest.mark.parametrize("path,body", [
    ("/api/units/recruit", {"type": "tank", "count": 1}),
    ("/api/units/recruit", {"type": "sniper", "count": "muchos"}),
    ("/api/units/recruit", {"type": "sniper", "count": 0}),
    ("/api/units/recruit", {"type": "gunner", "count": 20}),                # not enough money
    ("/api/simulation/tick", {"dt": -1}),
    ("/api/simulation/tick", {"dt": "x"}),
    ("/api/transport/move", {"soldier_ids": ["S1"], "dest": "V_C1", "mode": "walk"}),  # no soldiers
    ("/api/transport/helicopter", {"soldier_ids": [], "dest": "V_C1"}),
])
def test_bad_requests_return_json_400_never_500(api, path, body):
    api.post("/api/defense/plan")
    api.post("/api/simulation/reset")
    res = api.post(path, json=body)
    assert res.status_code == 400 and res.get_json()["success"] is False


def test_current_scenario_includes_the_initial_cheapest_route(api):
    route = api.get("/api/scenario/current").get_json()["data"]["initial_route"]
    assert route["vertices"] == ["M_ENTRADA", "M_N1", "M_N2", "M_SALIDA"] and route["cost"] == 23.0
