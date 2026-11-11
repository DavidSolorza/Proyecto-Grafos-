"""Global exception handlers for the Flask application."""
from flask import Flask, jsonify


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def register_error_handlers(app: Flask) -> None:
    """Register centralized error handlers on the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return (
            jsonify({"success": False, "error": error.message}),
            error.status_code,
        )

    @app.errorhandler(ValueError)
    @app.errorhandler(TypeError)
    def handle_bad_input(error):
        return jsonify({"success": False, "error": f"Datos inválidos: {error}"}), 400

    @app.errorhandler(404)
    def handle_not_found(_error):
        return (
            jsonify({"success": False, "error": "Resource not found"}),
            404,
        )

    @app.errorhandler(500)
    def handle_server_error(error):
        return (
            jsonify(
                {"success": False, "error": f"Internal server error: {error}"}
            ),
            500,
        )

