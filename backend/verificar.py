"""One command to check the whole project against the statement: `python verificar.py`.

Runs the automated tests grouped by statement section and a few static rules
(no graph libraries, no heapq, files under 150 lines, valid example scenarios).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# (statement section, what it demands, test files that prove it)
SECTIONS = [
    ("§2", "Estructuras propias: cola de prioridad y Union-Find", ["test_min_heap.py", "test_algorithms.py"]),
    ("§3", "Grafos GE y GM: reglas, medios permitidos, puentes y calles", ["test_s3_graphs.py", "test_edge_rules.py"]),
    ("§3/§12", "Validación del escenario antes de usarlo", ["test_validation.py"]),
    ("§4", "MST (Kruskal) y selección voraz de torres", ["test_s4_planning.py"]),
    ("§5", "Soldados, alcance efectivo y combate", ["test_s5_combat.py"]),
    ("§6", "Convoy, peligro y navegación reactiva", ["test_s6_convoy.py"]),
    ("§7/§8", "Traslado terrestre, puentes y cuadrilla de reconstrucción", ["test_s7_ground.py", "test_repair_crew.py"]),
    ("§9/§10", "Helicóptero, excedentes y presupuesto", ["test_s9_air_budget.py"]),
    ("§11", "Reloj lógico y condiciones de fin", ["test_s11_end.py"]),
    ("§12", "Arranque vacío y carga de JSON desde la interfaz", ["test_s12_api.py"]),
]


def run_tests(files: list[str]) -> tuple[bool, str]:
    cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"]
    out = subprocess.run(cmd + [f"tests/{f}" for f in files], cwd=ROOT, capture_output=True, text=True)
    last = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else "sin salida"
    return out.returncode == 0, last


def source_files() -> list[Path]:
    exts = {".py", ".js", ".jsx", ".css"}
    skip = {"node_modules", "dist", "__pycache__"}
    dirs = [ROOT / "src", ROOT / "tests", ROOT.parent / "frontend" / "src"]
    return [p for d in dirs for p in d.rglob("*") if p.suffix in exts and not skip & set(p.parts)]


def static_checks() -> list[tuple[bool, str]]:
    files = source_files()
    backend = [p for p in files if p.suffix == ".py" and "src" in p.parts]
    banned = re.compile(r"^\s*(import|from)\s+(networkx|igraph|graph_tool|scipy\.sparse\.csgraph|heapq)\b", re.M)
    users = [p.name for p in backend if banned.search(p.read_text(encoding="utf-8"))]
    long_files = [f"{p.name} ({len(p.read_text(encoding='utf-8').splitlines())})" for p in files
                  if len(p.read_text(encoding="utf-8").splitlines()) >= 150]
    from src.features.scenario.application.loader import ScenarioLoader
    bad = []
    for scenario in sorted((ROOT.parent / "docs").glob("escenario_*.json")):
        try:
            ok = all(ScenarioLoader.load_from_file(scenario).validate_initial_state().values())
        except Exception as exc:  # any failure means the example is broken
            ok = False
            print(f"    {scenario.name}: {exc}")
        if not ok:
            bad.append(scenario.name)
    n_scenarios = len(list((ROOT.parent / "docs").glob("escenario_*.json")))
    return [
        (not users, "Sin librerías de grafos ni heapq" + (f" (usan: {users})" if users else "")),
        (not long_files, "Todos los archivos tienen menos de 150 líneas" + (f" (largos: {long_files})" if long_files else "")),
        (not bad and n_scenarios >= 2, f"{n_scenarios} escenarios de ejemplo válidos" + (f" (fallan: {bad})" if bad else "")),
    ]


def main() -> int:
    failures = 0
    print("\nVERIFICACIÓN DEL PROYECTO CONTRA EL ENUNCIADO\n" + "=" * 60)
    for section, text, files in SECTIONS:
        ok, summary = run_tests(files)
        failures += not ok
        print(f"{'✔' if ok else '✘'} {section:7} {text}\n          {summary}")
    print("-" * 60)
    for ok, text in static_checks():
        failures += not ok
        print(f"{'✔' if ok else '✘'} {text}")
    total_ok, total = run_tests([])
    print("-" * 60 + f"\nSuite completa: {total}")
    print("RESULTADO: TODO CORRECTO" if not failures and total_ok else f"RESULTADO: {failures} problema(s)")
    return 0 if not failures and total_ok else 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
