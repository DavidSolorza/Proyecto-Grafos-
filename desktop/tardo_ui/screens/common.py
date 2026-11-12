"""Pieces shared by the screens."""
import pygame

from tardo_ui import theme as t

CHECKS = (("has_base", "Exactamente una base"), ("base_connected", "La base tiene componente conexa"),
          ("labyrinth_path_exists", "Existe camino entrada > salida"))
TYPE_LABEL = {"BASE": "Base", "CANDIDATE": "Candidata", "TRANSIT": "Transito", "HELIPORT": "Helipuerto"}


def route_text(scenario: dict) -> str:
    """The cheapest entry -> exit route computed when the scenario was loaded (section 3)."""
    route = scenario.get("initial_route")
    if not route:
        return "No hay camino entre la entrada y la salida"
    return f"{' > '.join(route['vertices'])}  (t = {round(route['cost'], 2):g}s)"


def page_head(ui, rect, eyebrow, title, text) -> int:
    ui.text(eyebrow.upper(), (rect.x, rect.y), "small", t.OCHRE)
    ui.text(title, (rect.x, rect.y + 16), "h2")
    return ui.wrap(text, (rect.x, rect.y + 50, min(rect.w, 760), 60), "body", t.SOFT)


def stat_grid(ui, rect, stats, cols=4) -> int:
    """Grid of (value, label) tiles; returns the y below it."""
    w, h = rect.w // cols, 50
    for i, (value, label) in enumerate(stats):
        x, y = rect.x + (i % cols) * w, rect.y + (i // cols) * (h + 6)
        pygame.draw.rect(ui.surface, t.PAPER, (x, y, w - 8, h), border_radius=8)
        ui.text(value, (x + 10, y + 5), "h3", max_w=w - 28)
        ui.text(label, (x + 10, y + 29), "small", t.SOFT, max_w=w - 28)
    return rect.y + ((len(stats) + cols - 1) // cols) * (h + 6)


def node_info(ui, rect, store) -> int:
    """Details of the vertex clicked on the map."""
    sel, sc = store.selected, store.scenario
    if not sel or not sc:
        return ui.wrap("Haz clic en un vértice del mapa para ver sus datos.", rect, "body", t.SOFT)
    graph = sc["graph_e" if sel["network"] == "GE" else "graph_m"]
    v = next(x for x in graph["vertices"] if x["id"] == sel["id"])
    ui.text(v["id"], (rect.x, rect.y), "bold")
    if sel["network"] == "GE":
        kind = f"Red elevada, {TYPE_LABEL.get(v['type'], v['type'])}, altura z = {v['z']}"
    else:
        kind = "Laberinto, " + ("entrada" if v["is_entry"] else "salida" if v["is_exit"] else "interseccion")
    ui.text(f"{kind}  ·  coords ({v['coords'][0]}, {v['coords'][1]})", (rect.x, rect.y + 20), "small", t.SOFT, max_w=rect.w)
    return rect.y + 42
