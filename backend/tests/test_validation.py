"""Sections 3 and 12: the scenario is validated BEFORE it reaches the algorithms."""
import copy
import json

import pytest

from conftest import DOCS
from src.core.errors.handlers import AppError
from src.features.scenario.application.loader import ScenarioLoader

BASE = json.loads((DOCS / "escenario_general_p_tardo.json").read_text(encoding="utf-8"))

INVALID = {
    "dos bases": (lambda r: r["graph_e"]["vertices"][1].update(type="BASE"), "exactamente una BASE"),
    "sin base": (lambda r: r["graph_e"]["vertices"][0].update(type="TRANSIT"), "exactamente una BASE"),
    "id de vértice repetido": (lambda r: r["graph_e"]["vertices"][1].update(id="V_BASE"), "repetido"),
    "id de arista repetido": (lambda r: r["graph_e"]["edges"][1].update(id="E_E1"), "repetido"),
    "coordenada negativa en GE": (lambda r: r["graph_e"]["vertices"][0].update(coords=[-5, 10]), "positivos"),
    "coordenada cero en GE": (lambda r: r["graph_e"]["vertices"][0].update(coords=[0, 10]), "positivos"),
    "tipo de posición inválido": (lambda r: r["graph_e"]["vertices"][0].update(type="CASTLE"), "tipo inválido"),
    "tiempo a pie 0": (lambda r: r["graph_e"]["edges"][0].update(time_walk=0), "time_walk"),
    "tiempo en moto negativo": (lambda r: r["graph_e"]["edges"][0].update(time_moto=-1), "time_moto"),
    "puente con resistencia 0": (lambda r: r["graph_e"]["edges"][0].update(bridge_max_hp=0, bridge_current_hp=0), "puente"),
    "resistencia no entera": (lambda r: r["graph_e"]["edges"][0].update(bridge_max_hp=2.5), "puente"),
    "resistencia actual > máxima": (lambda r: r["graph_e"]["edges"][0].update(bridge_current_hp=99), "puente"),
    "arista a vértice inexistente": (lambda r: r["graph_e"]["edges"][0].update(v="NOPE"), "no existen"),
    "arista consigo misma": (lambda r: r["graph_e"]["edges"][0].update(v="V_BASE"), "consigo mismo"),
    "sin entrada": (lambda r: r["graph_m"]["vertices"][0].update(is_entry=False), "una entrada y una salida"),
    "dos salidas": (lambda r: r["graph_m"]["vertices"][1].update(is_exit=True), "una entrada y una salida"),
    "entrada igual a salida": (lambda r: r["graph_m"]["vertices"][0].update(is_exit=True), "una entrada"),
    "coordenada no numérica en GM": (lambda r: r["graph_m"]["vertices"][0].update(coords=["a", 1]), "finitos"),
    "corredor longitud 0": (lambda r: r["graph_m"]["edges"][0].update(length=0), "length"),
    "corredor velocidad negativa": (lambda r: r["graph_m"]["edges"][0].update(speed_allowed=-2), "speed_allowed"),
    "D0 = 0": (lambda r: r["metadata"].update(D0=0), "D0"),
    "K = 0": (lambda r: r["metadata"].update(max_towers_K=0), "max_towers_K"),
    "K decimal": (lambda r: r["metadata"].update(max_towers_K=2.5), "max_towers_K"),
    "presupuesto negativo": (lambda r: r["metadata"].update(initial_budget=-1), "initial_budget"),
    "tiempo de reparación 0": (lambda r: r["metadata"].update(bridge_repair_time=0), "bridge_repair_time"),
    "convoy vacío": (lambda r: r.update(convoy={"tanks": 0, "trucks": 0, "robot_soldiers": 0}), "al menos una máquina"),
    "convoy negativo": (lambda r: r.update(convoy={"tanks": -1, "trucks": 0, "robot_soldiers": 1}), "enteros"),
    "rv negativo": (lambda r: r["candidates_meta"][0].update(rv=-1), "rv"),
    "rv de un vértice que no es candidato": (lambda r: r["candidates_meta"][0].update(vertex_id="V_T1"), "CANDIDATE"),
    "falta un tipo de soldado": (lambda r: r["defenders_config"].pop("sniper"), "falta 'sniper'"),
    "soldado con costo 0": (lambda r: r["defenders_config"]["infantry"].update(cost=0), "cost"),
    "helicóptero sin velocidad": (lambda r: r.update(helicopter={"speed": 0}), "helicopter"),
    "falta graph_m": (lambda r: r.pop("graph_m"), "graph_m"),
}


@pytest.mark.parametrize("name", list(INVALID))
def test_invalid_scenarios_are_rejected_with_a_useful_message(name):
    mutate, expected = INVALID[name]
    raw = copy.deepcopy(BASE)
    mutate(raw)
    with pytest.raises(AppError) as err:
        ScenarioLoader.load_from_dict(raw)
    assert err.value.status_code == 400 and expected in err.value.message


@pytest.mark.parametrize("file", ["escenario_general_p_tardo.json", "escenario_complejo.json"])
def test_the_two_delivered_scenarios_are_valid(file):
    manager = ScenarioLoader.load_from_file(DOCS / file)
    assert all(manager.validate_initial_state().values())


def test_missing_connection_between_entry_and_exit_is_detected():
    raw = copy.deepcopy(BASE)
    raw["graph_m"]["edges"].pop()
    manager = ScenarioLoader.load_from_dict(raw)
    assert manager.validate_initial_state()["labyrinth_path_exists"] is False
