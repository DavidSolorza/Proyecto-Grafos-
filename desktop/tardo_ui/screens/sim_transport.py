"""Simulation panel: choose soldiers, destination and transport; consult the route."""
import pygame

from tardo_ui import theme as t
from tardo_ui.store import FREE

STATUS = {"AT_BASE": "en base", "STATIONED": "en torre", "MOVING": "en camino", "WAITING": "detenido",
          "FLYING": "volando", "REPAIRING": "reconstruyendo"}
MODES = (("walk", "A pie (1)"), ("moto", "Moto (1-2)"), ("air", "Helicóptero (hasta 4)"))
CHIP_W, CHIP_H, MAX_CHIPS = 150, 26, 12


def transport(ui, box, store) -> None:
    sim = store.sim
    heli = sim["helicopter"]
    inner = ui.card(box, "Soldados y transporte")
    ui.badge((box.right - 14, box.y + 9), f"helicópteros: {heli['uses_left']} · ${heli['cost']:.0f}", "info", "topright")
    y = chips(ui, inner, store)
    base = next(v["id"] for v in store.scenario["graph_e"]["vertices"] if v["type"] == "BASE")
    x = inner.x
    for dest in [*store.tower_ids, base]:
        if ui.button((x, y, 84, 28), dest, key=f"dest:{dest}", tone="ghost", active=store.dest == dest, kind="small"):
            store.dest, store.route_text = dest, ""
        x += 88
    y += 34
    x = inner.x
    for key, label in MODES:
        w = 130 if key != "air" else 170
        if ui.button((x, y, w, 28), label, key=f"medio:{key}", tone="ghost", active=store.mode == key, kind="small"):
            store.mode, store.route_text = key, ""
        x += w + 4
    y += 34
    ready = bool(store.picked) and bool(store.dest)
    if ui.button((inner.x, y, 100, 30), "Enviar", enabled=ready, tone="on"):
        store.send()
    if ui.button((inner.x + 108, y, 100, 30), "Ver ruta", enabled=ready and store.mode != "air", tone="ghost"):
        store.show_route()
    ui.text(store.route_text, (inner.x + 218, y + 7), "mono", t.INK, max_w=inner.w - 220)
    y += 34
    for tr in sim["transfers"][:2]:
        note = "detenido, esperando ruta" if tr["status"] == "WAITING" else tr["mode"]
        ui.text(f"{tr['id']}: {', '.join(tr['soldiers'])} > {tr['dest']} ({note})", (inner.x, y), "mono", t.SOFT, max_w=inner.w)
        y += 15


def chips(ui, inner, store) -> int:
    soldiers = store.sim["soldiers"]
    if not soldiers:
        ui.text("Compra un soldado para poder moverlo.", (inner.x, inner.y + 4), "body", t.SOFT)
        return inner.y + 34
    per_row = max(1, inner.w // (CHIP_W + 4))
    for i, s in enumerate(soldiers[:MAX_CHIPS]):
        rect = (inner.x + (i % per_row) * (CHIP_W + 4), inner.y + (i // per_row) * (CHIP_H + 4), CHIP_W, CHIP_H)
        free = s["status"] in FREE
        where = f" {s['vertex']}" if free else ""
        if ui.button(rect, f"{s['id']} {s['type'][:3]} {STATUS[s['status']]}{where}", key=f"soldado:{s['id']}", tone="ghost",
                     active=s["id"] in store.picked, enabled=free, kind="small"):
            store.toggle_pick(s["id"])
    rows = (min(len(soldiers), MAX_CHIPS) + per_row - 1) // per_row
    if len(soldiers) > MAX_CHIPS:
        ui.text(f"+{len(soldiers) - MAX_CHIPS} más", (inner.right, inner.y + rows * (CHIP_H + 4) - 2), "small", t.SOFT, "topright")
    return inner.y + rows * (CHIP_H + 4) + 6
