"""Section 12: the app starts empty, and clients can follow the session through the status fingerprint."""
import pytest

from conftest import DOCS
from src.app import create_app
from src.features.scenario.application.session import session


def upload(client, content, name="esc.json"):
    import io
    return client.post("/api/scenario/upload", data={"file": (io.BytesIO(content), name)},
                       content_type="multipart/form-data")

@pytest.fixture
def empty_api():
    session.__init__()                                     # what a freshly started server has
    return create_app().test_client()


def test_the_app_starts_empty_until_the_user_uploads_a_json(empty_api):
    cur = empty_api.get("/api/scenario/current").get_json()
    assert cur["success"] and cur["loaded"] is False and cur["data"] is None
    assert empty_api.get("/api/defense/plan").get_json()["plan"] is None
    for res in (empty_api.post("/api/defense/plan"), empty_api.post("/api/simulation/reset"),
                empty_api.get("/api/simulation/state")):
        assert res.status_code == 409
    assert "carga un escenario" in empty_api.post("/api/defense/plan").get_json()["error"]


def test_after_uploading_the_first_scenario_everything_works(empty_api):
    raw = (DOCS / "escenario_general_p_tardo.json").read_bytes()
    assert upload(empty_api, raw).status_code == 200
    assert empty_api.get("/api/scenario/current").get_json()["loaded"] is True
    assert empty_api.post("/api/defense/plan").status_code == 200
    assert empty_api.post("/api/simulation/reset").status_code == 200


def test_an_invalid_first_upload_leaves_the_app_empty(empty_api):
    assert upload(empty_api, b"{}").status_code == 400
    assert empty_api.get("/api/scenario/current").get_json()["loaded"] is False


def test_status_fingerprint_changes_when_the_session_changes(empty_api):
    first = empty_api.get("/api/scenario/status").get_json()
    assert first["loaded"] is False and first["match"] is None and first["revision"]["scenario"] >= 0
    upload(empty_api, (DOCS / "escenario_general_p_tardo.json").read_bytes())
    loaded = empty_api.get("/api/scenario/status").get_json()
    assert loaded["loaded"] and not loaded["has_plan"] and loaded["revision"]["scenario"] > first["revision"]["scenario"]
    empty_api.post("/api/defense/plan")
    empty_api.post("/api/simulation/reset")
    before = empty_api.get("/api/scenario/status").get_json()
    empty_api.post("/api/units/recruit", json={"type": "infantry", "count": 1})
    after = empty_api.get("/api/scenario/status").get_json()
    assert before["match"]["soldiers"] == 0 and after["match"]["soldiers"] == 1
    assert after["match"]["events"] > before["match"]["events"] and after["match"]["available"] == 1900
    empty_api.post("/api/simulation/tick", json={"dt": 1})
    assert empty_api.get("/api/scenario/status").get_json()["match"]["clock"] == 1.0
