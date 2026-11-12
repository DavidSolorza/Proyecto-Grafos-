"""Home screen: load the scenario JSON (file chooser) and read its summary."""
import pygame

from tardo_ui import theme as t
from tardo_ui.screens.common import CHECKS, page_head, route_text, stat_grid

STEPS = (("01", "Carga el escenario", "Un JSON describe los dos grafos, el convoy y el presupuesto. El backend lo valida.", "inicio"),
         ("02", "Planifica la defensa", "Kruskal arma el árbol mínimo y un algoritmo voraz elige las torres.", "plan"),
         ("03", "Simula el combate", "Compra soldados, envíalos por tierra o aire y mira cómo el convoy esquiva el peligro.", "simulacion"))


def draw(ui, rect, store, app) -> None:
    y = page_head(ui, rect, "Proyecto 2 · Grafos", "La derrota del dictador General P. Tardo",
                  "Un convoy de máquinas avanza por un laberinto (grafo GM) hacia la salida. Los humanos resisten desde "
                  "una red elevada de caminos y puentes (grafo GE). Tú decides dónde construir las torres y a quién "
                  "enviar a cada una.") + 6
    w = (rect.w - 24) // 3
    for i, (n, title, text, target) in enumerate(STEPS):
        box = pygame.Rect(rect.x + i * (w + 12), y, w, 92)
        inner = ui.card(box)
        ui.text(n, (inner.x, inner.y - 2), "mono", t.OCHRE)
        ui.text(title, (inner.x, inner.y + 14), "h3")
        ui.wrap(text, (inner.x, inner.y + 38, inner.w, 50), "small", t.SOFT)
        if target != "inicio" and store.scenario and ui.clicked(box):
            store.tab = target
    y += 108
    left = pygame.Rect(rect.x, y, int(rect.w * 0.6) - 8, min(rect.bottom - y, 330))
    right = pygame.Rect(left.right + 16, y, rect.right - left.right - 16, 230)
    summary(ui, left, store)
    loader(ui, right, store, app)


def summary(ui, box, store) -> None:
    sc = store.scenario
    if not sc:
        inner = ui.card(box, "Sin escenario cargado")
        ui.wrap("La aplicación arranca vacía a propósito: no hay ninguna ruta fija. Elige un archivo .json con el "
                "botón de la derecha y aquí aparecerá el resumen.", inner, "body", t.SOFT)
        return
    m = sc["metadata"]
    inner = ui.card(box, m["title"])
    ui.badge((box.right - 14, box.y + 10), "escenario activo", "ok", "topright")
    y = stat_grid(ui, inner, [(f"${m['initial_budget']}", "Presupuesto"), (str(m["max_towers_k"]), "Torres máx. (K)"),
                              (f"{m['d0']}s", "Tiempo ref. D0"), (str(m["alpha"]), "Peligro alfa"),
                              (str(m["beta"]), "Altura beta"), (f"{m['bridge_repair_time']}s", "Reparar puente"),
                              (str(m.get("bridge_repair_crew", 0)), "Personas por reparación"),
                              (f"{m['time_limit']:.0f}s", "Límite de tiempo")]) + 4
    c = sc["convoy"]
    y = ui.wrap(f"Convoy: {c['tanks']} tanque(s), {c['trucks']} camión(es) y {c['robot_soldiers']} soldado(s) robot. "
                f"GE: {len(sc['graph_e']['vertices'])} vértices y {len(sc['graph_e']['edges'])} aristas. "
                f"GM: {len(sc['graph_m']['vertices'])} vértices y {len(sc['graph_m']['corridors'])} corredores.",
                (inner.x, y, inner.w, 50), "body", t.SOFT)
    y = ui.wrap("Camino inicial de menor costo: " + route_text(sc), (inner.x, y, inner.w, 40), "body", t.INK)
    x = inner.x
    for key, label in CHECKS:
        ok = (store.validation or {}).get(key)
        x = ui.badge((x, y + 4), ("OK  " if ok else "NO  ") + label, "ok" if ok else "bad").right + 8


def loader(ui, box, store, app) -> None:
    inner = ui.card(box, "Cargar escenario")
    ui.badge((box.right - 14, box.y + 10), ".json", "info", "topright")
    y = ui.wrap("Elige un archivo con los dos grafos, el convoy y los parámetros. El backend lo valida antes de usarlo.",
                (inner.x, inner.y, inner.w, 50), "body", t.SOFT)
    if ui.button((inner.x, y + 6, 240, 36), "Seleccionar archivo...", key="Seleccionar archivo", tone="on"):
        app.open_picker()
    ui.wrap("Los escenarios de ejemplo están en la carpeta docs del proyecto (botón «Ejemplos del proyecto» del selector).",
            (inner.x, y + 52, inner.w, 60), "small", t.SOFT)
