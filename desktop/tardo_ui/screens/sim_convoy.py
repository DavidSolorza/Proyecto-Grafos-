"""Simulation panels: the enemy convoy with its decision explained, the event log and the corridor table."""
import pygame

from tardo_ui import theme as t
from tardo_ui.paging import paged

KIND_COLOR = {"bridge": t.OCHRE, "combat": t.TERRA, "convoy": t.RUST, "air": (70, 120, 140), "buy": t.SAGE,
              "move": t.INK, "end": t.INK, "system": t.SOFT}
ENEMY = {"TANK": "Tanque", "TRUCK": "Camión", "ROBOT_SOLDIER": "Soldado robot"}


def convoy(ui, box, store) -> None:
    cv = store.sim["convoy"]
    inner = ui.card(box, "Convoy enemigo")
    y = inner.y - 4
    groups: dict = {}
    for e in cv["enemies"]:
        g = groups.setdefault(e["type"], {"n": 0, "alive": 0, "hp": 0, "max": 0, "reward": e["reward"]})
        g["n"] += 1
        g["alive"] += e["alive"]
        g["hp"] += e["hp"]
        g["max"] += e["max_hp"]
    for kind, g in groups.items():
        ui.text(ENEMY.get(kind, kind), (inner.x, y), "small", t.INK if g["alive"] else t.SOFT)
        bar_w = t.fluid(50, inner.w * 0.2, 150)
        ui.bar((inner.x + 100, y + 3, bar_w, 9), g["hp"] / g["max"], t.HOT if g["alive"] else t.SOFT)
        x = inner.x + 108 + bar_w
        ui.text(f"{g['alive']}/{g['n']} vivos · {g['hp']:.0f} HP · +${g['reward']}", (x, y), "mono", t.SOFT, max_w=inner.right - x)
        y += 18
    dec = cv.get("decision")
    y += 6
    ui.text("¿Por qué ese camino?", (inner.x, y), "bold")
    y += 20
    if not dec:
        ui.text("El convoy decide en cada intersección una vez que inicia.", (inner.x, y), "small", t.SOFT, max_w=inner.w)
        return
    y = ui.wrap(f"En {dec['at']} (t = {dec['time']}s): {dec['note']}.", (inner.x, y, inner.w, 40), "small", t.SOFT)
    for o in dec["options"][:max(1, min(5, (box.bottom - y - 4) // 16))]:
        chosen = o["corridor"] == dec["chosen"]["corridor"]
        ui.text(f"{'> ' if chosen else '  '}{o['corridor']} hacia {o['to']}   costo {o['cost']:.1f}", (inner.x, y), "mono",
                t.INK if chosen else t.SOFT, max_w=inner.w)
        y += 16


def event_log(ui, box, store) -> None:
    events = store.sim["events"][::-1]                                  # newest first
    inner = ui.card(box, "Bitácora: qué ocurrió y por qué")
    area = pygame.Rect(inner.x, inner.y, inner.w, inner.h)
    ui.text(f"{len(events)} eventos", (box.right - 224, box.y + 12), "mono", t.SOFT, "topright")
    store.log_scroll = max(0, min(store.log_scroll - ui.scroll(box) * 2, len(events) * 3))
    ui.surface.set_clip(area)
    y = area.y - store.log_scroll * 16
    for ev in events:
        step = ui.fonts.get("small").get_linesize() + 1
        if y + step * len(ui.lines(ev["text"], "small", area.w - 60)) > area.bottom:
            break                                                       # never show half a line
        ui.text(f"{ev['t']:6.2f}", (area.x, y), "mono", t.SOFT)
        y = ui.wrap(ev["text"], (area.x + 56, y, area.w - 60), "small", KIND_COLOR.get(ev["kind"], t.INK), gap=1) + 1
    ui.surface.set_clip(None)


def corridors(ui, box, store) -> None:
    """Corridor table; a wide panel shows two columns so fewer pages are needed."""
    inner = ui.card(box, "Corredores: tiempo, peligro y peso")
    cols = 2 if inner.w >= 640 else 1
    col_w = inner.w // cols
    offsets = (0, 84, 144, 214) if cols == 2 else (0, 110, 190, 280)
    for col in range(cols):
        for label, dx in zip(("Corredor", "t(e)", "P(e)", "w(e) = t + alfa·P"), offsets):
            ui.text(label, (inner.x + col * col_w + dx, inner.y), "small", t.SOFT)
    top = max([1.0] + [c["danger"] for c in store.sim["corridors"]])
    rows = max(1, (inner.bottom - inner.y - 18) // 17)
    shown = paged(ui, store, "corredores", store.sim["corridors"], rows * cols, box, (box.right - 228, box.y + 9))
    for i, c in enumerate(shown):
        x, y = inner.x + (i // rows) * col_w, inner.y + 18 + (i % rows) * 17
        pygame.draw.rect(ui.surface, t.heat(c["danger"] / top), (x - 7, y + 2, 4, 12))
        for dx, val in zip(offsets, (c["id"], f"{c['time']:.1f}", f"{c['danger']:.1f}", f"{c['weight']:.1f}")):
            ui.text(val, (x + dx, y), "mono")
