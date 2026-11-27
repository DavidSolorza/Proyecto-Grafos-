"""Layout quality: nothing overlaps or is cut off, whatever the window size."""
import pygame
import pytest

from conftest import DOCS, Driver
from tardo_ui import theme as t

SCENARIOS = sorted(p.name for p in DOCS.glob("escenario*.json"))
SIZES = [(840, 560), (1360, 820), (1920, 1009)]


def screen(size, name, tab):
    d = Driver(size)
    d.load(name)
    if tab in ("plan", "simulacion"):
        d.store.calculate_plan()
    d.store.tab = tab
    d.frame()
    if tab == "simulacion":
        for _ in range(14):
            d.store.recruit("infantry")
        for i, tower in enumerate(d.store.tower_ids):
            d.store.picked, d.store.dest, d.store.mode = [f"S{i + 1}"], tower, "walk"
            d.store.send()
        d.store.advance(5)
    d.store.notice = None
    d.frame()
    return d


def drawn_texts(d):
    """Rectangle of every string of one frame, plus the strings that had to be shortened."""
    ui, rects, cut = d.app.ui, [], []
    text, wrap, fit = ui.text, ui.wrap, ui.fit

    def spy_text(txt, *args, **kwargs):
        rect = text(txt, *args, **kwargs)
        if str(txt) and ui.surface.get_clip().contains(rect):
            rects.append((str(txt), rect))
        return rect

    def spy_wrap(txt, area, kind="body", color=t.SOFT, gap=2):
        font = ui.fonts.get(kind)
        for i, line in enumerate(ui.lines(txt, kind, area[2])):
            rect = pygame.Rect((area[0], area[1] + i * (font.get_linesize() + gap)), font.size(line))
            if ui.surface.get_clip().contains(rect):
                rects.append((line, rect))
        return wrap(txt, area, kind, color, gap)

    def spy_fit(txt, kind, width):
        out = fit(txt, kind, width)
        if out != txt:
            cut.append(txt)
        return out

    ui.text, ui.wrap, ui.fit = spy_text, spy_wrap, spy_fit
    d.frame()
    del ui.text, ui.wrap, ui.fit
    return rects, cut


@pytest.mark.parametrize("desktop,expected", [((1366, 768), (1326, 678)), ((1920, 1080), (1360, 820)), ((800, 600), (840, 560))])
def test_the_first_window_fits_the_screen(desktop, expected):
    assert t.window_size(*desktop) == expected


@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("tab", ["inicio", "grafos", "plan", "simulacion"])
def test_no_text_covers_another_one_and_nothing_leaves_the_canvas(size, tab):
    d = screen(size, "escenario_gran_ciudadela.json", tab)
    rects, cut = drawn_texts(d)
    canvas = d.surface.get_rect()
    assert cut == [] and all(canvas.contains(r) for _, r in rects)
    clashes = [(a, b) for i, (a, ra) in enumerate(rects) for b, rb in rects[i + 1:]
               if ra.inflate(-2, -4).colliderect(rb.inflate(-2, -4))]
    assert clashes == []


@pytest.mark.parametrize("name", SCENARIOS)
def test_map_labels_of_every_scenario_never_overlap(name):
    for size in SIZES:
        for tab in ("plan", "simulacion"):
            d = screen(size, name, tab)
            placed = d.app.ui.labels.placed
            area = d.app.ui.labels.bounds
            assert placed and all(area.contains(r) for r in placed)
            assert all(r.collidelist(placed[i + 1:]) < 0 for i, r in enumerate(placed)), (name, size, tab)


def test_a_crowd_at_the_base_is_drawn_as_one_counter():
    d = Driver()
    d.load()
    d.store.calculate_plan()
    d.go("simulacion")
    for _ in range(14):
        d.store.recruit("infantry")
    assert "×14" in d.texts()


def test_the_file_chooser_keeps_the_application_visible_behind_it():
    d = Driver()
    d.click("Seleccionar archivo")
    d.frame()
    corner = tuple(d.surface.get_at((4, d.surface.get_height() - 4)))[:3]
    assert sum(corner) > 150                                    # dimmed paper, not a solid black screen
