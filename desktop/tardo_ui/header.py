"""The top bar: gradient, logo mark, backend status and the pill-shaped tabs."""
import pygame

from tardo_ui import theme as t
from tardo_ui.store import TABS

HEADER_H = 96
EDGE = (60, 52, 42)


def draw_header(ui, store, width: int) -> None:
    ui.surface.blit(ui.gradient((width, HEADER_H), t.INK2, t.INK), (0, 0))
    pygame.draw.line(ui.surface, EDGE, (0, HEADER_H - 1), (width, HEADER_H - 1))
    cx, cy = 40, 34                                          # logo mark: a target with the ochre tower in the middle
    for radius in (20, 13):
        pygame.draw.circle(ui.surface, t.mix(t.SAND, t.INK, 0.35), (cx, cy), radius, 1)
    pygame.draw.circle(ui.surface, t.GOLD, (cx, cy), 5)
    ui.text("General P. Tardo", (72, 12), "h2", t.PAPER)
    ui.text("Simulador de grafos · Estructuras de Datos · cliente Pygame", (72, 44), "small", t.MAP_DIM)
    ok = store.backend_ok
    ui.badge((width - 20, 18), "Backend conectado" if ok else "Backend sin conexión", "ok" if ok else "bad", "topright")
    x = 22
    for key, label in TABS:
        rect = pygame.Rect(x, HEADER_H - 40, 150, 32)
        active = store.tab == key
        ui.hits[f"tab:{key}"] = rect
        if active:
            pygame.draw.rect(ui.surface, t.PAPER, rect, border_radius=16)
        elif ui.hovering(rect):
            pygame.draw.rect(ui.surface, t.INK2, rect, border_radius=16)
            pygame.draw.rect(ui.surface, EDGE, rect, 1, border_radius=16)
        ui.text(label, rect.center, "bold", t.INK if active else t.MAP_DIM, "center")
        if ui.clicked(rect):
            store.tab = key
        x += 156
