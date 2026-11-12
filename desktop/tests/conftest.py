"""Helpers for the Pygame client tests: a headless window driven with simulated mouse events."""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")      # no real window is needed
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "desktop"), str(ROOT / "backend")]
DOCS = ROOT / "docs"

import pygame  # noqa: E402
import pytest  # noqa: E402

from src.app import create_app  # noqa: E402
from src.features.scenario.application.session import session  # noqa: E402
from tardo_ui.api import ApiClient  # noqa: E402
from tardo_ui.app import App  # noqa: E402
from tardo_ui.store import Store  # noqa: E402

pygame.init()


class FlaskTransport:
    """Same contract as the HTTP transport, but calls the Flask app in-process (fast, no ports)."""

    def __init__(self, client) -> None:
        self.client = client

    def request(self, method, path, body=None):
        res = self.client.open(path, method=method, json=body)
        return res.status_code, res.get_json() or {}


class Driver:
    """A fresh backend session + a Store + an App drawing on an off-screen surface."""

    def __init__(self, size=(1360, 820)) -> None:
        session.__init__()
        self.client = create_app().test_client()
        self.api = ApiClient(FlaskTransport(self.client))
        self.store = Store(self.api)
        self.window = pygame.Surface(size)                  # what the user sees
        self.app = App(self.store, self.window)
        self.t = 0
        self.store.refresh()
        self.frame()

    @property
    def surface(self) -> pygame.Surface:
        """The logical canvas the screens draw on (equal to the window when the scale is 1.0)."""
        return self.app.canvas

    @property
    def hits(self) -> dict:
        return self.app.ui.hits

    def frame(self, *events, advance: int = 16) -> None:
        self.t += advance
        self.app.frame(events, now=self.t)

    def click_at(self, pos) -> None:
        """Click at a position of the logical canvas (converted to window pixels, as a real mouse would give)."""
        pos = tuple(round(v * self.app.scale) for v in pos)
        self.frame(pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)),
                   pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))
        self.frame()                                    # redraw so the button registry is current

    def click(self, key: str) -> None:
        assert key in self.hits, f"no hay un botón «{key}» en pantalla; hay: {sorted(self.hits)}"
        self.click_at(self.hits[key].center)

    def key(self, code) -> None:
        self.frame(pygame.event.Event(pygame.KEYDOWN, key=code, mod=0, unicode=""))

    def wheel(self, pos, dy: int) -> None:
        pos = tuple(round(v * self.app.scale) for v in pos)
        self.frame(pygame.event.Event(pygame.MOUSEMOTION, pos=pos, rel=(0, 0), buttons=(0, 0, 0)),
                   pygame.event.Event(pygame.MOUSEWHEEL, y=dy, x=0))

    def load(self, name: str = "escenario_general_p_tardo.json") -> None:
        assert self.store.load_file(DOCS / name)
        self.frame()

    def go(self, tab: str) -> None:
        self.click(f"tab:{tab}")

    def play_to_end(self, limit: int = 3000) -> None:
        """Press Iniciar and let the real-time loop run (each 250 ms of window time = one tick)."""
        self.click("Iniciar")
        for _ in range(limit):
            if self.store.finished:
                break
            self.frame(advance=250)
        assert self.store.finished, "la partida no terminó"

    def texts(self) -> list:
        """Every string drawn in one frame (to check what the screen tells the user)."""
        out, ui = [], self.app.ui
        draw_text, draw_wrap, draw_badge = ui.text, ui.wrap, ui.badge
        ui.text = lambda txt, *a, **k: (out.append(str(txt)), draw_text(txt, *a, **k))[1]
        ui.wrap = lambda txt, *a, **k: (out.append(str(txt)), draw_wrap(txt, *a, **k))[1]
        ui.badge = lambda pos, label, *a, **k: (out.append(str(label)), draw_badge(pos, label, *a, **k))[1]
        try:
            self.frame()
        finally:
            del ui.text, ui.wrap, ui.badge
        return out

    def shot(self, path) -> None:
        pygame.image.save(self.window, str(path))

    def count_color(self, color, rect=None) -> int:
        """How many pixels of the frame have exactly this color (to prove that something was drawn)."""
        area = self.surface if rect is None else self.surface.subsurface(rect)
        return pygame.transform.threshold(None, area, color, (1, 1, 1, 255), None, 0, None, True)


@pytest.fixture
def ui():
    return Driver()


@pytest.fixture
def ready():
    """Simple scenario loaded and planned, on the simulation screen."""
    d = Driver()
    d.load()
    d.store.calculate_plan()
    d.go("simulacion")
    return d
