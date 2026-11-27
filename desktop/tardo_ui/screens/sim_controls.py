"""Simulation panels: clock controls and the budget with the recruit buttons."""
import pygame

from tardo_ui import theme as t

STATUS = {"IDLE": ("Listo", "info"), "RUNNING": ("En combate", "warn"), "VICTORY_ELIMINATION": ("Victoria por eliminación", "ok"),
          "VICTORY_RESISTANCE": ("Victoria por resistencia", "ok"), "DEFEAT": ("Derrota", "bad")}
NAMES = {"infantry": "Infantería", "sniper": "Francotirador", "gunner": "Artillero"}


def controls(ui, box, store) -> None:
    sim, inner = store.sim, ui.card(box)
    label, tone = STATUS.get(sim["status"], (sim["status"], "info"))
    ui.badge((inner.x, inner.y), label, tone)
    ui.text(f"{sim['clock']:.1f}s / {sim['time_limit']:g}s", (inner.right, inner.y), "mono", t.INK, "topright")
    ui.bar((inner.x, inner.y + 28, inner.w, 8), sim["clock"] / sim["time_limit"])
    y, x = inner.y + 46, inner.x
    if ui.button((x, y, 104, 32), "Pausar" if store.running else "Iniciar", key="Iniciar", tone="on", enabled=not store.finished):
        store.toggle_play()
    x += 110
    if ui.button((x, y, 58, 32), "+1 s", enabled=not store.running and not store.finished, tone="ghost"):
        store.advance(1)
    x += 64
    for n in (1, 2, 5):
        if ui.button((x, y, 44, 32), f"{n}x", key=f"{n}x", tone="ghost", active=store.speed == n):
            store.speed = n
        x += 48
    if ui.button((inner.right - 104, y, 104, 32), "Reiniciar", tone="ghost"):
        store.reset_match()


def recruit(ui, box, store) -> None:
    sim = store.sim
    b = sim["budget"]
    inner = ui.card(box, "Presupuesto")
    amounts = (("Disponible", "available"), ("Reservado", "reserved"), ("Gastado", "spent"), ("Ganado", "earned"))
    for i, (label, field) in enumerate(amounts):                       # a 2 x 2 grid never needs to cut the figures
        ui.text(f"{label} ${b[field]:.0f}", (inner.x + (i % 2) * (inner.w // 2), inner.y - 3 + (i // 2) * 16), "mono",
                t.INK if i == 0 else t.SOFT, max_w=inner.w // 2 - 6)
    cfg = sim["defenders_config"]
    w = inner.w // 3
    for i, kind in enumerate(sorted(cfg, key=lambda k: cfg[k]["cost"])):
        c, x = cfg[kind], inner.x + i * w
        if ui.button((x, inner.y + 33, w - 8, 30), f"{NAMES[kind]}  ${c['cost']}", key=NAMES[kind], tone="ghost",
                     enabled=b["available"] >= c["cost"] and not store.finished, kind="small"):
            store.recruit(kind)
        for row, text in enumerate((f"daño {c['damage']:g} · alcance {c['base_range']:g}", f"{c['frequency']:g} ataques/s")):
            ui.text(text, (x + 2, inner.y + 66 + row * 15), "small", t.SOFT, max_w=w - 6)
