"""Graphs screen: both networks on one plane, with layers and vertex inspection."""
import pygame

from tardo_ui import theme as t
from tardo_ui.map.canvas import draw_legend, draw_map
from tardo_ui.screens.common import node_info, page_head, route_text

MODES = (("both", "Ambas capas"), ("ge", "Red elevada GE"), ("gm", "Laberinto GM"))
EXPLAIN = ("Dos grafos independientes comparten el plano: el convoy camina por GM y los soldados defienden desde GE. "
           "No existe ninguna arista entre ambos; solo se relacionan por la distancia (alcance de disparo).")


def draw(ui, rect, store, app) -> None:
    sc = store.scenario
    page_head(ui, rect, "Fase 0 · Escenario", "Dos grafos que comparten el mismo plano", "")
    side_w = 360
    mp = pygame.Rect(rect.x, rect.y + 54, rect.w - side_w - 16, rect.h - 54 - 54)
    draw_map(ui, mp, store, layers=store.layers, route=store.show_initial_route)
    keys = ["base", "candidate", "heliport", "road", "corridor"] + (["route"] if store.show_initial_route else [])
    draw_legend(ui, (mp.x, mp.bottom + 8), keys, mp.w)
    side = pygame.Rect(mp.right + 16, mp.y, side_w, mp.h)
    inner = ui.card(side, "Capas")
    x = inner.x
    for key, label in MODES:
        if ui.button((x, inner.y, 104, 30), label, key=label, tone="ghost", active=store.layers == key, kind="small"):
            store.layers = key
        x += 108
    y = ui.wrap(EXPLAIN, (inner.x, inner.y + 44, inner.w, 120), "small", t.SOFT) + 8
    if sc:
        if ui.button((inner.x, y, 190, 28), "Camino inicial", key="Camino inicial", tone="ghost", active=store.show_initial_route, kind="small"):
            store.show_initial_route = not store.show_initial_route
        y = ui.wrap("Camino de menor costo de la entrada a la salida: " + route_text(sc), (inner.x, y + 34, inner.w, 90), "small", t.INK) + 8
    pygame.draw.line(ui.surface, t.LINE, (inner.x, y), (inner.right, y))
    y = node_info(ui, pygame.Rect(inner.x, y + 8, inner.w, 60), store) + 6
    if sc:
        ui.wrap(f"Componente de la base: {len(sc['graph_e']['connected_component_base'])} de "
                f"{len(sc['graph_e']['vertices'])} vértices alcanzables. Solo en ellos se pueden poner torres.",
                (inner.x, y, inner.w, 80), "small", t.SOFT)
