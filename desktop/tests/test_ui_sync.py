"""The application clock, and following changes made by another client on the shared session."""
import json

import pytest

from conftest import DOCS, FlaskTransport
from tardo_ui.api import ApiClient, ApiError, HttpTransport
from tardo_ui.store import SYNC_MS, TICK_MS, Store

def test_running_follows_the_speed_and_stops_when_the_match_ends(ready):
    s = ready.store
    s.speed = 5
    s.toggle_play()
    start = s.sim["clock"]
    s.tick_real(s.now + TICK_MS)
    assert s.sim["clock"] == pytest.approx(start + 1.25)
    for i in range(100):
        s.tick_real(s.now + TICK_MS)
    assert s.finished and s.running is False and s.sim["status"] == "DEFEAT"


def test_play_is_ignored_without_a_match_or_after_the_end(ui):
    ui.store.toggle_play()
    assert ui.store.running is False


def test_changes_made_by_another_client_are_picked_up(ready):
    s = ready.store
    other = ApiClient(FlaskTransport(ready.client))          # e.g. the React app buying a soldier
    other.recruit("gunner", 1)
    assert s.sim["soldiers"] == []
    s.tick_real(s.now + SYNC_MS + 1)
    assert [x["type"] for x in s.sim["soldiers"]] == ["GUNNER"] and s.sim["budget"]["available"] == 1500
    other.upload_scenario(json.loads((DOCS / "escenario_complejo.json").read_text(encoding="utf-8")))
    s.tick_real(s.now + SYNC_MS + 1)
    assert "complejo" in s.scenario["metadata"]["title"] and s.plan is None and s.sim is None


def test_no_refresh_loop_after_our_own_changes(ready):
    s = ready.store
    s.recruit("infantry")
    calls = []
    original = s.refresh
    s.refresh = lambda: (calls.append(1), original())
    s.tick_real(s.now + SYNC_MS + 1)
    assert calls == []


def test_the_real_http_transport_reports_a_dead_backend():
    with pytest.raises(ApiError, match="No se pudo conectar"):
        ApiClient(HttpTransport("http://127.0.0.1:9", timeout=0.5)).health()
    store = Store(ApiClient(HttpTransport("http://127.0.0.1:9", timeout=0.5)))
    store.refresh()
    assert store.backend_ok is False and store.notice[1] == "error"
