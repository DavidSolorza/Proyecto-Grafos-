"""World-to-screen transform: both graphs share one plane, so one viewport fits them all."""
from math import dist

import pygame


class Viewport:
    """Fits every vertex of GE and GM inside `rect`, keeping the aspect ratio."""

    def __init__(self, rect: pygame.Rect, scenario: dict) -> None:
        self.rect = pygame.Rect(rect)
        pts = [v["coords"] for g in ("graph_e", "graph_m") for v in scenario[g]["vertices"]] or [[0, 0], [100, 60]]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        pad = max(max(xs), max(ys)) * 0.12 + 6          # same margin rule as the web map
        self.min_x, self.min_y = min(xs) - pad, min(ys) - pad
        w, h = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
        self.scale = min(self.rect.w / w, self.rect.h / h)
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
