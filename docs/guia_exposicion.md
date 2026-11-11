# Guía de exposición

Pensada para explicar el proyecto en 10–15 minutos y para responder preguntas en la sustentación.
V = vértices, E = aristas.

## 1. Idea en una frase

Dos grafos independientes comparten el plano: el convoy camina por **GM** y los soldados defienden desde **GE**.
Solo se relacionan por distancia (alcance de disparo).

## 2. Estructuras de datos

| Qué | Dónde | Por qué esa estructura |
|---|---|---|
| Grafo con **lista de adyacencia** (`vertices` y `adj` como diccionarios) | `graph_e.py`, `graph_m.py` | Los grafos son dispersos; recorrer vecinos cuesta O(grado) y agregar es O(1). |
| **Union-Find** (rango + compresión de caminos) | `disjoint_set.py` | Kruskal necesita saber en casi O(1) si dos vértices ya están conectados. |
| **Cola** (`deque`) | BFS de la componente conexa y distancias en el árbol | Recorrido por capas. |
| **Cola de prioridad** (montículo binario propio, `min_heap.py`) | Dijkstra en GE y en GM | Extraer el vértice de menor costo en O(log V): árbol completo guardado en una lista, el padre de `i` es `(i-1)//2`, `push` sube y `pop` baja. |
| **Diccionario de reservas** | `World.reserved` | Controla ocupantes + reservas ≤ 3 por torre, también con vuelos simultáneos. |
| **Lista de eventos** | `World.events` | La interfaz explica qué pasó y por qué. |

## 3. Algoritmos y complejidad

| Algoritmo | Archivo | Complejidad |
|---|---|---|
| BFS de la componente de la base | `graph_e.py` | O(V + E) |
| Kruskal (ordenar + Union-Find) | `mst_service.py` | O(E log E) |
| Distancia D_T sobre el árbol | `mst_service.py` | O(V) |
| Selección voraz de K torres | `tower_selector.py` | O(K · C · M), C candidatas y M corredores |
| Dijkstra de soldados (tiempo a pie o moto) | `ge_paths.py` | O((V + E) log V) |
| Peligro w(e) = t(e) + α·P(e) | `danger.py` | O(M · S), S soldados en torres |
| Navegación reactiva del convoy | `router.py` | O((V + E) log V) por intersección |
| Paso de simulación | `engine.py` | O(soldados + enemigos + transportes) |

## 4. Reglas del enunciado y dónde viven

- **Desempates del MST**: aristas con igual tiempo se ordenan por id (`mst_service.py`).
- **Desempates de torres**: mayor S(p), luego menor D_T, luego id (`tower_selector.py`).
- **Sin retroceso inútil**: si la mejor ruta vuelve al vértice anterior, se busca otra con primer paso distinto (`router.py`).
- **Puente**: solo la moto lo desgasta (−1 por cruce, sin importar 1 o 2 ocupantes); al llegar a 0 se destruye y se
  reconstruye tras `bridge_repair_time` (`bridges.py`). Una arista sin `bridge_max_hp` es una calle: no se desgasta.
  La reconstrucción **ocupa a N personas** (`bridge_repair_crew`): N soldados que estén en la base quedan en estado
  `REPAIRING` (no atacan ni reciben órdenes) y el reloj de la obra solo corre mientras haya cuadrilla completa.
- **Soldados detenidos**: reintentan cuando cambia la conectividad (`World.version`, `ground.py`).
- **Helicóptero**: reserva cupo, descarga lo que cabe y reparte el excedente a la torre más cercana con cupo; si no
  hay, regresa a la base (`air.py`).
- **Prioridad en el mismo instante**: ataques → máquinas en la salida → límite de tiempo (`engine.py`).
- **Una recompensa por máquina**: se cobra solo al pasar de vivo a muerto (`combat.py`).

## 5. Guion de demo (5 minutos)

1. **Inicio**: mostrar el escenario cargado y los invariantes verificados. Subir `escenario_complejo.json`.
2. **Los grafos**: alternar GE / GM y hacer clic en vértices.
3. **Plan de defensa** (escenario complejo): calcular; activar/desactivar árbol y radios; abrir "Paso a paso" y explicar
   por qué ganó `V_C4` en la iteración 1. Señalar que `V_ISLA` queda fuera de la componente.
4. **Simulación**: comprar 2 francotiradores y 1 infantería; enviar uno en moto y otro a pie (comparar tiempos con
   "Ver ruta"); iniciar a 2×. Mostrar la tabla "¿Por qué ese camino?" cuando el convoy elige entre corredores,
   y los puentes cambiando de `n/n` a `✕` al colapsar.
5. Probar el helicóptero con 4 soldados hacia una torre y ver cómo reparte el excedente.

## 6. Preguntas probables

- *¿Por qué el MST no elimina las demás aristas?* Es solo una referencia de planificación (distancias D_T); los soldados siguen usando todo el grafo.
- *¿Qué pasa si hay dos MST posibles?* El orden por (tiempo, id) hace que siempre salga el mismo.
- *¿Cómo evitas que dos vuelos llenen la misma torre?* Cada vuelo reserva cupo al despegar y lo libera al aterrizar.
- *¿Por qué Dijkstra y no BFS?* Las aristas tienen pesos distintos.
- *¿Y si un peso w(e) cambia?* Se recalcula en cada intersección con los soldados que están en torres en ese momento.

## 7. Simplificaciones declaradas

- La cuadrilla de reconstrucción sale de los soldados que estén **en la base** (no de las torres) y no viaja hasta el
  puente: la obra solo ocupa tiempo y personas. Con `bridge_repair_crew = 0` (valor por defecto) no necesita gente.
- Un tiempo `null` en `time_walk` o `time_moto` significa que ese medio no puede usar la arista. El árbol de Kruskal
  es "a pie": las posiciones que solo se alcanzan por aristas solo-moto quedan fuera del árbol y no pueden ser torres.
- `max_uses` del helicóptero es el total de vuelos permitidos; no se modelan varios aparatos.
- Un soldado solo se detiene en la base o en una torre (no en vértices de tránsito); si se queda sin ruta, queda
  "detenido" donde esté y reanuda al cambiar la conectividad.
- La ruta del convoy usa la velocidad permitida de cada corredor y la longitud `length` del JSON (no la distancia
  euclidiana de las coordenadas).
- El estado vive en memoria de un solo usuario: reiniciar el servidor borra el plan y la partida.
