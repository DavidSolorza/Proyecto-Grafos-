"""Simulation screen: map with units on the left, command panels on the right, explanation log below the map."""
import pygame

from tardo_ui import theme as t
from tardo_ui.map.canvas import draw_legend, draw_map, legend_height
from tardo_ui.screens import sim_controls, sim_convoy, sim_transport
from tardo_ui.screens.common import node_info, page_head

END = {"VICTORY_ELIMINATION": ("Victoria por eliminación", t.SAGE), "VICTORY_RESISTANCE": ("Victoria por resistencia", t.SAGE),
       "DEFEAT": ("Derrota", t.TERRA)}
LEGEND_KEYS = ["base", "tower", "road", "corridor", "convoy", "soldier"]


def draw(ui, rect, store, app) -> None:
    if not store.plan:
        inner = ui.card(pygame.Rect(rect.centerx - 280, rect.y + rect.h // 5, 560, 150), "Primero el plan")
        ui.wrap("La simulación necesita las torres elegidas por el árbol mínimo y el algoritmo voraz.", inner, "body", t.SOFT)
        if ui.button((inner.x, inner.y + 56, 200, 34), "Calcular plan", key="ir al plan", tone="on"):
            store.tab = "plan"
        return
    if not store.sim:
        inner = ui.card(pygame.Rect(rect.centerx - 280, rect.y + rect.h // 5, 560, 170), "Todo listo para el combate")
        ui.wrap(f"Se crea una partida nueva con las {len(store.plan['towers'])} torres del plan. Después no se pueden mover.",
                inner, "body", t.SOFT)
        if ui.button((inner.x, inner.y + 60, 220, 34), "Crear simulación", tone="on"):
            store.reset_match()
        return
    page_head(ui, pygame.Rect(rect.x, rect.y, rect.w, 40), "Fase 2 · Combate en tiempo lógico", "Simulación", "")
    right_w = t.fluid(450, rect.w * 0.34, 560)
    left_w = rect.w - right_w - 12
    log_h = t.fluid(150, rect.h * 0.27, 270)
    under = legend_height(ui, LEGEND_KEYS, left_w) + 50          # legend, vertex details and gaps below the map
    mp = pygame.Rect(rect.x, rect.y + 54, left_w, rect.h - 54 - log_h - under)
    banner = store.finished and not store.hide_end
    before = store.selected
    draw_map(ui, mp, store, units=True, layers="both", interactive=not banner)
    chosen = store.selected
    if chosen and chosen != before and chosen["network"] == "GE":     # a click on the map picks the destination
        store.dest, store.route_text = chosen["id"], ""
    below = draw_legend(ui, (mp.x, mp.bottom + 6), LEGEND_KEYS, mp.w)
    info = pygame.Rect(mp.x, below + 2, mp.w, 40)
    node_info(ui, info, store)
    bottom = pygame.Rect(rect.x, rect.bottom - log_h, left_w, log_h)
    bottom_panel(ui, bottom, store)
    right(ui, pygame.Rect(rect.right - right_w, rect.y, right_w, rect.h), store)
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
    for height, fn in ((96, sim_controls.controls), (142, sim_controls.recruit), (270, sim_transport.transport),
                       (box.h - 96 - 142 - 270 - 24, sim_convoy.convoy)):
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
