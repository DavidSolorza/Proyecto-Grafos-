"""Moving parts of the map: soldiers, the convoy, helicopters, and the surveillance radii of towers."""
import pygame

from tardo_ui import theme as t

LETTER = {"INFANTRY": "I", "SNIPER": "F", "GUNNER": "A"}
TYPE_COLOR = {"INFANTRY": t.LEAF, "SNIPER": (120, 170, 190), "GUNNER": t.GOLD}
AT_A_VERTEX = ("AT_BASE", "STATIONED", "REPAIRING", "WAITING")


def draw_radii(ui, vp, scenario, plan) -> None:
    """Rv circle of each chosen tower (translucent, so the corridors underneath stay visible)."""
    overlay = pygame.Surface(vp.rect.size, pygame.SRCALPHA)
    coords = {v["id"]: v["coords"] for v in scenario["graph_e"]["vertices"]}
    for tw in plan["towers"]:
        x, y = vp.to_screen(coords[tw["vertex_id"]])
        center, radius = (x - vp.rect.x, y - vp.rect.y), vp.length(tw["rv"])
        pygame.draw.circle(overlay, (*t.GOLD, 28), center, radius)
        pygame.draw.circle(overlay, (*t.GOLD, 150), center, radius, 1)
    ui.surface.blit(overlay, vp.rect.topleft)


def draw_soldiers(ui, vp, sim) -> None:
    stack: dict = {}
    for s in sim["soldiers"]:
        if s["status"] == "FLYING":
            continue
        x, y = vp.to_screen(s["xy"])
        if s["status"] in AT_A_VERTEX:
            y += 30                                              # below the vertex label
        n = stack[(x, y)] = stack.get((x, y), -1) + 1
        x += n * 15 - 8
        color = TYPE_COLOR[s["type"]]
        if s["status"] == "REPAIRING":
            pygame.draw.circle(ui.surface, t.OCHRE, (x, y), 10, 2)
        pygame.draw.circle(ui.surface, t.mix(color, t.INK, 0.5) if s["status"] == "WAITING" else color, (x, y), 7)
        ui.text(LETTER[s["type"]], (x, y), "map", t.INK, "center")


def draw_convoy(ui, vp, sim) -> None:
    alive = sum(1 for e in sim["convoy"]["enemies"] if e["alive"])
    if not alive:
        return
    x, y = vp.to_screen(sim["convoy"]["xy"])
    phase = (ui.time_ms % 1600) / 1600                                  # expanding ring: the convoy is alive and moving
    ring = 14 + round(16 * phase)
    glow = pygame.Surface((2 * ring + 4, 2 * ring + 4), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*t.HOT, round(150 * (1 - phase))), (ring + 2, ring + 2), ring, 2)
    ui.surface.blit(glow, (x - ring - 2, y - ring - 2))
    pygame.draw.circle(ui.surface, t.HOT, (x, y), 12)
    pygame.draw.circle(ui.surface, t.PAPER, (x, y), 12, 2)
    ui.text(str(alive), (x, y), "bold", t.INK, "center")
    ui.text("Convoy", (x, y - 16), "map", t.HOT, "midbottom")


def draw_flights(ui, vp, sim) -> None:
    for f in sim["flights"]:
        x, y = vp.to_screen(f["xy"])
        pygame.draw.line(ui.surface, t.PAPER, (x - 10, y), (x + 10, y), 3)
        pygame.draw.line(ui.surface, t.PAPER, (x, y - 10), (x, y + 10), 3)
        ui.text(f"{f['id'] if 'id' in f else 'H'}:{len(f['soldiers'])}", (x, y - 13), "map", t.PAPER, "midbottom")


def draw_units(ui, vp, sim) -> None:
    draw_soldiers(ui, vp, sim)
    draw_flights(ui, vp, sim)
    draw_convoy(ui, vp, sim)
