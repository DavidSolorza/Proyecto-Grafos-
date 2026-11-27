"""World-to-screen transform: both graphs share one plane, so one viewport fits them all."""
from math import dist

import pygame

from tardo_ui import theme as t


class Viewport:
    """Fits every vertex of GE and GM inside `rect`, keeping the aspect ratio.

    The margin is measured in pixels with a clamp, so the graphs use all the room a large map offers and
    the labels of the peripheral vertices still fit inside a small one.
    """

    def __init__(self, rect: pygame.Rect, scenario: dict) -> None:
        self.rect = pygame.Rect(rect)
        pts = [v["coords"] for g in ("graph_e", "graph_m") for v in scenario[g]["vertices"]] or [[0, 0], [100, 60]]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        mx = t.clamp(34, self.rect.w * 0.06, 72)
        my = t.clamp(34, self.rect.h * 0.10, 64)
        w, h = max(1e-9, max(xs) - min(xs)), max(1e-9, max(ys) - min(ys))
        self.scale = min(max(1.0, self.rect.w - 2 * mx) / w, max(1.0, self.rect.h - 2 * my) / h)
        self.min_x, self.min_y = min(xs), min(ys)
        self.off_x = self.rect.x + (self.rect.w - w * self.scale) / 2
        self.off_y = self.rect.y + (self.rect.h - h * self.scale) / 2

    def to_screen(self, p) -> tuple[int, int]:
        return (round(self.off_x + (p[0] - self.min_x) * self.scale),
                round(self.off_y + (p[1] - self.min_y) * self.scale))

    def length(self, world_units: float) -> int:
        return max(1, round(world_units * self.scale))

    def pick(self, scenario: dict, layers: str, pos, reach: int = 16):
        """Nearest vertex under the mouse as (network, vertex) or None."""
        best, best_d = None, reach
        for net, graph, shown in (("GM", "graph_m", layers in ("both", "gm")), ("GE", "graph_e", layers in ("both", "ge"))):
            for v in scenario[graph]["vertices"] if shown else []:
                d = dist(self.to_screen(v["coords"]), pos)
                if d <= best_d:
                    best, best_d = (net, v), d
        return best
