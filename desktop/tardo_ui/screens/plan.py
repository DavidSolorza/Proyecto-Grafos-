"""Defense plan screen: minimum spanning tree, greedy tower selection and its step-by-step explanation."""
import pygame

from tardo_ui import theme as t
from tardo_ui.map.canvas import draw_legend, draw_map
from tardo_ui.screens.common import node_info, page_head, stat_grid


def draw(ui, rect, store, app) -> None:
    plan = store.plan
    page_head(ui, rect, "Fase 1 · Planificación", "Plan de defensa", "")
    side_w = 430
    mp = pygame.Rect(rect.x, rect.y + 54, rect.w - side_w - 16, rect.h - 54 - 54)
    draw_map(ui, mp, store, tree=store.show_tree, radii=store.show_radii, layers="both")
    draw_legend(ui, (mp.x, mp.bottom + 8), ["base", "candidate", "tower", "tree", "corridor"], mp.w)
    x = rect.right - side_w
    if ui.button((x, rect.y + 6, 180, 34), "Recalcular plan" if plan else "Calcular plan", key="Calcular plan", tone="on"):
        store.calculate_plan()
    if ui.button((x + 188, rect.y + 6, 110, 34), "Árbol T_E", key="Árbol", tone="ghost",
                 active=store.show_tree and bool(plan), enabled=bool(plan)):
        store.show_tree = not store.show_tree
    if ui.button((x + 306, rect.y + 6, 124, 34), "Radios Rv", key="Radios", tone="ghost",
                 active=store.show_radii and bool(plan), enabled=bool(plan)):
        store.show_radii = not store.show_radii
    inner = ui.card(pygame.Rect(x, mp.y, side_w, mp.h), "Resultado")
    if not plan:
        ui.wrap("Pulsa «Calcular plan» para ver el árbol, las torres y la cobertura.", inner, "body", t.SOFT)
        return
    y = stat_grid(ui, inner, [(str(len(plan["towers"])), "Torres"), (f"{plan['coverage_pct']}%", "Cobertura"),
                              (f"{plan['mst']['total_time']:.0f}s", "Peso MST"),
                              (str(len(plan["mst"]["edges"])), "Aristas")], cols=4) + 2
    y = towers_table(ui, inner, plan, y)
    y = watched(ui, inner, store, y + 2)
    if plan["unreachable"]:
        y = ui.wrap("Fuera de la componente de la base (no pueden ser torres): " + ", ".join(plan["unreachable"]),
                    (inner.x, y + 4, inner.w, 40), "small", t.TERRA)
    y = steps(ui, inner, plan, y + 6)
    node_info(ui, pygame.Rect(inner.x, max(y + 4, inner.bottom - 44), inner.w, 40), store)


def towers_table(ui, inner, plan, y) -> int:
    for label, dx in (("Torre", 0), ("Rv", 90), ("D_T", 150), ("S(p)", 220), ("Aporta", 300)):
        ui.text(label, (inner.x + dx, y), "small", t.SOFT)
    y += 18
    for tw in plan["towers"]:
        ui.text(tw["vertex_id"], (inner.x, y), "bold")
        for dx, val in ((90, f"{tw['rv']:g}"), (150, f"{tw['dt']:g}s"), (220, f"{tw['score']:.2f}"), (300, f"{tw['gain']:g} u.")):
            ui.text(val, (inner.x + dx, y + 1), "mono")
        y += 20
    return y


def watched(ui, inner, store, y) -> int:
    """Which corridors are under surveillance and how much of the labyrinth that is."""
    plan, total = store.plan, len(store.scenario["graph_m"]["corridors"])
    head = (f"Corredores vigilados: {len(plan['covered_corridors'])} de {total} "
            f"({plan['covered_length']:g} de {plan['total_length']:g} u. de longitud)")
    ui.text(head, (inner.x, y), "small", t.INK, max_w=inner.w)
    return ui.wrap(", ".join(plan["covered_corridors"]) or "ninguno", (inner.x, y + 16, inner.w, 40), "small", t.SOFT)


def steps(ui, inner, plan, y) -> int:
    ui.text("Paso a paso de la selección voraz", (inner.x, y), "bold")
    y += 22
    for st in plan["steps"]:
        ui.text(f"Iteración {st['iteration']}: gana {st['chosen']}  ·  vigila ahora: {', '.join(st['new_corridors']) or 'nada nuevo'}",
                (inner.x, y), "small", t.OCHRE, max_w=inner.w)
        y += 16
        for s in st["scores"]:
            win = s["vertex_id"] == st["chosen"]
            ui.text(f"{'> ' if win else '  '}{s['vertex_id']}: C = {s['gain']:g}, D_T = {s['dt']:g}s, S = {s['score']:.2f}",
                    (inner.x + 8, y), "mono", t.INK if win else t.SOFT, max_w=inner.w - 8)
            y += 16
        y += 4
    return y
