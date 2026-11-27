"""Moving parts of the map: soldiers, the convoy, helicopters, and the surveillance radii of towers."""
import pygame

from tardo_ui import theme as t
from tardo_ui.map.labels import around

LETTER = {"INFANTRY": "I", "SNIPER": "F", "GUNNER": "A"}
TYPE_COLOR = {"INFANTRY": t.LEAF, "SNIPER": (120, 170, 190), "GUNNER": t.GOLD}
AT_A_VERTEX = ("AT_BASE", "STATIONED", "DEPLOYED", "REPAIRING", "WAITING")


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


def cluster_items(members: list) -> list:
    """Up to three soldiers are drawn one by one; larger groups become one chip per type and state ("I x9")."""
    if len(members) <= 3:
        return [(s["type"], s["status"], "") for s in members]
    counts: dict = {}
    for s in members:
        state = s["status"] if s["status"] in ("REPAIRING", "WAITING") else ""
        counts[(s["type"], state)] = counts.get((s["type"], state), 0) + 1
    return [(kind, state, f"×{n}") for (kind, state), n in counts.items()]


def cluster_width(ui, items: list) -> int:
    return 4 + sum(17 + (ui.fonts.get("map").size(n)[0] + 4 if n else 0) for _, _, n in items)


def paint_cluster(ui, labels, items: list, rect: pygame.Rect) -> None:
    if len(items) > 1 or items[0][2]:
        labels.backdrop(rect)
    x = rect.x + 2
    for kind, state, count in items:
        center, color = (x + 8, rect.centery), TYPE_COLOR[kind]
        if state == "REPAIRING":
            pygame.draw.circle(ui.surface, t.OCHRE, center, 9, 2)
        pygame.draw.circle(ui.surface, t.mix(color, t.INK, 0.5) if state == "WAITING" else color, center, 7)
        ui.text(LETTER[kind], center, "map", t.INK, "center")
        x += 17
        if count:
            x = ui.text(count, (x + 1, rect.centery), "map", t.MAP_TEXT, "midleft").right + 3


def groups(vp, sim, parked: bool) -> dict:
    """Soldiers that share a screen position, split into standing at a vertex or travelling."""
    out: dict = {}
    for s in sim["soldiers"]:
        if s["status"] != "FLYING" and (s["status"] in AT_A_VERTEX) == parked:
            out.setdefault(vp.to_screen(s["xy"]), []).append(s)
    return out


def park_soldiers(ui, vp, sim, labels) -> None:
    """Soldiers standing at a vertex get a free place next to it, like one more label."""
    for (x, y), members in groups(vp, sim, True).items():
        items = cluster_items(members)
        spots = [("midtop", (x, y + 28))] + around(x, y, 18, "below")
        labels.add(5, (cluster_width(ui, items), 18), spots,
                   lambda rect, items=items: paint_cluster(ui, labels, items, rect))


def draw_travelling(ui, vp, sim, labels) -> None:
    for (x, y), members in groups(vp, sim, False).items():
        items = cluster_items(members)
        rect = pygame.Rect(0, 0, cluster_width(ui, items), 18)
        rect.center = (x, y)
        paint_cluster(ui, labels, items, rect)


def park_convoy(ui, vp, sim, labels) -> None:
    """The labels keep clear of the convoy marker, and its caption takes a free side."""
    if not any(e["alive"] for e in sim["convoy"]["enemies"]):
        return
    x, y = vp.to_screen(sim["convoy"]["xy"])
    labels.reserve((x, y), 26, 26)
    labels.text(3, "Convoy", t.HOT, around(x, y, 15, "above"), border=t.HOT)


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


def draw_flights(ui, vp, sim, labels) -> None:
    for f in sim["flights"]:
        x, y = vp.to_screen(f["xy"])
        pygame.draw.line(ui.surface, t.PAPER, (x - 10, y), (x + 10, y), 3)
        pygame.draw.line(ui.surface, t.PAPER, (x, y - 10), (x, y + 10), 3)
        text = f"{f['id'] if 'id' in f else 'H'}:{len(f['soldiers'])}"
        caption = pygame.Rect(0, 0, ui.fonts.get("map").size(text)[0] + 8, 15)
        caption.midbottom = (x, y - 12)
        labels.backdrop(caption)
        ui.text(text, caption.center, "map", t.PAPER, "center")


def draw_units(ui, vp, sim, labels) -> None:
    draw_travelling(ui, vp, sim, labels)
    draw_flights(ui, vp, sim, labels)
    draw_convoy(ui, vp, sim)
