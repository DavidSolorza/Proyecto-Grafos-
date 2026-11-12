"""Fluid interface (the Pygame equivalent of CSS clamp): the scale follows the window between a minimum and a maximum."""
import pygame
import pytest

from conftest import Driver
from tardo_ui import theme as t
from tardo_ui.app import MIN_SIZE


def test_clamp_keeps_the_value_between_its_limits():
    assert t.clamp(1, 0, 3) == 1 and t.clamp(1, 2, 3) == 2 and t.clamp(1, 9, 3) == 3


@pytest.mark.parametrize("size,expected", [
    ((1360, 820), 1.0),                      # the design size is drawn 1:1
    ((1380, 830), 1.0),                      # very close to it: still 1:1 so text stays crisp
    ((680, 410), t.MIN_SCALE),               # a tiny window never shrinks the interface below the minimum
    ((840, 560), 0.7),
    ((4000, 3000), t.MAX_SCALE),             # a huge screen never grows it beyond the maximum
])
def test_ui_scale_is_clamped(size, expected):
    assert t.ui_scale(*size) == pytest.approx(expected)


def test_ui_scale_grows_smoothly_with_the_window():
    scales = [t.ui_scale(w, round(w * 820 / 1360)) for w in range(900, 2400, 100)]
    assert scales == sorted(scales) and scales[0] >= t.MIN_SCALE and scales[-1] <= t.MAX_SCALE
    assert all(b - a < 0.1 for a, b in zip(scales, scales[1:]))            # no sudden jumps


@pytest.mark.parametrize("size", [MIN_SIZE, (1000, 640), (1360, 820), (1920, 1080), (2560, 1440)])
def test_every_screen_fits_and_fills_any_window_size(size):
    d = Driver(size)
    d.load("escenario_complejo.json")
    d.store.calculate_plan()
    d.store.recruit("sniper")
    w, h = size
    for tab in ("inicio", "grafos", "plan", "simulacion"):
        d.go(tab)
        cw, ch = d.surface.get_size()
        assert abs(cw * d.app.scale - w) <= 1 and abs(ch * d.app.scale - h) <= 1      # the canvas covers the whole window
        vp = d.app.ui.viewport
        if vp:                                                                          # the map never leaves the canvas
            assert vp.rect.right <= cw and vp.rect.bottom <= ch
    top_left = tuple(d.window.get_at((3, 3)))[:3]
    assert top_left != t.PAPER and sum(top_left) < 150                                   # the header was drawn and stretched


def test_clicks_in_window_pixels_reach_the_right_button_when_scaled():
    d = Driver((1920, 1080))
    assert d.app.scale == pytest.approx(1920 / 1360, rel=0.01) or d.app.scale > 1.2
    d.load()
    rect = d.hits["tab:plan"]
    window_pos = tuple(round(v * d.app.scale) for v in rect.center)
    d.frame(pygame.event.Event(pygame.MOUSEMOTION, pos=window_pos, rel=(0, 0), buttons=(0, 0, 0)),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=window_pos, button=1))
    assert d.store.tab == "plan"
    d.frame()
    wrong = (round(rect.centerx), round(rect.centery))                                   # logical position used as if it were window pixels
    d.go("inicio")
    d.frame(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=wrong, button=1))
    assert d.store.tab != "plan"


def test_resizing_the_window_rebuilds_the_canvas_only_when_needed():
    d = Driver((1360, 820))
    d.load()
    assert d.app.canvas is d.window and d.app.scale == 1.0
    d.app.window = pygame.Surface((1900, 1000))
    d.frame()
    first = d.app.canvas
    assert first is not d.app.window and d.app.scale > 1.2
    d.frame()
    assert d.app.canvas is first                                                          # the same canvas is reused between frames
    d.app.window = pygame.Surface((1000, 640))
    d.frame()
    assert d.app.scale < 1.0 and d.app.canvas.get_size() == (round(1000 / d.app.scale), round(640 / d.app.scale))
    d.app.window = pygame.Surface((1360, 820))
    d.frame()
    assert d.app.canvas is d.app.window                                                   # back to the design size: drawn 1:1 again


def test_visual_polish_header_gradient_card_shadow_and_map_grid(ui):
    ui.load()
    ui.go("grafos")
    top, bottom = tuple(ui.surface.get_at((600, 2)))[:3], tuple(ui.surface.get_at((600, 92)))[:3]
    assert top != bottom and sum(top) > sum(bottom)                                       # header gradient: lighter on top
    card = ui.hits["Ambas capas"]                                                         # a button inside the side card
    assert card.right < ui.surface.get_width()
    stage = ui.app.ui.viewport.rect
    below_map = tuple(ui.surface.get_at((stage.centerx, stage.bottom + 14)))[:3]
    assert below_map != t.PAPER and sum(below_map) < sum(t.PAPER)                          # the soft shadow under the map


def test_convoy_pulse_animates_with_the_application_clock(ready):
    ready.store.sim["convoy"]["xy"] = list(ready.store.scenario["graph_m"]["vertices"][0]["coords"])
    vp = ready.app.ui.viewport
    x, y = vp.to_screen(ready.store.sim["convoy"]["xy"])
    ring = pygame.Rect(x - 30, y - 30, 60, 60)
    ready.t = 0
    ready.frame(advance=400)
    early = pygame.image.tobytes(ready.surface.subsurface(ring), "RGB")
    ready.frame(advance=800)
    late = pygame.image.tobytes(ready.surface.subsurface(ring), "RGB")
    assert early != late                                                                   # the expanding ring moved
