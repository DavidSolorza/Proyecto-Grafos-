"""Audits the statement point by point against a real server: `python auditar_enunciado.py`.

It starts the Flask API on a free port (so the session is empty, as in section 12), drives it over HTTP exactly
like the Pygame and React clients do, and prints one line per point of the statement.
Use `--informe ../docs/informe_auditoria.md` to write the results as a Markdown report.
"""
import argparse
import logging
import socket
import sys
import threading
import traceback
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from werkzeug.serving import make_server  # noqa: E402

from audit import c_scenario_plan, c_combat_convoy, c_bridges_air_time, c_extra  # noqa: E402,F401  (importing registers the checks, in this order)
from audit.core import CHECKS, Api  # noqa: E402
from src.app import create_app  # noqa: E402


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def run(api: Api) -> list[tuple]:
    results = []
    for section, point, fn in CHECKS:
        try:
            fn(api)
            results.append((section, point, True, ""))
        except AssertionError as err:
            results.append((section, point, False, str(err) or "assertion failed"))
        except Exception:                                  # a crash is also a failure, with its traceback
            results.append((section, point, False, traceback.format_exc(limit=2).strip().splitlines()[-1]))
    return results


def to_markdown(results: list[tuple]) -> str:
    passed = sum(1 for r in results if r[2])
    lines = [f"# Informe de auditoría del enunciado\n",
             f"Generado con `python auditar_enunciado.py` el {date.today().isoformat()}. Cada punto se comprueba contra un servidor "
             "Flask real por HTTP, que es lo que usan los clientes Pygame y React.\n",
             f"**Resultado: {passed} de {len(results)} puntos correctos.**\n",
             "| Sección | Punto del enunciado | Resultado |", "|---|---|---|"]
    lines += [f"| {s} | {p} | {'✔ correcto' if ok else '✘ ' + d} |" for s, p, ok, d in results]
    from audit.appendix import APPENDIX
    return "\n".join(lines) + "\n" + APPENDIX


def main() -> int:
    parser = argparse.ArgumentParser(description="Auditoría ejecutable del enunciado")
    parser.add_argument("--informe", help="archivo Markdown donde guardar el informe")
    args = parser.parse_args()
    logging.getLogger("werkzeug").setLevel(logging.ERROR)     # keep the report readable
    port = free_port()
    server = make_server("127.0.0.1", port, create_app(), threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        results = run(Api(f"http://127.0.0.1:{port}"))
    finally:
        server.shutdown()
    print("\nAUDITORÍA PUNTO A PUNTO DEL ENUNCIADO (servidor real por HTTP)\n" + "=" * 70)
    for section, point, ok, detail in results:
        print(f"{'✔' if ok else '✘'} {section:7} {point}" + ("" if ok else f"\n          -> {detail}"))
    passed = sum(1 for r in results if r[2])
    print("-" * 70 + f"\n{passed} de {len(results)} puntos correctos")
    if args.informe:
        Path(args.informe).write_text(to_markdown(results), encoding="utf-8")
        print("Informe guardado en", args.informe)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
