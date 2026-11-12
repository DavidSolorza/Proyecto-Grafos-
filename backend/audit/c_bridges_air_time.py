"""Audit checks for sections 8 to 11: bridges, helicopters, budget, logical clock and end conditions."""
from audit.core import Match, check

FRAGILE = "escenario_puentes.json"        # E_E1 has 3 uses, E_E2 only 1, and a slow convoy (match lasts 77 s)
CREW = "escenario_cuadrilla.json"         # repairs need 2 people at the base


def bridge(state, bridge_id):
    return next(b for b in state["bridges"] if b["id"] == bridge_id)


@check("§8", "Cada moto que termina de cruzar un puente le resta 1 (aunque lleve 2); caminar no lo desgasta")
def wear(api):
    m = Match(api, FRAGILE)
    m.buy("infantry", 3)
    m.move(["S1"], "V_C1", "walk")
    m.move(["S2", "S3"], "V_C1", "moto")
    state = m.tick(5.25)
    assert bridge(state, "E_E1")["hp"] == 2, "one crossing by a motorcycle with two riders must cost exactly 1"


@check("§8", "Con resistencia 0 el puente se destruye y no participa en búsquedas; el soldado a pie queda detenido")
def collapse_and_blocked(api):
    m = Match(api, FRAGILE)
    m.buy("infantry", 3)
    m.move(["S1"], "V_C1", "walk")
    m.move(["S2", "S3"], "V_C1", "moto")
    state = m.tick(13)
    assert bridge(state, "E_E2")["destroyed"] is True
    assert next(s for s in state["soldiers"] if s["id"] == "S1")["status"] == "WAITING"


@check("§8", "Tras el tiempo de reconstrucción el puente recupera su resistencia máxima y los detenidos reanudan solos")
def rebuild_and_resume(api):
    m = Match(api, FRAGILE)
    m.buy("infantry", 3)
    m.move(["S1"], "V_C1", "walk")
    m.move(["S2", "S3"], "V_C1", "moto")
    state = m.tick(37.75)
    assert bridge(state, "E_E2")["destroyed"] is True
    state = m.tick(0.5)                                             # 8 s collapse + 30 s repair = 38 s
    assert bridge(state, "E_E2")["destroyed"] is False and bridge(state, "E_E2")["hp"] == 1
    state = m.tick(15)
    assert next(s for s in state["soldiers"] if s["id"] == "S1")["status"] == "STATIONED"


@check("§3/§8", "La reconstrucción ocupa a N personas: quedan ocupadas y no atacan ni reciben órdenes hasta terminar")
def crew(api):
    m = Match(api, CREW)
    m.buy("infantry", 3)
    m.move(["S1"], "V_C1", "moto")
    state = m.tick(9)
    assert [s["status"] for s in state["soldiers"]][1:] == ["REPAIRING", "REPAIRING"]
    m.rejected("/transport/move", {"soldier_ids": ["S2"], "dest": "V_C1", "mode": "walk"}, "ocupado")
    state = m.tick(29.5)
    assert bridge(state, "E_E2")["destroyed"] is False and [s["status"] for s in state["soldiers"]][1:] == ["AT_BASE"] * 2


@check("§3/§8", "Una arista sin datos de puente es una calle (no se desgasta); un medio con tiempo null no puede usar la arista")
def roads_and_forbidden_modes(api):
    m = Match(api, CREW)
    assert api.get("/transport/path?src=V_BASE&dst=V_H1&mode=walk")[1]["path"] is None          # E_E4 only admits motorcycles
    assert api.get("/transport/path?src=V_BASE&dst=V_H1&mode=moto")[1]["path"]["time"] == 18.0  # 5 + 3 + 6 + 4
    m.buy("infantry")
    m.move(["S1"], "V_C2", "moto")                                  # V_C1 -> V_C2 is a plain road
    state = m.tick(14.5)
    assert [b["id"] for b in state["bridges"]] == ["E_E1", "E_E2"]  # roads are not reported as bridges


@check("§9", "Helicóptero: hasta 4 soldados; vuelo = distancia euclidiana / velocidad; reserva dinero y cupo al despegar")
def helicopter_flight(api):
    m = Match(api)
    m.buy("infantry", 4)
    state = m.ok("/transport/helicopter", {"soldier_ids": ["S1", "S2", "S3", "S4"], "dest": "V_C1"})["state"]
    assert state["budget"]["reserved"] == 200 and state["budget"]["available"] == 1400
    assert next(t for t in state["towers"] if t["vertex_id"] == "V_C1")["reserved"] == 3
    m.rejected("/transport/helicopter", {"soldier_ids": ["S1", "S2", "S3", "S4", "S5"], "dest": "V_C1"}, "1 a 4")


@check("§9", "Al llegar baja lo que cabe; el excedente va a la torre más cercana con cupo; todo es una operación (un uso, un cobro)")
def helicopter_surplus(api):
    m = Match(api)
    m.buy("infantry", 4)
    m.ok("/transport/helicopter", {"soldier_ids": ["S1", "S2", "S3", "S4"], "dest": "V_C1"})
    state = m.tick(4)
    towers = {t["vertex_id"]: t["occupants"] for t in state["towers"]}
    assert towers == {"V_C1": 3, "V_C2": 1} and state["helicopter"]["uses_left"] == 2
    assert state["budget"]["reserved"] == 0 and state["budget"]["spent"] == 600       # 4 x 100 + one flight of 200
    assert any("aterrizó en V_C1: bajan 3" in e["text"] for e in state["events"])


@check("§9", "Si no es posible ubicar a todos, regresan a la base; hay un máximo de usos configurable")
def helicopter_return_and_uses(api):
    m = Match(api)
    m.buy("infantry", 7)
    m.ok("/transport/helicopter", {"soldier_ids": ["S1", "S2", "S3", "S4"], "dest": "V_C1"})
    m.tick(4)
    m.ok("/transport/helicopter", {"soldier_ids": ["S5", "S6"], "dest": "V_C2"})
    m.tick(4)
    m.ok("/transport/helicopter", {"soldier_ids": ["S7"], "dest": "V_C1"})     # both towers are full: it must come back
    state = m.tick(6)
    assert next(s for s in state["soldiers"] if s["id"] == "S7")["status"] == "AT_BASE"
    m.rejected("/transport/helicopter", {"soldier_ids": ["S7"], "dest": "V_C2"}, "No quedan usos")


@check("§10", "Presupuesto disponible y reservado distintos; ninguna operación deja saldo negativo; traslados terrestres gratis")
def budget(api):
    m = Match(api)
    m.buy("gunner", 4)                                              # spends all 2000
    m.rejected("/units/recruit", {"type": "infantry", "count": 1}, "Presupuesto insuficiente")
    m.rejected("/transport/helicopter", {"soldier_ids": ["S1"], "dest": "V_C1"}, "Presupuesto insuficiente")
    state = m.move(["S1"], "V_C1", "walk")
    assert state["budget"]["available"] == 0 and state["budget"]["spent"] == 2000


@check("§11", "Reloj lógico en segundos, independiente de la frecuencia de dibujo (pasos de 0,25 s)")
def logical_clock(api):
    m = Match(api)
    assert m.tick(0.25)["clock"] == 0.25 and m.tick(1)["clock"] == 1.25 and m.tick(2.5)["clock"] == 3.75


@check("§11", "Fin: todas las máquinas destruidas = victoria por eliminación (14,25 s con 2 francotiradores)")
def end_elimination(api):
    m = Match(api)
    m.buy("sniper", 2)
    m.move(["S1", "S2"], "V_C1", "moto")
    state = m.tick(30)
    assert (state["status"], state["clock"]) == ("VICTORY_ELIMINATION", 14.25)


@check("§11", "Fin: una máquina viva llega a la salida = derrota")
def end_defeat(api):
    state = Match(api).tick(100)
    assert (state["status"], state["clock"]) == ("DEFEAT", 23.0)


@check("§11", "Fin: se llega al límite de tiempo sin llegada enemiga = victoria por resistencia")
def end_resistance(api):
    state = Match(api, FRAGILE, edit=lambda r: r["metadata"].update(time_limit=30)).tick(100)
    assert (state["status"], state["clock"]) == ("VICTORY_RESISTANCE", 30.0)


@check("§11", "Al terminar se detienen las actualizaciones")
def updates_stop(api):
    m = Match(api)
    done = m.tick(100)
    again = m.tick(50)
    assert (again["clock"], len(again["events"]), again["budget"]) == (done["clock"], len(done["events"]), done["budget"])
