"""Cached visual effects: vertical gradients with rounded corners and soft drop shadows."""
import pygame

from tardo_ui import theme as t


def gradient(cache: dict, size, top, bottom, radius: int = 0) -> pygame.Surface:
    """Vertical gradient (optionally with rounded corners), cached per size and colors."""
    key = ("gradient", tuple(size), top, bottom, radius)
    if key not in cache:
        w, h = size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            pygame.draw.line(surf, t.mix(top, bottom, y / max(1, h - 1)), (0, y), (w, y))
        if radius:
            mask = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
            surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        cache[key] = surf
    return cache[key]


def shadow(cache: dict, surface: pygame.Surface, rect, radius: int = 12, spread: int = 7, strength: int = 34) -> None:
    """Soft drop shadow under a rounded rectangle (cached per size)."""
    rect = pygame.Rect(rect)
    key = ("shadow", rect.size, radius, spread, strength)
    if key not in cache:
        surf = pygame.Surface((rect.w + 2 * spread, rect.h + 2 * spread), pygame.SRCALPHA)
        for grow in range(spread, 0, -1):
            alpha = round(strength * (1 - grow / spread) ** 2) + 2
            box = pygame.Rect(spread - grow, spread - grow, rect.w + 2 * grow, rect.h + 2 * grow)
            pygame.draw.rect(surf, (20, 17, 14, alpha), box, border_radius=radius + grow)
        cache[key] = surf
    surface.blit(cache[key], (rect.x - spread, rect.y - spread + 3))
