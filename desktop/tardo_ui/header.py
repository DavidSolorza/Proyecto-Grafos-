"""The top bar: gradient, logo mark, backend status and the pill-shaped tabs."""
import pygame

from tardo_ui import theme as t
from tardo_ui.store import TABS

HEADER_H = 76
EDGE = (60, 52, 42)


def draw_header(ui, store, width: int) -> None:
    """One row: logo and title on the left, tabs after them, backend status on the right."""
    ui.surface.blit(ui.gradient((width, HEADER_H), t.INK2, t.INK), (0, 0))
    pygame.draw.line(ui.surface, EDGE, (0, HEADER_H - 1), (width, HEADER_H - 1))
    cx, cy = 40, HEADER_H // 2                               # logo mark: a target with the ochre tower in the middle
    for radius in (20, 13):
        pygame.draw.circle(ui.surface, t.mix(t.SAND, t.INK, 0.35), (cx, cy), radius, 1)
    pygame.draw.circle(ui.surface, t.GOLD, (cx, cy), 5)
    title = ui.text("General P. Tardo", (72, 13), "h2", t.PAPER)
    subtitle = ui.text("Estructuras de Datos · cliente Pygame", (72, 48), "small", t.MAP_DIM)
    ok = store.backend_ok
    badge = ui.badge((width - 20, cy), "Backend conectado" if ok else "Backend sin conexión", "ok" if ok else "bad", "midright")
    x = max(title.right, subtitle.right) + t.fluid(16, width * 0.025, 48)
    tab_w = t.fluid(104, (badge.left - x - 16) / len(TABS) - 6, 150)
    for key, label in TABS:
        rect = pygame.Rect(x, cy - 17, tab_w, 34)
        active = store.tab == key
        ui.hits[f"tab:{key}"] = rect
        if active:
            pygame.draw.rect(ui.surface, t.PAPER, rect, border_radius=17)
        elif ui.hovering(rect):
            pygame.draw.rect(ui.surface, t.INK2, rect, border_radius=17)
            pygame.draw.rect(ui.surface, EDGE, rect, 1, border_radius=17)
        ui.text(label, rect.center, "bold", t.INK if active else t.MAP_DIM, "center", tab_w - 10)
        if ui.clicked(rect):
            store.tab = key
        x += tab_w + 6
