"""Places the texts of the map so they do not cover each other or the vertex symbols."""
import pygame


def around(x: int, y: int, gap: int, first: str = "below") -> list:
    """Candidate anchors around a point: the preferred side first, then the others, then farther away."""
    spots = []
    for g in (gap, gap + 13, gap + 26):
        sides = {"below": ("midtop", (x, y + g)), "above": ("midbottom", (x, y - g)),
                 "right": ("midleft", (x + g, y)), "left": ("midright", (x - g, y))}
        spots.append(sides[first])
        spots += [spot for side, spot in sides.items() if side != first]
        d = round(g * 0.7)
        spots += [("topleft", (x + d, y + d)), ("topright", (x - d, y + d)),
                  ("bottomleft", (x + d, y - d)), ("bottomright", (x - d, y - d))]
    return spots


def along(a, b) -> list:
    """Candidate anchors along an edge, starting at its middle."""
    spots = []
    for f in (0.5, 0.36, 0.64, 0.24, 0.76):
        x, y = round(a[0] + (b[0] - a[0]) * f), round(a[1] + (b[1] - a[1]) * f)
        spots += [("center", (x, y)), ("midbottom", (x, y - 3)), ("midtop", (x, y + 3))]
    return spots


class Labels:
    """Collects requests, then places them by priority (lower first) in the first free candidate."""

    def __init__(self, ui, bounds: pygame.Rect) -> None:
        self.ui, self.bounds = ui, pygame.Rect(bounds).inflate(-6, -6)
        self.taken: list = []
        self.requests: list = []
        self.placed: list = []                          # rectangles of the labels drawn (checked by tests)

    def reserve(self, center, w: int, h: int) -> None:
        """Keep labels away from a symbol already drawn."""
        rect = pygame.Rect(0, 0, w, h)
        rect.center = center
        self.taken.append(rect)

    def add(self, priority: int, size, spots: list, paint, optional: bool = False) -> None:
        self.requests.append((priority, len(self.requests), size, spots, paint, optional))

    def text(self, priority: int, text: str, color, spots, kind="map", border=None, optional=False) -> None:
        w, h = self.ui.fonts.get(kind).size(text)

        def paint(rect):
            self.backdrop(rect, border)
            self.ui.text(text, rect.center, kind, color, "center")

        self.add(priority, (w + 6, h), spots, paint, optional)

    def backdrop(self, rect, border=None) -> None:
        key = ("backdrop", rect.size)
        if key not in self.ui._cache:
            surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(surf, (20, 17, 14, 205), surf.get_rect(), border_radius=5)
            self.ui._cache[key] = surf
        self.ui.surface.blit(self.ui._cache[key], rect)
        if border:
            pygame.draw.rect(self.ui.surface, border, rect, 1, border_radius=5)

    def spot(self, size, spots) -> pygame.Rect | None:
        for anchor, pos in spots:
            rect = pygame.Rect((0, 0), size)
            setattr(rect, anchor, pos)
            if self.bounds.contains(rect) and rect.collidelist(self.taken) < 0:
                return rect
        return None

    def flush(self) -> None:
        for _, _, size, spots, paint, optional in sorted(self.requests, key=lambda r: r[:2]):
            rect = self.spot(size, spots)
            if rect is None:
                if optional:                            # corridor ids are also listed in the corridor table
                    continue
                rect = pygame.Rect((0, 0), size)
                setattr(rect, *spots[0])
                rect.clamp_ip(self.bounds)
            self.taken.append(rect)
            self.placed.append(rect)
            paint(rect)
        self.requests = []
