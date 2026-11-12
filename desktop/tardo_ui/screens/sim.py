"""Simulation screen: map with units on the left, command panels on the right, explanation log below the map."""
import pygame

from tardo_ui import theme as t
from tardo_ui.map.canvas import draw_legend, draw_map
from tardo_ui.screens import sim_controls, sim_convoy, sim_transport
from tardo_ui.screens.common import node_info, page_head

END = {"VICTORY_ELIMINATION": ("Victoria por eliminación", t.SAGE), "VICTORY_RESISTANCE": ("Victoria por resistencia", t.SAGE),
       "DEFEAT": ("Derrota", t.TERRA)}
RIGHT_W = 540


def draw(ui, rect, store, app) -> None:
    if not store.plan:
        inner = ui.card(pygame.Rect(rect.x, rect.y, 560, 150), "Primero el plan")
        ui.wrap("La simulación necesita las torres elegidas por el árbol mínimo y el algoritmo voraz.", inner, "body", t.SOFT)
        if ui.button((inner.x, inner.y + 56, 200, 34), "Calcular plan", key="ir al plan", tone="on"):
            store.tab = "plan"
        return
    if not store.sim:
        inner = ui.card(pygame.Rect(rect.x, rect.y, 560, 170), "Todo listo para el combate")
        ui.wrap(f"Se crea una partida nueva con las {len(store.plan['towers'])} torres del plan. Después no se pueden mover.",
                inner, "body", t.SOFT)
        if ui.button((inner.x, inner.y + 60, 220, 34), "Crear simulación", tone="on"):
            store.reset_match()
        return
    page_head(ui, pygame.Rect(rect.x, rect.y, rect.w, 40), "Fase 2 · Combate en tiempo lógico", "Simulación", "")
    left_w = rect.w - RIGHT_W - 12
    log_h = max(150, int(rect.h * 0.28))
    mp = pygame.Rect(rect.x, rect.y + 54, left_w, rect.h - 54 - log_h - 80)
    banner = store.finished and not store.hide_end
    draw_map(ui, mp, store, units=True, layers="both", interactive=not banner)
    draw_legend(ui, (mp.x, mp.bottom + 6), ["base", "tower", "road", "corridor", "convoy", "soldier"], mp.w)
    info = pygame.Rect(mp.x, mp.bottom + 30, mp.w, 44)
    node_info(ui, info, store)
    bottom = pygame.Rect(rect.x, rect.bottom - log_h, left_w, log_h)
    bottom_panel(ui, bottom, store)
    right(ui, pygame.Rect(rect.right - RIGHT_W, rect.y, RIGHT_W, rect.h), store)
    if banner:
        end_banner(ui, mp, store)


def bottom_panel(ui, box, store) -> None:
    if store.bottom_tab == "bitacora":
        sim_convoy.event_log(ui, box, store)
    else:
        sim_convoy.corridors(ui, box, store)
    for i, (key, label) in enumerate((("bitacora", "Bitácora"), ("corredores", "Corredores"))):
        if ui.button((box.right - 214 + i * 104, box.y + 6, 98, 26), label, key=f"pestaña:{key}", tone="ghost",
                     active=store.bottom_tab == key, kind="small"):
            store.bottom_tab = key


def right(ui, box, store) -> None:
    y = box.y
    for height, fn in ((98, sim_controls.controls), (118, sim_controls.recruit), (250, sim_transport.transport),
                       (box.h - 98 - 118 - 250 - 24, sim_convoy.convoy)):
        fn(ui, pygame.Rect(box.x, y, box.w, height), store)
        y += height + 8


def end_banner(ui, mp, store) -> None:
    title, color = END[store.sim["status"]]
    box = pygame.Rect(0, 0, min(520, mp.w - 40), 210)
    box.center = mp.center
    pygame.draw.rect(ui.surface, t.CARD, box, border_radius=14)
    pygame.draw.rect(ui.surface, color, box, 3, border_radius=14)
    ui.text(title, (box.centerx, box.y + 22), "h2", color, "midtop")
    ui.wrap(store.sim["end_reason"], (box.x + 24, box.y + 70, box.w - 48), "body", t.SOFT)
    b = store.sim["budget"]
    ui.text(f"Tiempo {store.sim['clock']:.2f}s  ·  disponible ${b['available']:.0f}  ·  ganado ${b['earned']:.0f}",
            (box.centerx, box.y + 128), "mono", t.INK, "midtop")
    if ui.button((box.x + 24, box.bottom - 54, 190, 36), "Jugar de nuevo", tone="on"):
        store.reset_match()
    if ui.button((box.right - 214, box.bottom - 54, 190, 36), "Ver mapa", tone="ghost"):
        store.hide_end = True
