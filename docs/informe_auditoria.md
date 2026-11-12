# Informe de auditoría del enunciado

Generado con `python auditar_enunciado.py` el 2026-11-11. Cada punto se comprueba contra un servidor Flask real por HTTP, que es lo que usan los clientes Pygame y React.

**Resultado: 47 de 47 puntos correctos.**

| Sección | Punto del enunciado | Resultado |
|---|---|---|
| §12 | El usuario selecciona el JSON desde la interfaz; no hay rutas fijas (el servidor arranca vacío) | ✔ correcto |
| §12 | El JSON contiene ambos grafos, candidatas, base, entrada y salida, unidades, convoy y parámetros | ✔ correcto |
| §12 | Un archivo que no es JSON se rechaza con un mensaje claro y el escenario activo no cambia | ✔ correcto |
| §3 GE | Exactamente una base | ✔ correcto |
| §3 GE | Identificador único; coordenadas finitas positivas; tipo válido; aristas entre vértices existentes | ✔ correcto |
| §3 GE | Tiempos a pie y en moto positivos cuando se permite el medio; puentes con resistencia entera positiva | ✔ correcto |
| §3 GM | Entrada y salida diferentes; corredores con longitud y velocidad positivas | ✔ correcto |
| §3 GM | t(e) = l(e) / v(e) y se calcula el camino de menor costo inicial entre entrada y salida | ✔ correcto |
| §4 | MST sobre la componente de la base con el tiempo a pie; T_E incluye todos sus vértices (V-1 aristas) | ✔ correcto |
| §4 | Posiciones fuera de la componente de la base no pueden ser torres (V_ISLA) | ✔ correcto |
| §4 | Con árboles equivalentes y empates el resultado es siempre el mismo (desempate determinista) | ✔ correcto |
| §4 | S(p) = C(p) / (1 + D_T(B,p)/D0): se elige la mayor puntuación positiva y se recalcula la cobertura | ✔ correcto |
| §4 | Se detiene al alcanzar K o cuando nadie aporta cobertura; no es obligatorio usar exactamente K | ✔ correcto |
| §4 | Cada candidata tiene su radio de vigilancia Rv; un corredor está vigilado si su punto medio está a distancia <= Rv | ✔ correcto |
| §4 | Se muestran el árbol, las torres, los corredores vigilados y la cobertura total (datos que entrega la API) | ✔ correcto |
| §4/§10 | Las torres no se reubican una vez iniciado el enfrentamiento | ✔ correcto |
| §5 | Las torres admiten tres soldados como máximo, de cualquier especialidad (ocupantes + reservas) | ✔ correcto |
| §5 | Alcance efectivo Ref = Rbase * (1 + beta*z): francotirador (20) en V_C1 (z = 2, beta = 0.2) alcanza 28 | ✔ correcto |
| §5 | Tras llegar a una torre puede atacar en el siguiente instante de actualización, no en el mismo | ✔ correcto |
| §5 | Infantería y francotirador atacan a la máquina viva de menor resistencia (empate por identificación) | ✔ correcto |
| §5 | Frecuencia de ataque: el francotirador (0,5 ataques/s) dispara cada 2 s | ✔ correcto |
| §5 | El artillero aplica su daño a todas las máquinas vivas que alcance (área) | ✔ correcto |
| §5/§10 | Cada máquina destruida genera una única recompensa (tanque 150, camión 100, robot 50) | ✔ correcto |
| §6 | El JSON define las cantidades del convoy; cada máquina tiene identidad y resistencia propias (200/100/50 HP) | ✔ correcto |
| §6 | Peligro: D(q) = suma d*f de los soldados que alcanzan q; P(e) = media de 3 puntos * t(e); w(e) = t(e) + alfa*P(e) | ✔ correcto |
| §6 | Navegación reactiva: en cada intersección elige el primer corredor de la mejor ruta y explica las opciones | ✔ correcto |
| §6 | Sin defensas, el convoy tarda exactamente el tiempo del camino inicial de menor costo (23 s) | ✔ correcto |
| §7 | Cada soldado adquirido aparece en la base | ✔ correcto |
| §7 | A pie va un soldado por operación; en moto uno o dos | ✔ correcto |
| §7 | Antes de aceptar: origen y destino, ruta válida, soldados disponibles y capacidad; si falla, el estado no cambia | ✔ correcto |
| §7/§11 | Los soldados en tránsito no atacan | ✔ correcto |
| §8 | Cada moto que termina de cruzar un puente le resta 1 (aunque lleve 2); caminar no lo desgasta | ✔ correcto |
| §8 | Con resistencia 0 el puente se destruye y no participa en búsquedas; el soldado a pie queda detenido | ✔ correcto |
| §8 | Tras el tiempo de reconstrucción el puente recupera su resistencia máxima y los detenidos reanudan solos | ✔ correcto |
| §3/§8 | La reconstrucción ocupa a N personas: quedan ocupadas y no atacan ni reciben órdenes hasta terminar | ✔ correcto |
| §3/§8 | Una arista sin datos de puente es una calle (no se desgasta); un medio con tiempo null no puede usar la arista | ✔ correcto |
| §9 | Helicóptero: hasta 4 soldados; vuelo = distancia euclidiana / velocidad; reserva dinero y cupo al despegar | ✔ correcto |
| §9 | Al llegar baja lo que cabe; el excedente va a la torre más cercana con cupo; todo es una operación (un uso, un cobro) | ✔ correcto |
| §9 | Si no es posible ubicar a todos, regresan a la base; hay un máximo de usos configurable | ✔ correcto |
| §10 | Presupuesto disponible y reservado distintos; ninguna operación deja saldo negativo; traslados terrestres gratis | ✔ correcto |
| §11 | Reloj lógico en segundos, independiente de la frecuencia de dibujo (pasos de 0,25 s) | ✔ correcto |
| §11 | Fin: todas las máquinas destruidas = victoria por eliminación (14,25 s con 2 francotiradores) | ✔ correcto |
| §11 | Fin: una máquina viva llega a la salida = derrota | ✔ correcto |
| §11 | Fin: se llega al límite de tiempo sin llegada enemiga = victoria por resistencia | ✔ correcto |
| §11 | Al terminar se detienen las actualizaciones | ✔ correcto |
| §9 | Los excedentes se asignan a las otras torres en orden de distancia euclidiana desde el helicóptero (3 torres) | ✔ correcto |
| §11 | En coincidencias temporales se resuelven primero los ataques, luego la salida y por último el límite de tiempo | ✔ correcto |

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
