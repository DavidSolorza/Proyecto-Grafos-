"""Registry of audit checks and a tiny HTTP client (standard library only)."""
import json
import urllib.error
import urllib.request
from pathlib import Path

DOCS = Path(__file__).resolve().parents[2] / "docs"
CHECKS: list = []       # (section, statement point, function)


def check(section: str, point: str):
    """Register a check. It passes when the function returns normally; AssertionError means failure."""
    def register(fn):
        CHECKS.append((section, point, fn))
        return fn
    return register


class Api:
    """JSON over HTTP against the Flask server under audit."""

    def __init__(self, url: str) -> None:
        self.url = url.rstrip("/")

    def call(self, method: str, path: str, body=None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(self.url + "/api" + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as res:
                return res.status, json.loads(res.read() or b"{}")
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read() or b"{}")

    def get(self, path):
        return self.call("GET", path)

    def post(self, path, body=None):
        return self.call("POST", path, {} if body is None else body)


def scenario(name: str = "escenario_general_p_tardo.json", edit=None) -> dict:
    raw = json.loads((DOCS / name).read_text(encoding="utf-8"))
    if edit:
        edit(raw)
    return raw


class Match:
    """A fresh scenario + plan + match on the server, with short helpers for the checks."""

    def __init__(self, api: Api, name="escenario_general_p_tardo.json", edit=None, plan=True) -> None:
        self.api = api
        status, body = api.post("/scenario/upload", scenario(name, edit))
        assert status == 200, f"upload rejected: {body}"
        if plan:
            assert api.post("/defense/plan")[0] == 200
            assert api.post("/simulation/reset")[0] == 200

    def ok(self, path, body=None, expect=200):
        status, res = self.api.post(path, body)
        assert status == expect, f"{path} answered {status}: {res.get('error')}"
        return res

    def state(self) -> dict:
        return self.api.get("/simulation/state")[1]["state"]

    def buy(self, kind, n=1):
        return self.ok("/units/recruit", {"type": kind, "count": n})["state"]

    def move(self, ids, dest, mode):
        return self.ok("/transport/move", {"soldier_ids": ids, "dest": dest, "mode": mode})["state"]

    def tick(self, seconds):
        """Advance the logical clock. The API accepts at most 30 s per request, so long spans are split."""
        state = None
        while seconds > 0:
            step = min(seconds, 25)
            state = self.ok("/simulation/tick", {"dt": step})["state"]
            seconds -= step
        return state

    def rejected(self, path, body, text):
        """The server must refuse with a clear message and leave the match untouched."""
        before = self.state()
        status, res = self.api.post(path, body)
        assert status in (400, 409) and text in res.get("error", ""), f"{status}: {res}"
        after = self.state()
        for key in ("budget", "soldiers", "towers", "transfers", "flights", "clock"):
            assert before[key] == after[key], f"a rejected order changed '{key}'"


def hits(state, soldier=None):
    return [e for e in state["events"] if e["kind"] == "combat" and (soldier is None or e["text"].startswith(soldier))]
