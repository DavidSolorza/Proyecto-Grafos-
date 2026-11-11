"""Defense planning endpoints (MST + towers)."""
from flask import Blueprint, jsonify
from src.features.scenario.application.session import session

defense_bp = Blueprint("defense", __name__, url_prefix="/api/defense")


@defense_bp.route("/plan", methods=["POST"])
def create_plan():
    """Run Kruskal and the greedy tower selection."""
    return jsonify({"success": True, "plan": session.calculate_plan()})


@defense_bp.route("/plan", methods=["GET"])
def get_plan():
    """Return the last calculated plan (null if there is none yet)."""
    return jsonify({"success": True, "plan": session.plan})
