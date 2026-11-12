"""Audit checks for sections 3, 4 and 12: the graphs, the scenario file and the defense plan."""
import json
import urllib.error
import urllib.request

from audit.core import Match, check, scenario


def rejects(api, edit, text):
    status, body = api.post("/scenario/upload", scenario(edit=edit))
    assert status == 400 and text in body["error"], f"{status}: {body}"


@check("§12", "El usuario selecciona el JSON desde la interfaz; no hay rutas fijas (el servidor arranca vacío)")
def starts_empty(api):
    status, body = api.get("/scenario/current")
    assert body["loaded"] is False and body["data"] is None and api.post("/defense/plan")[0] == 409


@check("§12", "El JSON contiene ambos grafos, candidatas, base, entrada y salida, unidades, convoy y parámetros")
def full_file_is_accepted(api):
    status, body = api.post("/scenario/upload", scenario())
    data = api.get("/scenario/current")[1]["data"]
    assert status == 200 and all(k in data for k in ("graph_e", "graph_m", "candidates_meta", "convoy", "defenders_config", "metadata"))


@check("§12", "Un archivo que no es JSON se rechaza con un mensaje claro y el escenario activo no cambia")
def bad_file_keeps_scenario(api):
    Match(api, plan=False)
    req = urllib.request.Request(api.url + "/api/scenario/upload", data=b"esto no es json", method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req)
        raise AssertionError("accepted")
    except urllib.error.HTTPError as err:
        assert err.code == 400
    assert api.get("/scenario/current")[1]["loaded"] is True


@check("§3 GE", "Exactamente una base")
def exactly_one_base(api):
    rejects(api, lambda r: r["graph_e"]["vertices"][1].update(type="BASE"), "exactamente una BASE")
    rejects(api, lambda r: r["graph_e"]["vertices"][0].update(type="TRANSIT"), "exactamente una BASE")


@check("§3 GE", "Identificador único; coordenadas finitas positivas; tipo válido; aristas entre vértices existentes")
def ge_vertex_rules(api):
    rejects(api, lambda r: r["graph_e"]["vertices"][1].update(id="V_BASE"), "repetido")
    rejects(api, lambda r: r["graph_e"]["vertices"][0].update(coords=[-5, 10]), "positivos")
    rejects(api, lambda r: r["graph_e"]["vertices"][0].update(type="CASTLE"), "tipo inválido")
    rejects(api, lambda r: r["graph_e"]["edges"][0].update(v="NOPE"), "no existen")


@check("§3 GE", "Tiempos a pie y en moto positivos cuando se permite el medio; puentes con resistencia entera positiva")
def ge_edge_rules(api):
    rejects(api, lambda r: r["graph_e"]["edges"][0].update(time_walk=0), "time_walk")
    rejects(api, lambda r: r["graph_e"]["edges"][0].update(bridge_max_hp=0, bridge_current_hp=0), "puente")
    rejects(api, lambda r: r["graph_e"]["edges"][0].update(bridge_max_hp=2.5), "puente")
    ok = scenario(edit=lambda r: r["graph_e"]["edges"][0].update(time_walk=None))        # walking not allowed: valid
    assert api.post("/scenario/upload", ok)[0] == 200


@check("§3 GM", "Entrada y salida diferentes; corredores con longitud y velocidad positivas")
def gm_rules(api):
    rejects(api, lambda r: r["graph_m"]["vertices"][0].update(is_exit=True), "entrada")
    rejects(api, lambda r: r["graph_m"]["edges"][0].update(speed_allowed=0), "speed_allowed")
    rejects(api, lambda r: r["graph_m"]["edges"][0].update(length=-3), "length")


@check("§3 GM", "t(e) = l(e) / v(e) y se calcula el camino de menor costo inicial entre entrada y salida")
def initial_route(api):
    Match(api, plan=False)
    data = api.get("/scenario/current")[1]["data"]
    route = data["initial_route"]
    assert route["vertices"] == ["M_ENTRADA", "M_N1", "M_N2", "M_SALIDA"] and route["cost"] == 8.0 + 7.0 + 8.0   # 40/5 + 35/5 + 40/5
    assert api.post("/scenario/upload", scenario(edit=lambda r: r["graph_m"]["edges"].pop()))[0] == 400    # no path: rejected


@check("§4", "MST sobre la componente de la base con el tiempo a pie; T_E incluye todos sus vértices (V-1 aristas)")
def mst(api):
    Match(api, plan=False)
    plan = api.post("/defense/plan")[1]["plan"]
    assert plan["mst"]["total_time"] == 45.0 and len(plan["mst"]["edges"]) == 4 and plan["mst"]["dist_from_base"]["V_C1"] == 20.0


@check("§4", "Posiciones fuera de la componente de la base no pueden ser torres (V_ISLA)")
def unreachable(api):
    Match(api, "escenario_complejo.json", plan=False)
    plan = api.post("/defense/plan")[1]["plan"]
    assert plan["unreachable"] == ["V_ISLA"] and "V_ISLA" not in [t["vertex_id"] for t in plan["towers"]]


@check("§4", "Con árboles equivalentes y empates el resultado es siempre el mismo (desempate determinista)")
def deterministic(api):
    Match(api, "escenario_complejo.json", plan=False)
    first = api.post("/defense/plan")[1]["plan"]
    second = api.post("/defense/plan")[1]["plan"]
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


@check("§4", "S(p) = C(p) / (1 + D_T(B,p)/D0): se elige la mayor puntuación positiva y se recalcula la cobertura")
def greedy_scores(api):
    Match(api, plan=False)
    plan = api.post("/defense/plan")[1]["plan"]
    assert [(t["vertex_id"], round(t["score"], 2)) for t in plan["towers"]] == [("V_C1", 53.57), ("V_C2", 23.53)]
    assert [s["new_corridors"] for s in plan["steps"]] == [["M_C1", "M_C2"], ["M_C3"]]


@check("§4", "Se detiene al alcanzar K o cuando nadie aporta cobertura; no es obligatorio usar exactamente K")
def stops(api):
    Match(api, plan=False)
    assert len(api.post("/defense/plan")[1]["plan"]["towers"]) == 2                       # K = 3 but only 2 add coverage
    Match(api, plan=False, edit=lambda r: r["metadata"].update(max_towers_K=1))
    assert len(api.post("/defense/plan")[1]["plan"]["towers"]) == 1


@check("§4", "Cada candidata tiene su radio de vigilancia Rv; un corredor está vigilado si su punto medio está a distancia <= Rv")
def surveillance(api):
    rejects(api, lambda r: r["candidates_meta"].pop(0), "falta el radio rv")
    Match(api, plan=False)
    plan = api.post("/defense/plan")[1]["plan"]
    assert plan["covered_corridors"] == ["M_C1", "M_C2", "M_C3"] and plan["coverage_pct"] == 100.0


@check("§4", "Se muestran el árbol, las torres, los corredores vigilados y la cobertura total (datos que entrega la API)")
def plan_exposes_everything(api):
    Match(api, plan=False)
    plan = api.post("/defense/plan")[1]["plan"]
    assert all(k in plan for k in ("mst", "towers", "covered_corridors", "coverage_pct", "steps", "unreachable"))


@check("§4/§10", "Las torres no se reubican una vez iniciado el enfrentamiento")
def plan_is_locked(api):
    m = Match(api)
    m.tick(1)
    status, body = api.post("/defense/plan")
    assert status == 409 and "no se pueden reubicar" in body["error"]
