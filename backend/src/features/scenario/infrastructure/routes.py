"""Scenario REST API endpoints including upload and graph details."""
import json
from flask import Blueprint, jsonify, request
from src.core.errors.handlers import AppError
from src.features.scenario.application.loader import ScenarioLoader
from src.features.scenario.application.session import session

scenario_bp = Blueprint("scenario", __name__, url_prefix="/api/scenario")


@scenario_bp.route("/current", methods=["GET"])
def get_current_scenario():
    """Retrieve full active scenario data and initial state validation (null while none is loaded)."""
    if not session.has_scenario:
        return jsonify({"success": True, "loaded": False, "data": None, "validation": None})
    mgr = session.manager
    base = mgr.graph_e.get_base_vertex()
    return jsonify({
        "success": True,
        "loaded": True,
        "validation": mgr.validate_initial_state(),
        "data": {
            "metadata": mgr.metadata.__dict__,
            "graph_e": {
                "vertices": [v.__dict__ for v in mgr.graph_e.vertices.values()],
                "edges": [e.__dict__ for e in mgr.graph_e.edges.values()],
                "connected_component_base": list(
                    mgr.graph_e.get_connected_component(base.id) if base else []
                ),
            },
            "graph_m": {
                "vertices": [v.__dict__ for v in mgr.graph_m.vertices.values()],
                "corridors": [c.__dict__ for c in mgr.graph_m.corridors.values()],
            },
            "candidates_meta": mgr.candidates_meta,
            "convoy": mgr.convoy_config,
            "defenders_config": mgr.defenders_config,
            "helicopter": mgr.helicopter_config,
            "initial_route": mgr.initial_route,
        },
    })


@scenario_bp.route("/status", methods=["GET"])
def get_status():
    """Cheap fingerprint of the shared session so every client (Pygame, React) can tell when to refresh."""
    sim = session.simulation
    w = sim.world if sim else None
    return jsonify({
        "success": True,
        "loaded": session.has_scenario,
        "has_plan": session.plan is not None,
        "revision": dict(session.revision),
        "match": None if w is None else {
            "clock": round(w.clock, 2), "status": w.status.value, "events": w.event_seq,
            "soldiers": len(w.soldiers), "available": w.budget.available, "reserved": w.budget.reserved},
    })


@scenario_bp.route("/upload", methods=["POST"])
def upload_scenario():
    """Load and activate a new scenario from a JSON payload or an uploaded file."""
    try:
        if request.is_json:
            data = request.get_json()
        elif "file" in request.files:
            data = json.load(request.files["file"].stream)
        else:
            raise AppError("No se recibió ningún JSON")
        new_mgr = ScenarioLoader.load_from_dict(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise AppError("El archivo no es un JSON válido")
    except (KeyError, ValueError, TypeError) as exc:
        raise AppError(f"Escenario con formato incorrecto: {exc!r}")

    validation = new_mgr.validate_initial_state()
    if not validation["has_base"]:
        raise AppError("El escenario debe tener exactamente una BASE")
    if not validation["labyrinth_path_exists"]:
        raise AppError("No hay camino entre la ENTRADA y la SALIDA del laberinto")

    session.load(new_mgr)
    return jsonify({
        "success": True,
        "message": f"Escenario '{new_mgr.metadata.title}' cargado correctamente.",
        "validation": validation,
    })
