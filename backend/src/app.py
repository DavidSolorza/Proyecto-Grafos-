"""Flask application factory."""
from flask import Flask, jsonify
from flask_cors import CORS
from src.core.config.settings import settings
from src.core.errors.handlers import register_error_handlers
from src.features.scenario.infrastructure.routes import scenario_bp


def create_app() -> Flask:
    """Initialize and configure the Flask application."""
    app = Flask(__name__)

    # Enable CORS for frontend integration
    CORS(app, origins=settings.CORS_ORIGINS)

    # Register error handlers
    register_error_handlers(app)

    # Health check endpoint
    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "General P. Tardo Simulation API",
            "version": "1.0.0",
        })

    # Register feature blueprints
    app.register_blueprint(scenario_bp)

    return app

