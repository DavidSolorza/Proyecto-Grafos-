"""Main window: header, tabs, the active screen, the file chooser and notifications."""
from pathlib import Path

import pygame

from tardo_ui import theme as t
from tardo_ui.filepicker import FilePicker
from tardo_ui.header import HEADER_H, draw_header
from tardo_ui.screens import graphs, home, plan, sim
from tardo_ui.store import Store
from tardo_ui.ui import Ui

SCREENS = {"inicio": home, "grafos": graphs, "plan": plan, "simulacion": sim}
MIN_SIZE = (840, 560)
POINTER_EVENTS = (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)


class App:
    """Owns the frame loop. `frame()` draws one frame and can be driven by tests without a real window.

    The interface is drawn on a *logical* canvas whose size is the window size divided by a fluid scale
    (see theme.ui_scale: a clamp between a minimum and a maximum). The canvas is then stretched to the window,
    so the layout fills any window and everything grows and shrinks smoothly, like CSS clamp().
    """

    def __init__(self, store: Store, surface: pygame.Surface = None, size=(1360, 820)) -> None:
        self.store = store
        self.window = surface or pygame.display.set_mode(size, pygame.RESIZABLE)
        self.canvas, self.scale = self.window, 1.0
        self.ui = Ui(self.window)
        self.picker = None
        self.last_dir = None
        self.running = True

    @property
    def surface(self) -> pygame.Surface:
        """What the screens draw on (the logical canvas)."""
        return self.canvas

    def open_picker(self) -> None:
        self.picker = FilePicker(self.last_dir)
        self.ui.click = None                                    # this click opened the dialog: it must not also pick a row

    def _fit_canvas(self) -> None:
        w, h = self.window.get_size()
        self.scale = t.ui_scale(w, h)
        size = (round(w / self.scale), round(h / self.scale))
        if self.scale == 1.0:
            self.canvas = self.window
        elif self.canvas is self.window or self.canvas.get_size() != size:
            self.canvas = pygame.Surface(size)

    def _to_logical(self, event):
        """Mouse positions arrive in window pixels; the screens work in canvas pixels."""
        if event.type in POINTER_EVENTS and self.scale != 1.0:
            return pygame.event.Event(event.type, {**event.dict, "pos": tuple(v / self.scale for v in event.pos)})
        return event

    # ---- one frame ---------------------------------------------------------------------
    def frame(self, events=(), now: int = None) -> None:
        self._fit_canvas()
        surface, ui, store = self.canvas, self.ui, self.store
        events = [self._to_logical(e) for e in events]
        ui.scale, ui.time_ms = self.scale, pygame.time.get_ticks() if now is None else now
        ui.begin(surface, events)
        store.tick_real(ui.time_ms)
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.picker = None
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and store.tab == "simulacion" and not self.picker:
                store.toggle_play()
        surface.fill(t.PAPER)
        w, h = surface.get_size()
        ui.lock = self.picker is not None                       # the dialog blocks the screen behind it
        draw_header(ui, store, w)
        area = pygame.Rect(20, HEADER_H + 14, w - 40, h - HEADER_H - 28)
        if store.tab != "inicio" and not store.scenario:
            self.no_scenario(area)
        else:
            SCREENS[store.tab].draw(ui, area, store, self)
        if self.picker:
            ui.lock = False
            result = self.picker.draw(ui, pygame.Rect(0, 0, w, h))
            if result and result[0] == "choose":
                self.last_dir = Path(result[1]).parent
                self.picker = None
                store.load_file(result[1])
            elif result:
                self.picker = None
        self.toast(w, h)
        if surface is not self.window:                          # stretch the logical canvas to the real window
            pygame.transform.smoothscale(surface, self.window.get_size(), self.window)

    def no_scenario(self, area: pygame.Rect) -> None:
        ui = self.ui
        inner = ui.card(pygame.Rect(area.x, area.y, 560, 170), "Aún no hay un escenario cargado")
        ui.wrap("La aplicación arranca vacía: tú eliges el archivo JSON que describe los grafos, el convoy y el presupuesto.",
                inner, "body", t.SOFT)
        if ui.button((inner.x, inner.y + 62, 280, 36), "Ir a cargar un escenario", key="ir a inicio", tone="on"):
            self.store.tab = "inicio"

    def toast(self, w: int, h: int) -> None:
        notice = self.store.notice
        if not notice or self.store.now > notice[2]:
            return
        text, kind, _ = notice
        font = self.ui.fonts.get("body")
        box = pygame.Rect(0, 0, min(w - 40, font.size(text)[0] + 40), 40)
        box.midbottom = (w // 2, h - 14)
        self.ui.shadow(box, 10, strength=60)
        pygame.draw.rect(self.ui.surface, t.SAGE if kind == "ok" else t.TERRA, box, border_radius=10)
        self.ui.text(text, box.center, "body", t.PAPER, "center", box.w - 20)

    # ---- real loop -----------------------------------------------------------------------
    def run(self) -> None:
        clock = pygame.time.Clock()
        self.store.refresh()
        while self.running:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.VIDEORESIZE and (e.w < MIN_SIZE[0] or e.h < MIN_SIZE[1]):
                    pygame.display.set_mode((max(e.w, MIN_SIZE[0]), max(e.h, MIN_SIZE[1])), pygame.RESIZABLE)
            self.window = pygame.display.get_surface()
            self.frame(events)
            pygame.display.flip()
            clock.tick(60)
