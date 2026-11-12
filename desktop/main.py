"""Entry point of the Pygame client: `python desktop/main.py`.

If no backend is listening, it starts the Flask API inside this process. If the API is
already running (for example next to the React app), both clients share the same session.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame  # noqa: E402

from tardo_ui.api import DEFAULT_URL, ApiClient, ApiError, HttpTransport  # noqa: E402
from tardo_ui.app import App  # noqa: E402
from tardo_ui.launcher import ensure_backend  # noqa: E402
from tardo_ui.store import Store  # noqa: E402

FRONTEND = Path(__file__).resolve().parents[1] / "frontend"


def start_web():
    """Optional: also open the React app (needs `npm install` once)."""
    if not (FRONTEND / "node_modules").exists():
        print("React no está instalado: ejecuta `npm install` dentro de frontend/ para usar --web.")
        return None
    print("Abriendo React en http://localhost:5173 (misma sesión que Pygame)")
    return subprocess.Popen(["npm", "run", "dev"], cwd=FRONTEND, shell=os.name == "nt")


def main() -> int:
    parser = argparse.ArgumentParser(description="Cliente Pygame de La derrota del dictador General P. Tardo")
    parser.add_argument("--url", default=DEFAULT_URL, help="dirección de la API Flask (por defecto %(default)s)")
    parser.add_argument("--web", action="store_true", help="abre también el cliente React")
    args = parser.parse_args()
    try:
        server = ensure_backend(args.url)
    except ApiError as err:
        print(err)
        return 1
    print("API lista en", args.url, "(iniciada por Pygame)" if server else "(ya estaba corriendo)")
    web = start_web() if args.web else None
    pygame.init()
    pygame.display.set_caption("La derrota del dictador General P. Tardo")
    try:
        App(Store(ApiClient(HttpTransport(args.url)))).run()
    finally:
        pygame.quit()
        if server:
            server.shutdown()
        if web:
            web.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
