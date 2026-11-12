"""Static part of the audit report: section 13 (Pygame) and section 14 (deliverables)."""

APPENDIX = """
## Sección 13: la interfaz Pygame, viñeta por viñeta

Se comprueba con `desktop/tests/test_ui_s13_audit.py` (ventana fuera de pantalla, clics simulados, píxeles y textos dibujados):

| Viñeta del enunciado | Prueba | Resultado |
|---|---|---|
| Representar en 2D ambos grafos, base, candidatos, torres, soldados, convoy y puentes | `test_the_map_represents_both_graphs_base_candidates_towers_soldiers_convoy_and_bridges` | ✔ correcto |
| Cargar y validar escenarios | `test_load_and_validate_scenarios_with_the_reasons_shown` y `test_ui_filepicker.py` | ✔ correcto |
| Inspeccionar árbol mínimo y distribución propuesta | `test_inspect_the_minimum_tree_and_the_proposed_distribution` | ✔ correcto |
| Comprar soldados y ordenar transportes; consultar rutas y resultados algorítmicos | `test_buy_soldiers_order_transports_and_consult_routes_and_algorithmic_results` | ✔ correcto |
| Observar destrucción y habilitación de puentes | `test_observe_the_destruction_and_the_enabling_of_bridges` | ✔ correcto |
| Consultar indicadores y resultado final | `test_consult_indicators_and_the_final_result` | ✔ correcto |
| Explicar qué operación ocurrió y por qué | `test_the_interface_explains_what_happened_and_why` | ✔ correcto |
| Mostrar el camino inicial de menor costo y los corredores vigilados | `test_ui_spec_points.py` | ✔ correcto |

## Sección 14: entregables

| Entregable | Estado |
|---|---|
| Código fuente con instrucciones de instalación y ejecución | ✔ `README.md` y `docs/guia_ejecucion_y_verificacion.md` |
| Comentarios en inglés | ✔ revisado automáticamente (`python verificar.py`, "Comentarios y docstrings en inglés") |
| Repositorio Git con aportes verificables | ⚠ pendiente: hay cambios sin *commit*; cada integrante debe hacer los suyos |
| Manual de usuario | ✔ `docs/manual_usuario.md` |
| Manual técnico (dominio, grafos, responsabilidades, JSON, invariantes, decisiones, complejidad) | ✔ `docs/manual_tecnico.md` |
| Reporte de uso de inteligencia artificial | ✔ `docs/reporte_uso_ia.md` (los integrantes deben completar los campos marcados) |
| Distribución de tareas entre los dos integrantes | ✔ `docs/distribucion_tareas.md` |
| Dos escenarios JSON de distinta complejidad | ✔ cuatro escenarios en `docs/` |
| Uso de Pygame | ✔ `desktop/` (cliente de escritorio sobre la API Flask) |
| Videos (explicación en una segunda lengua y videotutorial) | ⚠ pendiente: los deben grabar los integrantes |

## Decisiones donde el enunciado deja libertad

| Tema | Decisión |
|---|---|
| Destinos de un traslado | Una torre del plan o la base (la capacidad se define para torres). |
| Helipuerto (`HELIPORT`) | Es un tipo de posición del grafo sin comportamiento propio: los vuelos salen de la base o de torres y llegan a torres. |
| Eventos temporales | Contadores por entidad (obra del puente, vuelo, traslado, enfriamiento del soldado) avanzados por el reloj de paso fijo de 0,25 s, en lugar de una cola de eventos; cuesta O(entidades) por paso. |
| Quién forma la cuadrilla de reconstrucción | Soldados que están en la base. |
| `max_uses` del helicóptero | Número total de vuelos permitidos. |
"""
