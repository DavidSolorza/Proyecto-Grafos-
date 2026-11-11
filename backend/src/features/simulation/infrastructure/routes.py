"""Simulation, units and transport endpoints."""
from flask import Blueprint, jsonify, request
from src.core.errors.handlers import AppError
from src.features.elevated_graph.application.ge_paths import shortest_path
from src.features.scenario.application.session import session
from src.features.simulation.application.serializer import simulation_to_dict

sim_bp = Blueprint("simulation", __name__, url_prefix="/api")


def _state():
    return jsonify({"success": True, "state": simulation_to_dict(session.require_simulation())})


@sim_bp.route("/simulation/state", methods=["GET"])
def get_state():
    return _state()


@sim_bp.route("/simulation/reset", methods=["POST"])
def reset():
    """Start a new match from the current plan."""
    session.new_simulation()
    return _state()


@sim_bp.route("/simulation/tick", methods=["POST"])
def tick():
    """Advance the logical clock by dt seconds."""
    dt = float((request.get_json(silent=True) or {}).get("dt", 1.0))
    if not 0 < dt <= 30:
        raise AppError("dt debe estar entre 0 y 30 segundos")
    session.require_simulation().tick(dt)
    return _state()


@sim_bp.route("/units/recruit", methods=["POST"])
def recruit():
    body = request.get_json(silent=True) or {}
    session.require_simulation().recruit(str(body.get("type", "")), int(body.get("count", 1)))
    return _state()


@sim_bp.route("/transport/move", methods=["POST"])
def move():
    """Ground transfer: walking (1 soldier) or motorcycle (1-2 soldiers)."""
    b = request.get_json(silent=True) or {}
    session.require_simulation().ground.request(b.get("soldier_ids", []), b.get("dest", ""), b.get("mode", "walk"))
    return _state()


@sim_bp.route("/transport/helicopter", methods=["POST"])
def helicopter():
    b = request.get_json(silent=True) or {}
    session.require_simulation().air.request(b.get("soldier_ids", []), b.get("dest", ""))
    return _state()


@sim_bp.route("/transport/path", methods=["GET"])
def query_path():
    """Ask for the best route between two GE vertices without moving anyone."""
    sim = session.require_simulation()
    src, dst, mode = (request.args.get(k, "") for k in ("src", "dst", "mode"))
    route = shortest_path(sim.world.manager.graph_e, src, dst, "moto" if mode == "moto" else "walk")
    if route is None:
        return jsonify({"success": True, "path": None})
    return jsonify({"success": True, "path": {"time": route[0], "vertices": route[1]}})
