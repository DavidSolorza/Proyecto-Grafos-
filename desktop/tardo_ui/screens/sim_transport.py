"""Simulation panel: choose soldiers, destination and transport; consult the route."""
import pygame

from tardo_ui import theme as t
from tardo_ui.paging import WIDTH, paged
from tardo_ui.store import FREE

MODE_NAMES = {"walk": "a pie", "moto": "en moto"}

STATUS = {"AT_BASE": "en base", "STATIONED": "en torre", "MOVING": "en camino", "WAITING": "detenido",
          "FLYING": "volando", "REPAIRING": "reconstruyendo", "DEPLOYED": "en punto"}
MODES = (("walk", "A pie (1)"), ("moto", "Moto (1-2)"), ("air", "Helicóptero (hasta 4)"))
KIND = {"INFANTRY": "Infantería", "SNIPER": "Francotirador", "GUNNER": "Artillero"}
CHIP_H, CHIPS_PER_PAGE, PER_ROW = 38, 6, 3
DESTS_PER_PAGE = 5


def transport(ui, box, store) -> None:
    sim = store.sim
    heli = sim["helicopter"]
    inner = ui.card(box, "Soldados y transporte")
    ui.badge((box.right - 14, box.y + 9), f"vuelos: {heli['uses_left']} · ${heli['cost']:.0f}", "info", "topright")
    y = chips(ui, box, inner, store)
    destinations(ui, inner, store, y)
    y += 34
    w = (inner.w - 8) // 3
    for i, (key, label) in enumerate(MODES):
        rect = (inner.x + i * (w + 4), y, w, 28)
        if ui.button(rect, label, key=f"medio:{key}", tone="ghost", active=store.mode == key, kind="small"):
            store.mode, store.route_text = key, ""
    y += 34
    ready = bool(store.picked) and bool(store.dest) and not store.finished
    if ui.button((inner.x, y, 100, 30), "Enviar", enabled=ready, tone="on"):
        store.send()
    if ui.button((inner.x + 108, y, 100, 30), "Ver ruta", enabled=ready and store.mode != "air", tone="ghost"):
        store.show_route()
    hint = store.route_text or (f"Destino: {store.dest}" if store.dest else "Elige destino o haz clic en el mapa")
    ui.text(hint, (inner.x + 218, y + 7), "mono", t.INK, max_w=inner.w - 220)
    y += 34
    area = pygame.Rect(inner.x, y, inner.w, 32)
    for tr in paged(ui, store, "traslados", sim["transfers"], 2, area, (inner.right, y)):
        note = "detenido, esperando ruta" if tr["status"] == "WAITING" else MODE_NAMES.get(tr["mode"], tr["mode"])
        ui.text(f"{tr['id']}: {', '.join(tr['soldiers'])} > {tr['dest']} ({note})", (inner.x, y), "mono", t.SOFT,
                max_w=inner.w - 92)
        y += 15


def destinations(ui, inner, store, y) -> None:
    """Every GE position is a valid destination; towers and the base come first."""
    vertices = store.scenario["graph_e"]["vertices"]
    base = next(v["id"] for v in vertices if v["type"] == "BASE")
    first = [*store.tower_ids, base]
    ordered = first + sorted(v["id"] for v in vertices if v["id"] not in first)
    area = pygame.Rect(inner.x, y, inner.w, 28)
    shown = paged(ui, store, "destinos", ordered, DESTS_PER_PAGE, area, (inner.right, y + 4))
    w = (inner.w - WIDTH - 6 - 4 * (DESTS_PER_PAGE - 1)) // DESTS_PER_PAGE
    for i, dest in enumerate(shown):
        if ui.button((inner.x + i * (w + 4), y, w, 28), dest, key=f"dest:{dest}", tone="ghost",
                     active=store.dest == dest, kind="small"):
            store.dest, store.route_text = dest, ""


def chips(ui, box, inner, store) -> int:
    soldiers = store.sim["soldiers"]
    if not soldiers:
        ui.text("Compra un soldado para poder moverlo.", (inner.x, inner.y + 4), "body", t.SOFT)
        return inner.y + 34
    w = (inner.w - 4 * (PER_ROW - 1)) // PER_ROW
    rows = -(-min(len(soldiers), CHIPS_PER_PAGE) // PER_ROW)
    area = pygame.Rect(inner.x, inner.y, inner.w, rows * (CHIP_H + 4))
    title_right = box.x + 12 + ui.fonts.get("h3").size("Soldados y transporte")[0]
    shown = paged(ui, store, "soldados", soldiers, CHIPS_PER_PAGE, area, (title_right + 10 + WIDTH, box.y + 9))
    for i, s in enumerate(shown):
        rect = pygame.Rect(inner.x + (i % PER_ROW) * (w + 4), inner.y + (i // PER_ROW) * (CHIP_H + 4), w, CHIP_H)
        chip(ui, rect, s, store)
    return inner.y + rows * (CHIP_H + 4) + 4


def chip(ui, rect, s, store) -> None:
    """Two lines: who the soldier is, and where it is or what it is doing."""
    free, picked = s["status"] in FREE, s["id"] in store.picked
    if ui.button(rect, "", key=f"soldado:{s['id']}", tone="ghost", active=picked, enabled=free):
        store.toggle_pick(s["id"])
    ink = t.PAPER if picked else t.INK if free else t.mix(t.INK, t.PAPER, 0.55)
    where = f" {s['vertex']}" if free and s["status"] != "AT_BASE" else ""
    ui.text(f"{s['id']} · {KIND[s['type']]}", (rect.centerx, rect.y + 4), "small", ink, "midtop", rect.w - 8)
    ui.text(f"{STATUS[s['status']]}{where}", (rect.centerx, rect.y + 21), "small",
            t.SAND if picked else t.SOFT if free else ink, "midtop", rect.w - 8)
