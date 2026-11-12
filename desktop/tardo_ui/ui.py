"""Immediate-mode widgets: every frame the screens call these functions and get the clicks back."""
import pygame

from tardo_ui import effects, theme as t

TONES = {  # tone -> (background, text, border)
    "plain": (t.CARD, t.INK, t.LINE), "ghost": (t.PAPER, t.INK, t.LINE), "on": (t.INK, t.PAPER, t.INK),
    "gold": (t.GOLD, t.INK, t.OCHRE), "danger": (t.TERRA, t.PAPER, t.TERRA),
}
BADGES = {"ok": (t.SAGE, t.PAPER), "warn": (t.OCHRE, t.INK), "bad": (t.TERRA, t.PAPER), "info": (t.PAPER_DEEP, t.INK)}


class Ui:
    """Frame context: current mouse, the click of this frame and a registry of buttons (used by tests)."""

    def __init__(self, surface: pygame.Surface) -> None:
        self.surface, self.fonts = surface, t.Fonts()
        self.mouse, self.click, self.wheel, self.hits, self.lock = (0, 0), None, 0, {}, False
        self.viewport = None                       # last map viewport drawn
        self.scale, self.time_ms = 1.0, 0          # window scale (see App) and the application clock, for animations
        self._cache: dict = {}

    def begin(self, surface: pygame.Surface, events) -> None:
        self.surface, self.click, self.wheel, self.hits, self.lock = surface, None, 0, {}, False
        self.mouse = tuple(v / self.scale for v in pygame.mouse.get_pos())
        for e in events:
            if e.type == pygame.MOUSEMOTION:
                self.mouse = e.pos
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.click = self.mouse = e.pos
            elif e.type == pygame.MOUSEWHEEL:
                self.wheel += e.y

    # ---- input -------------------------------------------------------------------------
    def hovering(self, rect) -> bool:
        return not self.lock and pygame.Rect(rect).collidepoint(self.mouse)

    def clicked(self, rect) -> bool:
        return not self.lock and self.click is not None and pygame.Rect(rect).collidepoint(self.click)

    def scroll(self, rect) -> int:
        return self.wheel if self.hovering(rect) else 0

    # ---- text --------------------------------------------------------------------------
    def _render(self, text: str, kind: str, color) -> pygame.Surface:
        key = (text, kind, color)
        if key not in self._cache:
            if len(self._cache) > 3000:
                self._cache.clear()
            self._cache[key] = self.fonts.get(kind).render(text, True, color)
        return self._cache[key]

    def fit(self, text: str, kind: str, max_w: int) -> str:
        """Shorten the text with '...' so it fits the width."""
        font = self.fonts.get(kind)
        while text and font.size(text)[0] > max_w:
            text = text[:-2] + "…" if len(text) > 2 else ""
        return text

    def text(self, txt, pos, kind="body", color=t.INK, anchor="topleft", max_w=None) -> pygame.Rect:
        if max_w:
            txt = self.fit(str(txt), kind, max_w)
        img = self._render(str(txt), kind, color)
        rect = img.get_rect(**{anchor: pos})
        self.surface.blit(img, rect)
        return rect

    def wrap(self, txt, rect, kind="body", color=t.SOFT, gap=2) -> int:
        """Word-wrapped paragraph inside rect; returns the y below the last line."""
        font, y, line = self.fonts.get(kind), rect[1], ""
        for word in str(txt).split():
            trial = f"{line} {word}".strip()
            if font.size(trial)[0] > rect[2] and line:
                self.surface.blit(self._render(line, kind, color), (rect[0], y))
                y, line = y + font.get_linesize() + gap, word
            else:
                line = trial
        if line:
            self.surface.blit(self._render(line, kind, color), (rect[0], y))
            y += font.get_linesize() + gap
        return y

    # ---- shapes ------------------------------------------------------------------------
    def button(self, rect, label, key=None, tone="plain", active=False, enabled=True, kind="body") -> bool:
        rect = pygame.Rect(rect)
        self.hits[key or label] = rect
        bg, fg, border = TONES["on" if active else tone]
        hot = enabled and self.hovering(rect)
        if bg == t.INK:                                          # dark buttons get a soft vertical gradient
            self.surface.blit(self.gradient(rect.size, t.mix(t.INK, t.PAPER, 0.16 if hot else 0.07), t.INK, 8), rect)
        else:
            pygame.draw.rect(self.surface, t.mix(bg, t.GOLD, 0.25) if hot and not active else bg, rect, border_radius=8)
        pygame.draw.rect(self.surface, border, rect, 1, border_radius=8)
        color = fg if enabled else t.mix(fg, bg, 0.6)
        self.text(label, rect.center, kind, color, "center", rect.w - 10)
        return enabled and self.clicked(rect)

    def card(self, rect, title=None, dark=False) -> pygame.Rect:
        """Rounded panel with an optional title; returns the inner area."""
        rect = pygame.Rect(rect)
        self.shadow(rect, 12)
        top_color = t.INK2 if dark else t.mix(t.CARD, (255, 255, 255), 0.45)
        self.surface.blit(self.gradient(rect.size, top_color, t.INK if dark else t.CARD, 12), rect)
        pygame.draw.rect(self.surface, t.INK if dark else t.LINE, rect, 1, border_radius=12)
        top = 10
        if title:
            self.text(title, (rect.x + 12, rect.y + 9), "h3", t.PAPER if dark else t.INK)
            top = 36
        return pygame.Rect(rect.x + 12, rect.y + top, rect.w - 24, rect.h - top - 10)

    def gradient(self, size, top, bottom, radius=0) -> pygame.Surface:
        return effects.gradient(self._cache, size, top, bottom, radius)

    def shadow(self, rect, radius=12, spread=7, strength=34) -> None:
        effects.shadow(self._cache, self.surface, rect, radius, spread, strength)

    def bar(self, rect, frac, color=t.OCHRE) -> None:
        pygame.draw.rect(self.surface, t.PAPER_DEEP, rect, border_radius=4)
        done = pygame.Rect(rect[0], rect[1], int(rect[2] * max(0.0, min(1.0, frac))), rect[3])
        pygame.draw.rect(self.surface, color, done, border_radius=4)

    def badge(self, pos, label, tone="info", anchor="topleft") -> pygame.Rect:
        bg, fg = BADGES[tone]
        img = self._render(label, "small", fg)
        rect = img.get_rect(**{anchor: pos}).inflate(14, 6)
        pygame.draw.rect(self.surface, bg, rect, border_radius=10)
        self.surface.blit(img, img.get_rect(center=rect.center))
        return rect
