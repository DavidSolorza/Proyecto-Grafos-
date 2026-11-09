"""Scenario REST API endpoints including upload and graph details."""
from flask import Blueprint, jsonify, request
from src.core.config.settings import settings
from src.features.scenario.application.loader import ScenarioLoader

scenario_bp = Blueprint("scenario", __name__, url_prefix="/api/scenario")
_active_manager = None


def get_current_manager():
    """Retrieve or initialize the active ScenarioManager singleton."""
    global _active_manager
    if _active_manager is None:
        _active_manager = ScenarioLoader.load_from_file(
            settings.DEFAULT_SCENARIO_PATH
        )
    return _active_manager


@scenario_bp.route("/current", methods=["GET"])
def get_current_scenario():
    """Retrieve full active scenario data and initial state validation."""
    mgr = get_current_manager()
    validation = mgr.validate_initial_state()
    base = mgr.graph_e.get_base_vertex()

    return jsonify({
        "success": True,
        "validation": validation,
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
        },
    })


@scenario_bp.route("/upload", methods=["POST"])
def upload_scenario():
    """Load and activate a new scenario from JSON payload or file."""
    global _active_manager
    if request.is_json:
        data = request.get_json()
    elif "file" in request.files:
        import json
        file = request.files["file"]
        data = json.load(file.stream)
    else:
        return jsonify({"success": False, "error": "No JSON provided"}), 400

    new_mgr = ScenarioLoader.load_from_dict(data)
    validation = new_mgr.validate_initial_state()
    if not validation["has_base"]:
        return jsonify({"success": False, "error": "Scenario must have a BASE node"}), 400
    if not validation["labyrinth_path_exists"]:
        return jsonify({"success": False, "error": "No reachable path between ENTRY and EXIT"}), 400

    _active_manager = new_mgr
    return jsonify({
        "success": True,
        "message": f"Scenario '{new_mgr.metadata.title}' loaded successfully.",
        "validation": validation,
    })
