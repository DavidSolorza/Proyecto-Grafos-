"""Simulation panels: the enemy convoy with its decision explained, the event log and the corridor table."""
import pygame

from tardo_ui import theme as t

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
        ui.bar((inner.x + 110, y + 3, 150, 9), g["hp"] / g["max"], t.HOT if g["alive"] else t.SOFT)
        ui.text(f"{g['alive']}/{g['n']} vivos · {g['hp']:.0f} HP · +${g['reward']} c/u", (inner.x + 270, y), "mono", t.SOFT,
                max_w=inner.w - 270)
        y += 18
    dec = cv.get("decision")
    y += 6
    ui.text("¿Por qué ese camino?", (inner.x, y), "bold")
    y += 20
    if not dec:
        ui.text("El convoy decide en cada intersección una vez que inicia.", (inner.x, y), "small", t.SOFT, max_w=inner.w)
        return
    y = ui.wrap(f"En {dec['at']} (t = {dec['time']}s): {dec['note']}.", (inner.x, y, inner.w, 40), "small", t.SOFT)
    for o in dec["options"][:3]:
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
        ui.text(f"{ev['t']:6.2f}", (area.x, y), "mono", t.SOFT)
        y = ui.wrap(ev["text"], (area.x + 56, y, area.w - 60), "small", KIND_COLOR.get(ev["kind"], t.INK), gap=1) + 1
        if y > area.bottom:
            break
    ui.surface.set_clip(None)


def corridors(ui, box, store) -> None:
    inner = ui.card(box, "Corredores del laberinto: tiempo, peligro y peso")
    heads = (("Corredor", 0), ("t(e)", 110), ("P(e)", 190), ("w(e) = t + alfa·P", 280))
    for label, dx in heads:
        ui.text(label, (inner.x + dx, inner.y), "small", t.SOFT)
    top = max([1.0] + [c["danger"] for c in store.sim["corridors"]])
    y = inner.y + 18
    for c in store.sim["corridors"]:
        if y > inner.bottom - 14:
            break
        pygame.draw.rect(ui.surface, t.heat(c["danger"] / top), (inner.x - 6, y + 2, 4, 12))
        for dx, val in ((0, c["id"]), (110, f"{c['time']:.1f}"), (190, f"{c['danger']:.1f}"), (280, f"{c['weight']:.1f}")):
            ui.text(val, (inner.x + dx, y), "mono")
        y += 17
