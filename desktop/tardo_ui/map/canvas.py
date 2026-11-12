"""The map widget: draws both graphs, the plan and the units, and lets the user inspect vertices."""
import pygame

from tardo_ui import theme as t
from tardo_ui.map.layers import draw_corridors, draw_roads, draw_vertices_e, draw_vertices_m
from tardo_ui.map.units import draw_radii, draw_units
from tardo_ui.map.view import Viewport

LEGEND = {
    "base": ((240, 231, 214), "Base"), "candidate": ((138, 122, 92), "Candidata"), "tower": (t.GOLD, "Torre elegida"),
    "heliport": ((168, 156, 132), "Helipuerto (H)"), "road": ((232, 220, 196), "Camino / puente (GE)"),
    "tree": (t.LEAF, "Arbol minimo T_E"), "corridor": (t.RUST, "Corredor (GM)"), "convoy": (t.HOT, "Convoy"),
    "soldier": (t.LEAF, "Soldado (I, F, A)"), "route": (t.OCHRE, "Camino inicial de menor costo"),
}


def map_background(ui, rect: pygame.Rect) -> pygame.Surface:
    """Dark stage with a warm glow and a dotted grid (cached per size)."""
    key = ("stage", rect.size)
    if key not in ui._cache:
        w, h = rect.size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(ui.gradient(rect.size, t.INK2, t.INK, 12), (0, 0))
        glow = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(16):                                      # nested ellipses: the alpha grows towards the center
            size_w, size_h = w * (1.0 - i / 18), h * 1.1 * (1.0 - i / 18)
            pygame.draw.ellipse(glow, (*t.GOLD, 2 + i * 2), (w / 2 - size_w / 2, -size_h * 0.45, size_w, size_h))
        surf.blit(glow, (0, 0))
        step = 26
        for gx in range(step, w, step):
            for gy in range(step, h, step):
                pygame.draw.circle(surf, (216, 200, 166, 26), (gx, gy), 1)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=12)
        surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        ui._cache[key] = surf
    return ui._cache[key]


def draw_map(ui, rect, store, units=False, tree=False, radii=False, layers="both", interactive=True, route=False) -> None:
    rect = pygame.Rect(rect)
    ui.shadow(rect, 12, strength=44)
    ui.surface.blit(map_background(ui, rect), rect)
    pygame.draw.rect(ui.surface, (60, 52, 42), rect, 1, border_radius=12)
    sc = store.scenario
    if not sc:
        ui.text("Carga un escenario para ver el mapa", rect.center, "h3", t.MAP_DIM, "center")
        return
    vp = ui.viewport = Viewport(rect.inflate(-24, -24), sc)      # kept so tests and tooltips can convert coordinates
    plan, sim = store.plan, store.sim
    tree_ids = [e["id"] for e in plan["mst"]["edges"]] if tree and plan else []
    covered = plan["covered_corridors"] if radii and plan else []
    ui.surface.set_clip(rect)
    if layers in ("both", "gm"):
        route_ids = ((sc.get("initial_route") or {}).get("corridors", [])) if route else []
        draw_corridors(ui, vp, sc, sim, covered, route_ids)
    if layers in ("both", "ge"):
        if radii and plan:
            draw_radii(ui, vp, sc, plan)
        draw_roads(ui, vp, sc, sim, tree_ids)
    sel = store.selected or {}
    if layers in ("both", "gm"):
        draw_vertices_m(ui, vp, sc, sel.get("id") if sel.get("network") == "GM" else None)
    if layers in ("both", "ge"):
        draw_vertices_e(ui, vp, sc, sim, store.tower_ids, sel.get("id") if sel.get("network") == "GE" else None)
    if units and sim:
        draw_units(ui, vp, sim)
    ui.surface.set_clip(None)
    if interactive and ui.clicked(rect):
        hit = vp.pick(sc, layers, ui.click)
        store.selected = {"network": hit[0], "id": hit[1]["id"]} if hit else None


def draw_legend(ui, pos, keys, max_w) -> int:
    """Row of color swatches under the map; returns the y below it."""
    x, y = pos
    for key in keys:
        color, label = LEGEND[key]
        width = ui.fonts.get("small").size(label)[0] + 26
        if x + width > pos[0] + max_w:
            x, y = pos[0], y + 20
        pygame.draw.rect(ui.surface, color, (x, y + 3, 12, 12), border_radius=3)
        pygame.draw.rect(ui.surface, t.INK, (x, y + 3, 12, 12), 1, border_radius=3)
        ui.text(label, (x + 18, y + 1), "small", t.SOFT)
        x += width + 8
    return y + 22
