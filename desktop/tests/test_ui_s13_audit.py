"""Section 13, bullet by bullet: what the Pygame window must represent and let the user do."""
import pygame
import pytest

from conftest import Driver
from tardo_ui import theme as t

BASE, CANDIDATE, ROAD = (240, 231, 214), (138, 122, 92), (232, 220, 196)


def sim_screen(name="escenario_general_p_tardo.json"):
    d = Driver()
    d.load(name)
    d.store.calculate_plan()
    d.go("simulacion")
    return d


def test_the_map_represents_both_graphs_base_candidates_towers_soldiers_convoy_and_bridges():
    d = sim_screen("escenario_complejo.json")
    d.store.recruit("infantry")
    d.frame()
    area = d.app.ui.viewport.rect
    present = {name: d.count_color(color, area) for name, color in {
        "base": BASE, "candidata": CANDIDATE, "torre": t.GOLD, "camino/puente (GE)": ROAD, "corredor (GM)": t.RUST,
        "convoy": t.HOT, "soldado": t.LEAF}.items()}
    assert all(count > 0 for count in present.values()), present
    labels = " ".join(d.texts())
    assert "V_BASE" in labels and "M_ENTRADA" in labels and "M_SALIDA" in labels
    assert any(line in ("8/8", "10/10") for line in d.texts())                    # bridges show their strength


def test_load_and_validate_scenarios_with_the_reasons_shown():
    d = Driver()
    d.load()
    assert all("OK" in line for line in d.texts() if "Exactamente una base" in line or "componente conexa" in line or "camino entrada" in line)
    assert d.store.load_file(__import__("pathlib").Path(__file__)) is False                      # not JSON: the reason is displayed
    assert d.store.notice[1] == "error" and "JSON válido" in d.store.notice[0]


def test_inspect_the_minimum_tree_and_the_proposed_distribution():
    d = Driver()
    d.load("escenario_complejo.json")
    d.go("plan")
    d.click("Calcular plan")
    text = " | ".join(d.texts())
    for expected in ("V_C4", "V_C3", "72.2%", "Peso MST", "Paso a paso de la selección voraz", "Corredores vigilados", "V_ISLA"):
        assert expected in text, expected
    d.click("Árbol")                                                       # the tree can be shown and hidden
    assert d.store.show_tree is False


def test_buy_soldiers_order_transports_and_consult_routes_and_algorithmic_results():
    d = sim_screen()
    d.click("Francotirador")
    d.click("soldado:S1")
    d.click("dest:V_C1")
    d.click("medio:moto")
    d.click("Ver ruta")
    assert d.store.route_text == "V_BASE > V_T1 > V_C1 (8.0s)"
    d.click("Enviar")
    for _ in range(9):
        d.click("+1 s")
    text = " | ".join(d.texts())
    assert "¿Por qué ese camino?" in text and "costo" in text                  # decision of the convoy
    d.click("pestaña:corredores")
    text = " | ".join(d.texts())
    assert "w(e) = t + alfa·P" in text and "133.3" in text and "208.0" in text   # t, P and w of the corridors


def test_observe_the_destruction_and_the_enabling_of_bridges():
    d = sim_screen("escenario_puentes.json")
    for _ in range(3):
        d.click("Infantería")
    d.click("soldado:S1")
    d.click("soldado:S2")
    d.click("dest:V_C1")
    d.click("medio:moto")
    d.click("Enviar")
    for _ in range(9):
        d.click("+1 s")
    assert any(line.startswith("X ") for line in d.texts()), "a collapsed bridge shows its countdown"
    assert any("colapsó" in line for line in d.texts())
    for _ in range(30):
        d.click("+1 s")
    after = d.texts()
    assert any("fue reconstruido y vuelve a estar habilitado" in line for line in after)
    assert not any(line.startswith("X ") for line in after)


def test_consult_indicators_and_the_final_result():
    d = sim_screen()
    text = " | ".join(d.texts())
    for indicator in ("Disponible $2000", "Reservado $0", "Gastado $0", "Ganado $0", "0.0s / 300s", "Listo"):
        assert indicator in text, indicator
    d.play_to_end()
    text = " | ".join(d.texts())
    assert "Derrota" in text and "Una máquina viva llegó a la salida." in text and "Tiempo 23.00s" in text


@pytest.mark.parametrize("operation,expected", [
    ("compra", "Compraste 1 × infantry por $100"), ("traslado", "salen de V_BASE hacia V_C1"), ("llegada", "llegaron a V_C1")])
def test_the_interface_explains_what_happened_and_why(operation, expected):
    d = sim_screen()
    d.click("Infantería")
    d.click("soldado:S1")
    d.click("dest:V_C1")
    d.click("medio:moto")
    d.click("Enviar")
    for _ in range(9):
        d.click("+1 s")
    assert any(expected in line for line in d.texts()), operation
