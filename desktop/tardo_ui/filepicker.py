"""In-window file chooser, so the user picks the scenario JSON from the interface (no fixed paths)."""
import os
import string
from pathlib import Path

import pygame

from tardo_ui import theme as t

ROW = 28
EXAMPLES = Path(__file__).resolve().parents[2] / "docs"


def list_dir(folder: Path) -> list[tuple[str, bool]]:
    """Visible sub-folders first, then .json files, each sorted by name."""
    try:
        items = [(p.name, p.is_dir()) for p in folder.iterdir() if not p.name.startswith(".")]
    except OSError:
        return []
    return sorted((i for i in items if i[1] or i[0].lower().endswith(".json")),
                  key=lambda i: (not i[1], i[0].lower()))


def drives() -> list[Path]:
    return [Path(f"{c}:/") for c in string.ascii_uppercase if os.path.exists(f"{c}:/")] if os.name == "nt" else []


class FilePicker:
    """Modal dialog. `draw` returns ("choose", path), ("cancel", None) or None while still open."""

    def __init__(self, start=None) -> None:
        self.folder = Path(start) if start and Path(start).is_dir() else Path.cwd()
        self.scroll = 0
        self.entries = list_dir(self.folder)

    def go(self, folder: Path) -> None:
        self.folder, self.scroll = folder, 0
        self.entries = list_dir(folder)

    def draw(self, ui, screen_rect):
        pygame.draw.rect(ui.surface, (20, 17, 14, 0), screen_rect)
        dim = pygame.Surface(screen_rect.size, pygame.SRCALPHA)
        dim.fill((20, 17, 14, 170))
        ui.surface.blit(dim, screen_rect.topleft)
        box = pygame.Rect(0, 0, min(760, screen_rect.w - 40), min(560, screen_rect.h - 40))
        box.center = screen_rect.center
        inner = ui.card(box, "Elegir escenario (.json)")
        ui.text(str(self.folder), (inner.x, inner.y), "mono", t.SOFT, max_w=inner.w)
        x, y = inner.x, inner.y + 24
        shortcuts = [("Inicio", Path.home()), ("Ejemplos del proyecto", EXAMPLES)] + [(str(d), d) for d in drives()]
        for label, target in shortcuts:
            w = ui.fonts.get("body").size(label)[0] + 22
            if target.is_dir() and ui.button((x, y, w, 28), label, key=f"ir:{label}", tone="ghost"):
                self.go(target)
            x += w + 6
        area = pygame.Rect(inner.x, y + 38, inner.w, inner.h - 108)
        pygame.draw.rect(ui.surface, t.PAPER, area, border_radius=8)
        rows = [("..  (carpeta superior)", True, self.folder.parent)] + [
            (n + ("/" if d else ""), d, self.folder / n) for n, d in self.entries]
        self.scroll = max(0, min(self.scroll - ui.scroll(area), max(0, len(rows) - area.h // ROW)))
        ui.surface.set_clip(area)
        result = None
        for i, (label, is_dir, path) in enumerate(rows[self.scroll:]):
            r = pygame.Rect(area.x, area.y + i * ROW, area.w, ROW)
            if ui.hovering(r):
                pygame.draw.rect(ui.surface, t.PAPER_DEEP, r)
            ui.text(label, (r.x + 10, r.y + 5), "body", t.INK if not is_dir else t.OCHRE, max_w=r.w - 20)
            ui.hits[f"fila:{label}"] = r
            if ui.clicked(r) and area.collidepoint(ui.click):
                if is_dir:
                    self.go(path)
                    break
                result = ("choose", path)
        ui.surface.set_clip(None)
        if not self.entries:
            ui.text("No hay carpetas ni archivos .json aquí", area.center, "body", t.SOFT, "center")
        if ui.button((box.right - 130, box.bottom - 46, 110, 32), "Cancelar", key="Cancelar"):
            return ("cancel", None)
        return result
