"""Starts the Flask API inside this process when nothing is listening, so one command opens the game."""
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse

from tardo_ui.api import ApiClient, ApiError, HttpTransport

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"


def backend_alive(url: str) -> bool:
    try:
        return ApiClient(HttpTransport(url, timeout=1.0)).health().get("status") == "healthy"
    except ApiError:
        return False


def ensure_backend(url: str):
    """Return None if the API already runs (for example with the React app); else start it in a thread."""
    if backend_alive(url):
        return None
    parsed = urlparse(url)
    if parsed.hostname not in ("127.0.0.1", "localhost"):
        raise ApiError(f"No hay backend en {url} y solo se puede iniciar uno local.")
    if str(BACKEND_DIR) not in sys.path:
        sys.path.insert(0, str(BACKEND_DIR))
    from werkzeug.serving import make_server
    from src.app import create_app

    server = make_server("127.0.0.1", parsed.port or 5000, create_app(), threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
