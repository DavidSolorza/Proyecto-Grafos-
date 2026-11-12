"""Colors (same beige/black palette as the web client) and fonts."""
import os
from pathlib import Path

import pygame

PAPER, PAPER_DEEP, CARD = (240, 231, 214), (230, 217, 192), (250, 246, 236)
INK, INK2, SOFT, LINE = (20, 17, 14), (34, 29, 24), (106, 95, 82), (208, 195, 168)
SAND, OCHRE, GOLD = (216, 200, 166), (184, 137, 59), (217, 164, 65)
TERRA, HOT, SAGE, LEAF, RUST = (180, 71, 43), (224, 83, 50), (95, 122, 79), (143, 178, 124), (199, 112, 79)
MAP_TEXT, MAP_DIM = (232, 220, 196), (150, 138, 118)

SIZES = {"small": 13, "body": 15, "bold": 15, "h3": 18, "h2": 25, "title": 34, "mono": 13, "map": 12}
SERIF = "georgia,cambria,timesnewroman,serif"
SANS = "segoeui,calibri,arial,dejavusans,sans"
MONO = "consolas,couriernew,dejavusansmono,monospace"


WINDOWS_FONTS = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
# family -> (regular file, bold file): explicit files because the name "segoeui" resolves to the Light weight
FILES = {"sans": ("segoeui.ttf", "segoeuib.ttf"), "serif": ("georgia.ttf", "georgiab.ttf"), "mono": ("consola.ttf", "consolab.ttf")}
NAMES = {"sans": SANS, "serif": SERIF, "mono": MONO}


class Fonts:
    """Lazy font cache (pygame must be initialised first)."""

    def __init__(self) -> None:
        self._fonts: dict[str, pygame.font.Font] = {}

    def get(self, kind: str) -> pygame.font.Font:
        if kind not in self._fonts:
            family = "serif" if kind in ("h2", "title") else "mono" if kind == "mono" else "sans"
            bold = kind in ("bold", "h3", "h2", "title")
            path = WINDOWS_FONTS / FILES[family][bold]
            if path.exists():
                self._fonts[kind] = pygame.font.Font(str(path), SIZES[kind])
            else:                                                  # other systems: best installed match
                self._fonts[kind] = pygame.font.SysFont(NAMES[family], SIZES[kind], bold=bold)
        return self._fonts[kind]


BASE_SIZE = (1360, 820)             # the window size the layout was designed for (scale 1.0)
MIN_SCALE, MAX_SCALE = 0.7, 1.8     # the interface never shrinks or grows beyond these limits


def clamp(low: float, value: float, high: float) -> float:
    """Same idea as CSS clamp(min, preferred, max)."""
    return max(low, min(value, high))


def ui_scale(width: int, height: int) -> float:
    """Fluid scale of the whole interface: it follows the window size but stays between a minimum and a maximum."""
    raw = clamp(MIN_SCALE, min(width / BASE_SIZE[0], height / BASE_SIZE[1]), MAX_SCALE)
    return 1.0 if abs(raw - 1.0) < 0.02 else raw          # near the design size draw 1:1, so text stays crisp


def mix(a: tuple, b: tuple, t: float) -> tuple:
    """Linear blend between two colors (t = 0 gives a, t = 1 gives b)."""
    t = max(0.0, min(1.0, t))
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def heat(ratio: float) -> tuple:
    """Danger heat: calm sand to hot terracotta (same scale as the web map)."""
    return mix((216, 200, 166), (224, 83, 50), ratio)
