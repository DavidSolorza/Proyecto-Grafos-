"""Static layers of the map: corridors of GM, roads and bridges of GE, and their vertices."""
import pygame

from tardo_ui import theme as t
from tardo_ui.map.labels import along, around


def dashed(surface, color, a, b, width=2, dash=9, gap=6) -> None:
    """Dashed line between two screen points."""
    length = pygame.Vector2(b).distance_to(a)
    if length == 0:
        return
    step = (pygame.Vector2(b) - pygame.Vector2(a)) / length
    pos = 0.0
    while pos < length:
        end = min(pos + dash, length)
        pygame.draw.line(surface, color, pygame.Vector2(a) + step * pos, pygame.Vector2(a) + step * end, width)
        pos += dash + gap


def draw_corridors(ui, vp, scenario, sim, labels, covered=(), route=()) -> None:
    verts = {v["id"]: v for v in scenario["graph_m"]["vertices"]}
    live = {c["id"]: c for c in (sim or {}).get("corridors", [])}
    top = max([1.0] + [c["danger"] for c in live.values()])
    for c in scenario["graph_m"]["corridors"]:
        a, b = vp.to_screen(verts[c["u"]]["coords"]), vp.to_screen(verts[c["v"]]["coords"])
        color = t.heat(live[c["id"]]["danger"] / top) if c["id"] in live else t.RUST
        if c["id"] in route:                         # cheapest entry -> exit route (section 3): a wide band under the corridor
            pygame.draw.line(ui.surface, t.OCHRE, a, b, 9)
        dashed(ui.surface, color, a, b, 3 if c["id"] in covered else 2)
        if c["id"] in covered:
            mid = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
            pygame.draw.circle(ui.surface, t.LEAF, mid, 5)
            labels.reserve(mid, 10, 10)
        labels.text(6, c["id"], t.MAP_DIM, along(a, b), optional=True)


def bridge_label(br: dict) -> tuple[str, tuple]:
    if br["destroyed"]:
        return ("X sin cuadrilla" if br.get("waiting_crew") else f"X {br['repair_left']}s"), t.HOT
    return f"{br['hp']}/{br['max_hp']}", t.MAP_TEXT


def draw_roads(ui, vp, scenario, sim, labels, tree_ids=()) -> None:
    verts = {v["id"]: v for v in scenario["graph_e"]["vertices"]}
    live = {b["id"]: b for b in (sim or {}).get("bridges", [])}
    for e in scenario["graph_e"]["edges"]:
        a, b = vp.to_screen(verts[e["u"]]["coords"]), vp.to_screen(verts[e["v"]]["coords"])
        br, in_tree = live.get(e["id"]), e["id"] in tree_ids
        hurt = br and br["hp"] < br["max_hp"]
        color = t.HOT if br and br["destroyed"] else t.LEAF if in_tree else t.GOLD if hurt else (232, 220, 196)
        if tree_ids and not in_tree and not (br and br["destroyed"]):
            color = t.mix(color, t.INK, 0.6)
        if br and br["destroyed"]:
            dashed(ui.surface, color, a, b, 3, 8, 6)
        else:
            pygame.draw.line(ui.surface, color, a, b, 4 if in_tree else 2)
        if br:
            label, tone = bridge_label(br)
            labels.text(2, label, tone, along(a, b), border=t.HOT if br["destroyed"] else None)


def tower_pill(ui, labels, pos, tower) -> None:
    """Occupancy of a tower: "used/capacity" plus one dot per slot (solid = inside, gold = reserved)."""
    used, cap = tower["occupants"] + tower["reserved"], tower["capacity"]
    text = f"{used}/{cap}"
    text_w = ui.fonts.get("bold").size(text)[0]

    def paint(rect):
        labels.backdrop(rect, t.OCHRE)
        ui.text(text, (rect.x + 6, rect.centery), "bold", t.GOLD, "midleft")
        for i in range(cap):
            fill = t.LEAF if i < tower["occupants"] else t.GOLD if i < used else (80, 72, 60)
            pygame.draw.circle(ui.surface, fill, (rect.x + text_w + 14 + i * 10, rect.centery), 4)

    labels.add(0, (text_w + cap * 10 + 14, 20), around(*pos, 15, "above"), paint)


def draw_vertices_e(ui, vp, scenario, sim, labels, tower_ids, selected) -> None:
    occupancy = {tw["vertex_id"]: tw for tw in (sim or {}).get("towers", [])}
    for v in scenario["graph_e"]["vertices"]:
        x, y = vp.to_screen(v["coords"])
        tower = v["id"] in tower_ids
        if tower:                                              # soft halo around the chosen towers
            halo = pygame.Surface((46, 46), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*t.GOLD, 46), (23, 23), 22)
            ui.surface.blit(halo, (x - 23, y - 23))
        if selected == v["id"]:
            pygame.draw.circle(ui.surface, t.PAPER, (x, y), 17, 2)
        kind = v["type"]
        if kind == "BASE":
            pygame.draw.rect(ui.surface, t.PAPER, (x - 9, y - 9, 18, 18), border_radius=3)
        elif kind == "CANDIDATE":
            pts = [(x, y - 11), (x + 11, y), (x, y + 11), (x - 11, y)]
            pygame.draw.polygon(ui.surface, t.GOLD if tower else (138, 122, 92), pts)
            pygame.draw.polygon(ui.surface, t.GOLD if tower else t.INK, pts, 2)
        elif kind == "HELIPORT":
            pygame.draw.circle(ui.surface, (168, 156, 132), (x, y), 10)
            ui.text("H", (x, y), "bold", t.INK, "center")
        else:
            pygame.draw.circle(ui.surface, (168, 156, 132), (x, y), 5)
        size = 12 if kind == "TRANSIT" else 22
        labels.reserve((x, y), size, size)
        labels.text(1, v["id"], t.MAP_TEXT, around(x, y, size // 2 + 2, "below"))
        if tower and v["id"] in occupancy:
            tower_pill(ui, labels, (x, y), occupancy[v["id"]])


def draw_vertices_m(ui, vp, scenario, labels, selected) -> None:
    for v in scenario["graph_m"]["vertices"]:
        x, y = vp.to_screen(v["coords"])
        color = t.LEAF if v["is_entry"] else t.HOT if v["is_exit"] else t.RUST
        if selected == v["id"]:
            pygame.draw.circle(ui.surface, t.PAPER, (x, y), 16, 2)
        pygame.draw.polygon(ui.surface, color, [(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)])
        pygame.draw.polygon(ui.surface, t.INK, [(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)], 1)
        labels.reserve((x, y), 18, 18)
        tag = "ENTRADA" if v["is_entry"] else "SALIDA" if v["is_exit"] else ""
        label = f"{tag} {v['id']}" if tag and tag not in v["id"].upper() else v["id"]
        labels.text(1 if tag else 4, label, color, around(x, y, 11, "above"), border=color if tag else None)
