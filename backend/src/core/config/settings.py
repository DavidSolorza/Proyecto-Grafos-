"""Application configuration settings."""
import os
from pathlib import Path


class Settings:
    """Core configuration for the backend application."""

    ROOT_PROJECT_DIR: Path = Path(__file__).resolve().parents[4]

    # No fixed scenario path: the user always picks the JSON from the UI (requirement §12)
    PORT: int = int(os.environ.get("PORT", 5000))
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    HOST: str = os.environ.get("HOST", "0.0.0.0")

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]


settings = Settings()
