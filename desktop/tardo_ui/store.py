"""State and actions of the desktop client. No pygame in here, so it is easy to test."""
import json
from pathlib import Path

from tardo_ui.api import ApiClient, ApiError
from tardo_ui.commands import FINISHED, FREE, MatchCommands  # noqa: F401  (FINISHED, FREE are used by the screens)

TABS = (("inicio", "Inicio"), ("grafos", "Los grafos"), ("plan", "Plan de defensa"), ("simulacion", "Simulación"))
TICK_MS, SYNC_MS, NOTICE_MS = 250, 1500, 6000


class Store(MatchCommands):
    """Everything the screens show, plus the operations the user can trigger."""

    def __init__(self, api: ApiClient) -> None:
        self.api = api
        self.tab = "inicio"
        self.scenario = self.validation = self.plan = self.sim = None
        self.backend_ok = False
        self.notice = None                       # (text, "ok" | "error", expires_ms)
        self.selected = None                     # {"network": "GE" | "GM", "id": ...}
        self.layers, self.show_tree, self.show_radii, self.show_initial_route = "both", True, True, True
        self.speed, self.running, self.hide_end = 1, False, False
        self.picked, self.dest, self.mode, self.route_text = [], "", "walk", ""
        self.log_scroll, self.bottom_tab = 0, "bitacora"      # purely visual state of the simulation screen
        self.now = self._last_tick = self._last_sync = 0
        self._sig = None

    # ---- helpers -----------------------------------------------------------------------
    def say(self, text: str, kind: str = "ok") -> None:
        self.notice = (text, kind, self.now + NOTICE_MS)

    def _try(self, call, *args, quiet: bool = False):
        try:
            return call(*args)
        except ApiError as err:
            if not quiet:
                self.say(str(err), "error")
            return None

    def _remember(self) -> None:
        """Remember the session fingerprint after our own change, so we do not refresh for nothing."""
        res = self._try(self.api.status, quiet=True)
        self._sig = self._fingerprint(res) if res else None

    @staticmethod
    def _fingerprint(status: dict) -> str:
        return repr(status.get("revision")) + repr(status.get("match"))

    @property
    def finished(self) -> bool:
        return bool(self.sim) and self.sim["status"] in FINISHED

    @property
    def tower_ids(self) -> list:
        return [t["vertex_id"] for t in (self.plan or {}).get("towers", [])]

    # ---- loading -----------------------------------------------------------------------
    def refresh(self) -> None:
        """Re-read scenario, plan and match from the backend (the source of truth)."""
        res = self._try(self.api.current_scenario)
        self.backend_ok = res is not None
        if res is None:
            return
        self.scenario, self.validation = res.get("data"), res.get("validation")
        plan = self._try(self.api.plan, quiet=True)
        self.plan = plan["plan"] if plan else None
        state = self._try(self.api.state, quiet=True)
        self.sim = state["state"] if state else None
        self.picked = [s for s in self.picked if self.sim and any(x["id"] == s for x in self.sim["soldiers"])]
        if not self.sim or self.finished:
            self.running = False
        self._remember()

    def load_file(self, path) -> bool:
        """Read a JSON chosen by the user and let the backend validate it (requirement 12)."""
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except OSError:
            self.say("No se pudo leer el archivo", "error")
            return False
        except ValueError:
            self.say("El archivo no es un JSON válido", "error")
            return False
        res = self._try(self.api.upload_scenario, raw)
        if res is None:
            return False
        self.running, self.selected, self.picked, self.route_text = False, None, [], ""
        self.say(res.get("message", "Escenario cargado"))
        self.refresh()
        return True

    # ---- planning ----------------------------------------------------------------------
    def calculate_plan(self) -> None:
        res = self._try(self.api.create_plan)
        if res is None:
            return
        self.plan = res["plan"]
        self.say(f"Plan calculado: {len(self.plan['towers'])} torre(s), cobertura {self.plan['coverage_pct']}%")
        self.reset_match()

    def reset_match(self) -> None:
        self.running = False
        res = self._try(self.api.reset)
        if res:
            self.sim, self.hide_end, self.picked, self.route_text = res["state"], False, [], ""
            self._remember()

    # ---- clock of the application (not the logical clock of the match) ----------------------
    def tick_real(self, now: int) -> None:
        """Called every frame: run the match at the chosen speed, or follow changes made by other clients."""
        self.now = now
        if self.running and now - self._last_tick >= TICK_MS:
            self._last_tick = now
            self.advance(0.25 * self.speed)
        elif not self.running and now - self._last_sync >= SYNC_MS:
            self._last_sync = now
            self.sync()

    def sync(self) -> None:
        res = self._try(self.api.status, quiet=True)
        self.backend_ok = res is not None
        if res is not None and self._fingerprint(res) != self._sig:
            self.refresh()
