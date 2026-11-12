# Manual técnico

**Proyecto 2 de Estructuras de Datos — "La derrota del dictador General P. Tardo"**

Este manual documenta cómo está construido el sistema: arquitectura, modelo de dominio, grafos, esquema del
JSON, invariantes, algoritmos, decisiones de diseño, análisis de complejidad y API. Responde a los entregables de la
sección 14 del enunciado. Notación: **V** = vértices, **E** = aristas de GE, **M** = corredores de GM,
**C** = candidatas a torre, **S** = soldados, **K** = máximo de torres.

Documentos relacionados: [manual de usuario](manual_usuario.md), [reporte de uso de IA](reporte_uso_ia.md),
[guía de ejecución y verificación](guia_ejecucion_y_verificacion.md), [guía de pruebas](guia_pruebas.md) y
[guía de exposición](guia_exposicion.md) y [distribución de tareas](distribucion_tareas.md).

---

## 1. Arquitectura

```
┌─────────────────────┐                  ┌────────────────────────────────────────────┐                  ┌──────────────────────────┐
│ Pygame (escritorio) │  HTTP/JSON /api  │ Backend (Flask)                            │  HTTP/JSON /api  │ Frontend (React + Vite)  │
│ interfaz del §13    │ ◄──────────────► │  infraestructura  → rutas REST             │ ◄──────────────► │  vistas · hooks · SVG    │
└─────────────────────┘                  │  aplicación       → algoritmos y casos     │                  └──────────────────────────┘
                                         │  dominio          → entidades y grafos     │
                                         └────────────────────────────────────────────┘
```

- **Tres piezas que se complementan.** Flask es la única fuente de verdad (estado y algoritmos); Pygame es la interfaz
  gráfica pedida por el enunciado y React es un cliente web equivalente que además sirve de panel de observación. Los dos
  clientes comparten la misma sesión (ver §12).
- **Separación exigida (§2).** Los grafos y algoritmos no importan Flask, Pygame ni React. Por eso las 232 pruebas del
  backend corren sin servidor ni ventana. Las interfaces son clientes que solo muestran el estado que entrega la API.
- **Capas por funcionalidad** (`backend/src/features/`): cada carpeta tiene `domain/` (entidades puras),
  `application/` (algoritmos y casos de uso) e `infrastructure/` (rutas Flask).

| Carpeta | Responsabilidad |
|---|---|
| `core/structures/` | `MinHeap`: cola de prioridad propia. |
| `core/errors/`, `core/config/` | Errores JSON uniformes (`AppError`) y configuración (puerto, CORS). |
| `features/elevated_graph/` | GE: grafo, Union-Find, Kruskal, selección de torres, Dijkstra a pie y en moto, plan. |
| `features/labyrinth/` | GM: grafo, peligro `D(q)`, `P(e)`, `w(e)` y navegación del convoy. |
| `features/scenario/` | Carga y validación del JSON, `ScenarioManager`, sesión en memoria. |
| `features/simulation/` | Reloj lógico, mundo, convoy, combate, puentes, transporte terrestre y aéreo, serialización. |
| `frontend/src/` | Cliente React: `features/` (intro, graphs, plan, simulation, map), `hooks/`, `components/`, `styles/`. |
| `desktop/tardo_ui/` | Cliente Pygame: cliente de la API, estado, widgets, mapa, pantallas y selector de archivos (ver §12). |

- **Sin librerías de grafos (§2).** Solo se usan estructuras de la biblioteca estándar de Python (`dict`, `list`,
  `set`, `deque`, `sorted`). La cola de prioridad y el Union-Find son propios. `python verificar.py` comprueba por
  código que ningún archivo del backend importe `networkx`, `igraph` ni `heapq`.
- **Estado.** Una única `Session` en memoria (un usuario): escenario activo, plan y simulación. Un escenario nuevo
  descarta el plan y la partida anteriores.

---

## 2. Modelo de dominio y responsabilidades

### 2.1 Entidades

| Entidad | Archivo | Responsabilidad | Datos principales |
|---|---|---|---|
| `VertexE` | `elevated_graph/domain/entities.py` | Posición del terreno en GE | `id`, `coords`, `type` (BASE, CANDIDATE, TRANSIT, HELIPORT), `z` |
| `EdgeE` | ídem | Camino o puente de GE | `u`, `v`, `time_walk`, `time_moto` (`None` = medio no permitido), `bridge_max_hp`/`bridge_current_hp` (`None` = calle), `is_destroyed`, `repair_timer`, `occupied_by_repair_units` |
| `GraphE` | `elevated_graph/domain/graph_e.py` | Almacena y actualiza GE | `vertices`, `edges`, `adj` |
| `VertexM`, `CorridorM` | `labyrinth/domain/entities.py` | Nodo y corredor de GM | `is_entry`, `is_exit`; `length`, `speed_allowed`, `current_danger`, `current_weight` |
| `GraphM` | `labyrinth/domain/graph_m.py` | Almacena y actualiza GM | `vertices`, `corridors`, `adj` |
| `ScenarioMetadata`, `ScenarioManager` | `scenario/domain/` | Parámetros y grafos del escenario cargado | `D0`, `alpha`, `beta`, `K`, presupuesto, tiempos, `raw` |
| `Tower` | `simulation/domain/world.py` | Torre elegida por el plan | `vertex_id`, `rv`, `z`, `xy` |
| `Soldier` | `simulation/domain/units.py` | Defensor comprado | `type`, `damage`, `base_range`, `frequency`, `status`, `vertex`, `xy`, `next_attack` |
| `Enemy` | ídem | Una máquina del convoy | `type`, `max_hp`, `hp`, `reward` |
| `Transfer` | ídem | Traslado terrestre de 1–2 soldados | `mode`, `dest`, `vertices`, `edges`, `index`, `status` |
| `Flight` | ídem | Operación de helicóptero | `aboard`, `target`, `reserved`, `visited`, `status` |
| `Budget` | `simulation/domain/world.py` | Dinero | `available`, `reserved`, `spent`, `earned` |
| `World` | ídem | Estado compartido de la partida | reloj, estado, soldados, enemigos, reservas, eventos, `version` |

### 2.2 Componentes que operan sobre el modelo

| Componente | Archivo | Responsabilidad |
|---|---|---|
| `Simulation` | `simulation/application/engine.py` | Reloj lógico: compra soldados y avanza un paso en el orden correcto. |
| `GroundTransport` | `.../ground.py` | Valida solicitudes, recalcula rutas, reanuda detenidos. |
| `AirTransport` | `.../air.py` | Autoriza vuelos, reserva cupo y dinero, reparte excedentes. |
| `BridgeManager` | `.../bridges.py` | Desgaste, colapso, cuadrilla de N personas y reconstrucción. |
| `CombatResolver` | `.../combat.py` | Ataques de los soldados en torres. |
| `Convoy` | `.../convoy.py` | Posición y ruta compartidas; decide en cada intersección. |
| `Session` | `scenario/application/session.py` | Escenario, plan y partida activos. |

### 2.3 Estados de un soldado

```
AT_BASE ──(orden)──► MOVING ──(llega a torre)──► STATIONED ──(orden)──► MOVING …
   │  ▲                 │  ▲
   │  └─(llega a base)──┘  └── WAITING (sin ruta; reanuda al cambiar la conectividad)
   ├──(orden helicóptero)──► FLYING ──(aterriza)──► STATIONED / AT_BASE
   └──(cuadrilla de un puente)──► REPAIRING ──(obra terminada)──► AT_BASE
```

Solo `STATIONED` ataca y solo `AT_BASE` y `STATIONED` reciben órdenes. Un soldado nunca está en dos estados a la vez.

---

## 3. Los dos grafos

### 3.1 Representación

Ambos grafos usan **listas de adyacencia** guardadas en diccionarios:

```
GraphE.vertices : dict[id → VertexE]      GraphM.vertices  : dict[id → VertexM]
GraphE.edges    : dict[id → EdgeE]        GraphM.corridors : dict[id → CorridorM]
GraphE.adj      : dict[id → list[EdgeE]]  GraphM.adj       : dict[id → list[CorridorM]]
```

La arista se guarda **una sola vez** y se referencia desde la lista de ambos extremos, así que modificarla
(destruir un puente, cambiar un peso) se ve de inmediato desde los dos lados. La arista conserva su identidad y sus
datos durante toda la partida, por eso un puente destruido puede reconstruirse.

| Operación | Costo | Justificación |
|---|---|---|
| Agregar vértice o arista | O(1) | Inserción en diccionario y lista. |
| Recorrer los vecinos de `v` | O(grado de v) | Es la lista `adj[v]`. |
| BFS de componente conexa | O(V + E) | Cada vértice y arista se visita una vez. |
| Modificar una arista | O(1) | Referencia compartida. |

Se eligió lista de adyacencia sobre matriz porque los grafos del problema son dispersos (E del orden de V): una
matriz costaría O(V²) de memoria y obligaría a recorrer V casillas para listar vecinos.

### 3.2 GE y GM son independientes

No existe ninguna arista entre un vértice de GE y uno de GM. Comparten solo el sistema de coordenadas del plano:
la única interacción es la distancia euclidiana entre una torre (GE) y el convoy o el punto medio de un corredor (GM).

### 3.3 Tiempos y disponibilidad

- GE: el tiempo de cruce depende del medio (`time_walk`, `time_moto`); si es `null`, ese medio no puede usar la arista.
- GM: `t(e) = length(e) / speed_allowed(e)`. Los corredores nunca se destruyen; solo cambia su costo por peligro.
- GE: una arista con `bridge_max_hp` es un puente con resistencia; sin ese campo es una calle que nunca se desgasta.

---

## 4. Esquema del JSON del escenario (§12)

El usuario elige el archivo desde la interfaz; no existe ninguna ruta fija. El backend valida **todo** antes de
construir los grafos (`validator.py`, `validator_params.py`) y devuelve todos los problemas con un mensaje claro.

```jsonc
{
  "metadata": {
    "title": "texto",                   // opcional
    "D0": 50.0,                         // > 0              (defecto 50)   tiempo de referencia de S(p)
    "alpha": 1.5,                       // >= 0             (defecto 1.5)  peligro → tiempo
    "beta": 0.2,                        // >= 0             (defecto 0.2)  efecto de la altura en el alcance
    "max_towers_K": 3,                  // entero >= 1      (defecto 3)
    "initial_budget": 2000,             // >= 0             (defecto 2000)
    "bridge_repair_time": 30.0,         // > 0              (defecto 30)   segundos de la obra
    "bridge_repair_crew": 0,            // entero >= 0      (defecto 0)    personas que ocupa la obra
    "time_limit": 300.0                 // > 0              (defecto 300)  victoria por resistencia
  },
  "graph_e": {
    "vertices": [
      { "id": "V_BASE", "coords": [10, 10], "type": "BASE", "z": 0 }
      // coords: dos números finitos > 0 · type: BASE | CANDIDATE | TRANSIT | HELIPORT · z >= 0
    ],
    "edges": [
      { "id": "E_E1", "u": "V_BASE", "v": "V_T1",
        "time_walk": 12.0,              // > 0, o null si no se permite caminar
        "time_moto": 5.0,               // > 0, o null si no se permiten motos (al menos uno no nulo)
        "bridge_max_hp": 10,            // opcional: entero > 0 → es un puente; sin él es una calle
        "bridge_current_hp": 10 }       // opcional: entero, 0 < actual <= máxima (defecto: la máxima)
    ]
  },
  "graph_m": {
    "vertices": [
      { "id": "M_ENTRADA", "coords": [0, 0], "is_entry": true, "is_exit": false }   // coords finitas
    ],
    "edges": [
      { "id": "M_C1", "u": "M_ENTRADA", "v": "M_N1", "length": 40.0, "speed_allowed": 5.0 }  // ambos > 0
    ]
  },
  "candidates_meta": [ { "vertex_id": "V_C1", "rv": 25.0 } ],   // una entrada por CADA candidata (obligatoria); rv > 0; sin repetidas
  "convoy": { "tanks": 1, "trucks": 1, "robot_soldiers": 2 },    // enteros >= 0, al menos una máquina
  "defenders_config": {                                          // los tres tipos son obligatorios
    "infantry": { "cost": 100, "damage": 10,  "base_range": 5.0,  "frequency": 1.0 },
    "sniper":   { "cost": 300, "damage": 50,  "base_range": 20.0, "frequency": 0.5 },
    "gunner":   { "cost": 500, "damage": 100, "base_range": 15.0, "frequency": 0.2 }
  },
  "helicopter": { "speed": 15.0, "cost": 200, "max_uses": 3 }    // opcional; estos son los defectos
}
```

Secciones obligatorias: `metadata`, `graph_e`, `graph_m`, `convoy`, `defenders_config`.

Validaciones que rechazan el archivo (con mensaje en español): id repetido; una cantidad distinta de una `BASE`;
coordenada no positiva en GE; tipo inválido; arista a un vértice inexistente o a sí misma; tiempo no positivo; arista sin
ningún medio; puente con resistencia no entera, cero o actual mayor que la máxima; GM sin exactamente una entrada y una
salida distintas; corredor con longitud o velocidad no positiva; `D0 ≤ 0`; `K` no entero o `< 1`; convoy vacío;
`rv` no positivo, de un vértice que no es candidato, repetido o **ausente en alguna candidata** (cada candidata debe tener su radio); soldado sin costo, daño, alcance o frecuencia positivos;
helicóptero con velocidad 0. Además, al subirlo se comprueba que exista camino entre la entrada y la salida de GM. Si algo
falla, el escenario activo **no cambia**.

Los parámetros del enunciado que son fijos están en el código: tabla de máquinas (`ENEMY_STATS`: tanque 200 HP/150,
camión 100 HP/100, robot 50 HP/50), capacidad de torre 3, capacidad del helicóptero 4, paso del reloj 0.25 s.

---

## 5. Invariantes

**Del escenario (se verifican al cargar)**

1. Exactamente una base. Ids únicos e inmutables dentro de cada grafo.
2. Coordenadas finitas; positivas en GE.
3. Las aristas unen vértices existentes y distintos. Toda arista permite al menos un medio.
4. Resistencia de puente entera y positiva, con `actual ≤ máxima`.
5. GM tiene una entrada y una salida distintas, y existe camino entre ellas.
6. Parámetros numéricos dentro de su rango (por ejemplo `D0 > 0`, `K ≥ 1`).

**De la simulación (las comprueban las pruebas automáticas)**

7. Tiempo monótono: el reloj solo avanza en múltiplos de 0.25 s; al terminar la partida se detienen las actualizaciones.
8. Por torre: `ocupantes + reservas ≤ 3`, también con vuelos simultáneos.
9. Presupuesto: `available`, `reserved`, `spent` y `earned` siempre coherentes; ninguna operación deja saldo negativo.
10. Una máquina eliminada no recibe más ataques y su recompensa se cobra una sola vez.
11. Un puente destruido no participa en búsquedas ni admite cruces nuevos (los ya iniciados terminan).
12. Un soldado nunca está en dos posiciones ni en dos operaciones a la vez; en tránsito no ataca.
13. Una solicitud rechazada **no modifica el estado** (se valida todo antes de cambiar nada).
14. Las torres no se construyen ni se reubican una vez iniciado el enfrentamiento.
15. Un cambio de conectividad (colapso o reconstrucción) incrementa `World.version`, y los soldados detenidos
    reintentan cuando esa versión cambia.
16. Prioridad ante coincidencias de tiempo: primero los ataques, luego máquinas vivas en la salida, luego el límite.

---

## 6. Algoritmos

### 6.1 Árbol de expansión mínima (`mst_service.py`, `disjoint_set.py`)

1. Se calcula con BFS la **componente de la base**, usando solo aristas habilitadas y transitables a pie.
2. Se ordenan esas aristas por `(time_walk, id)`: el desempate por id hace que, con árboles mínimos equivalentes,
   siempre salga el mismo.
3. **Kruskal** con **Union-Find** (unión por rango y compresión de caminos): se acepta una arista si une dos
   componentes distintas.
4. Se calcula `D_T(B, p)`: suma de tiempos desde la base siguiendo **solo** el árbol (BFS sobre sus aristas).

El árbol es una referencia de planificación: **no elimina** aristas de GE. Las posiciones fuera de la componente no
pueden elegirse como torres (se informan como inalcanzables).

### 6.2 Selección voraz de torres (`tower_selector.py`)

Para cada candidata `p` dentro de la componente: un corredor está vigilado si la distancia desde `p` al **punto medio**
del corredor es `≤ Rv(p)`. En cada iteración se calcula

```
S(p) = C(p) / (1 + D_T(B,p) / D0)        C(p) = longitud de corredores aún no cubiertos que vigila p
```

y se elige la mayor puntuación **positiva**. Empates: menor `D_T`, luego id lexicográfico. Se recalcula la cobertura
pendiente y se repite hasta alcanzar `K` o hasta que ninguna candidata aporte cobertura nueva (no es obligatorio usar
exactamente `K`). El resultado incluye cada iteración (`steps`) para poder explicar la decisión en la interfaz.

### 6.3 Dijkstra con montículo propio (`ge_paths.py`, `router.py`, `min_heap.py`)

`MinHeap` es un montículo binario guardado en una lista (padre de `i` en `(i−1)//2`): `push` sube el elemento
y `pop` baja la raíz, ambos en O(log n). Guarda tuplas `(costo, id)`, así que los empates se resuelven por id. Se usa
la técnica de entradas obsoletas (si al extraer `cost > best[v]`, se descarta). Dos usos:

- **GE (soldados):** costo = tiempo del medio elegido; se omiten puentes destruidos y aristas que no permiten ese medio.
- **GM (convoy):** costo = `w(e)`; se calcula **desde la salida** (el grafo no es dirigido).

### 6.3b Camino inicial de menor costo (`route_finder.py`)

Al cargar el escenario, además de comprobar que entrada y salida están conectadas (BFS), se calcula el camino de **menor costo** con
Dijkstra y el montículo propio, usando `t(e) = longitud / velocidad`. El resultado (`vertices`, `corredores`, `costo`) se guarda en
el escenario (`initial_route`), lo entrega `GET /scenario/current` y las interfaces lo dibujan. Con un convoy sin defensas, el peligro
es cero y el convoy tarda exactamente ese tiempo (cuantizado al paso de 0,25 s); una prueba lo verifica.

### 6.4 Peligro y navegación reactiva (`danger.py`, `router.py`, `convoy.py`)

Para cada corredor se evalúan tres puntos: inicio, medio y final. La tasa de daño en un punto `q` es

```
D(q) = Σ  d_s · f_s        para cada soldado s en torre cuyo alcance efectivo cubre q
P(e) = (D(inicio) + D(medio) + D(fin)) / 3 · t(e)        w(e) = t(e) + α · P(e)
```

El artillero cuenta una sola vez por soldado en esta estimación. En **cada intersección** el convoy recalcula
los pesos con los soldados que están en torres en ese instante, busca el mejor camino a la salida y recorre solo
el primer corredor; no cambia de dirección dentro de un corredor. Si la mejor ruta exige volver al vértice anterior,
se busca otra ruta de **primer paso diferente** y se usa la de menor costo; solo si no existe se permite retroceder.
Las rutas consideradas son caminos simples: el cálculo prohíbe pasar de nuevo por el vértice donde se decide, para que un
callejón sin salida no cuente como alternativa. Cada decisión se guarda con todas sus opciones para que la interfaz
explique por qué se eligió ese corredor.

### 6.5 Combate (`combat.py`)

Alcance efectivo `R_ef = R_base · (1 + β · z)` con la altura `z` de la torre. Cada soldado **en torre** ataca cuando
se cumple su enfriamiento (`1/frecuencia`); al llegar a una torre puede atacar desde la siguiente actualización
(no en el mismo instante). Infantería y francotirador atacan a la máquina viva en alcance de **menor resistencia actual**
(empate por id); el artillero daña a **todas** las máquinas vivas en alcance. La recompensa se suma solo cuando una
máquina pasa de viva a muerta, por eso es única.

### 6.6 Traslado terrestre (`ground.py`)

Antes de aceptar una orden se verifican, sin modificar nada: medio válido, soldados existentes y disponibles, mismo
origen, capacidad del medio (a pie 1; moto 1 o 2), destino válido (torre del plan o base), destino distinto, capacidad
libre de la torre (ocupantes + reservas) y existencia de ruta. Solo entonces se reserva cupo y se crea el traslado.

Cada paso avanza el tiempo sobre la arista actual. Si un puente se destruye antes de entrar al tramo, el soldado
recalcula desde su vértice actual; si no hay ruta queda `WAITING` y reintenta cuando `World.version` cambia.

### 6.7 Puentes y cuadrilla (`bridges.py`)

Cada moto que **termina** de cruzar un puente le resta 1 de resistencia, sin importar cuántos van. Caminar no desgasta.
Al llegar a 0 el puente se destruye: deja de participar en búsquedas, los cruces ya iniciados terminan y empieza
la obra. La obra requiere `bridge_repair_crew` (N) soldados **en la base**: pasan a `REPAIRING` y quedan ocupados.
Si hay menos de N libres, la obra espera y su reloj no corre. Pasado `bridge_repair_time`, el puente recupera su
resistencia máxima, la cuadrilla queda libre y la conectividad cambia (`version += 1`).

### 6.8 Helicóptero (`air.py`)

Autoriza solo si hay usos disponibles, presupuesto suficiente, soldados presentes en el mismo punto y un destino que
sea torre del plan. Reserva el dinero y el cupo del destino al despegar. La duración es
`distancia euclidiana / velocidad`. Al aterrizar baja tantos soldados como cupo reservó; los excedentes van a la torre
más cercana (distancia euclidiana desde el helicóptero, desempate por id) con cupo libre que no haya visitado; si no
hay, regresan a la base. Todos los tramos son **una sola operación**: un único uso y un único cobro, que pasa de
reservado a gastado al terminar.

### 6.9 Reloj lógico y fin de partida (`engine.py`)

El tiempo avanza en pasos de **0.25 s**, independientes de la velocidad de dibujo. Cada paso, en este orden:
puentes → vuelos → traslados terrestres → convoy → combate → comprobación de fin. La comprobación respeta la
prioridad del enunciado: ① todas las máquinas destruidas (victoria por eliminación), ② una máquina viva en la salida
(derrota), ③ se llegó al límite de tiempo (victoria por resistencia).

---

## 7. Decisiones de diseño

| Tema abierto del enunciado | Decisión | Por qué |
|---|---|---|
| Representación de los grafos | Listas de adyacencia en diccionarios | Grafos dispersos; recorrer vecinos en O(grado). |
| Cola de prioridad | Montículo binario propio | Evita `heapq`, O(log n), simple de explicar y probar. |
| Desempate de MST | Ordenar aristas por `(tiempo, id)` | Resultado determinista. |
| Torres: desempate | Mayor `S`, menor `D_T`, id | Lo dicta el enunciado; las puntuaciones se redondean a 9 decimales para evitar empates falsos. |
| Reloj | Paso fijo de 0.25 s | Simple, determinista, y los eventos caen en una cuadrícula conocida. |
| Tiempo de un corredor | `length / speed_allowed` del JSON | Es la fórmula del enunciado; no se usa la distancia entre coordenadas. |
| Medios no permitidos | `null` en el tiempo | Distingue "no se permite" de "tiempo inválido". |
| Puente o calle | Hay `bridge_max_hp` o no | Evita un campo extra y deja claro cuáles se desgastan. |
| Quién repara (N personas) | Soldados que están en la base, sin viaje | El enunciado no define N; la base es el único lugar donde no combaten. |
| `max_uses` del helicóptero | Total de vuelos permitidos | El enunciado habla de "helicópteros" con "número máximo de usos"; se modela un contador. |
| Dónde se detiene un soldado | Solo en base o torres | Son las únicas posiciones donde un soldado puede permanecer según el modelo. |
| Estado del servidor | En memoria, un usuario | Alcanza para la demostración; reiniciar limpia todo. |
| Helipuerto (`HELIPORT`) | Tipo de posición sin comportamiento propio; los vuelos salen de la base o de torres y llegan a torres | El enunciado define el aterrizaje y el reparto solo en torres. |
| Eventos temporales | Contadores por entidad avanzados por el reloj de pasos de 0,25 s | Evita una cola de eventos; cuesta O(entidades) por paso y es determinista. |
| Destino de un traslado | Una torre del plan o la base | La capacidad (ocupantes + reservas) está definida para torres. |
| Interfaz | Pygame como interfaz principal (el enunciado lo pide) + React como cliente web, ambos sobre una API Flask | Cumple §13 sin mezclar lógica con dibujo; React queda como panel web y de observación sobre la misma sesión. |

---

## 8. Análisis de complejidad

| Operación | Archivo | Complejidad | Notas |
|---|---|---|---|
| Cargar y validar el JSON | `validator*.py` | O(V + E + M) | Una pasada por vértice, arista y corredor. |
| BFS de componente | `graph_e.py` | O(V + E) | |
| Kruskal | `mst_service.py` | O(E log E) | Dominado por el ordenamiento; Union-Find ≈ O(α(V)) por operación. |
| `D_T` sobre el árbol | `mst_service.py` | O(V) | BFS sobre V−1 aristas. |
| Selección voraz | `tower_selector.py` | O(C·M + K·C·M) | Precálculo de puntos medios y vigilancia + K iteraciones sobre C candidatas, cada una suma ≤ M corredores. |
| Dijkstra (GE o GM) | `ge_paths.py`, `router.py` | O((V + E) log V) | Cada arista puede insertar a lo sumo una entrada en el montículo. |
| Peligro de los corredores | `danger.py` | O(M · S) | 3 puntos por corredor × S soldados en torre. |
| Decisión del convoy | `convoy.py`, `router.py` | O(M·S + (V + M) log V) | Una por intersección (≤ V decisiones por recorrido en un camino simple). |
| Orden de traslado | `ground.py` | O(S + Dijkstra) | Validar, buscar ruta una vez. |
| Replanificación de detenidos | `ground.py` | O(Dijkstra) por traslado | Solo cuando `World.version` cambia. |
| Combate por paso | `combat.py` | O(S · N) | N máquinas vivas. |
| Cuadrilla por paso | `bridges.py` | O(E + S log S) por obra pendiente | Ordenar a los libres de la base. |
| Un paso de simulación | `engine.py` | O(E + T + F + S·N + decisión) | T traslados, F vuelos. |
| Partida completa | | ≤ `time_limit / 0.25` = 1200 pasos | Con el límite por defecto de 300 s. |
| Memoria | | O(V + E + M + S) | Listas de adyacencia y estado de unidades. |

**Ejemplo numérico (escenario simple).** V = 5, E = 4, M = 3, C = 2, K = 3. Kruskal acepta las 4 aristas (peso 45 s).
Las candidatas valen `S(V_C1) = 75 / (1 + 20/50) = 53.57` y `S(V_C2) = 75 / (1 + 35/50) = 44.12` en la primera
iteración; gana `V_C1`, y en la segunda `V_C2` queda con `S = 23.53` porque ya solo aporta 40 de longitud nueva. Con
ambas, la cobertura es 100 % y el algoritmo se detiene antes de llegar a K = 3.

---

## 9. API REST

Prefijo `/api`. Toda respuesta es JSON; los errores tienen la forma `{"success": false, "error": "mensaje"}` con
estado 400 (datos inválidos) o 409 (operación no permitida ahora).

| Método y ruta | Cuerpo | Qué hace |
|---|---|---|
| `GET /health` | — | Estado del servicio. |
| `GET /scenario/current` | — | Escenario activo y validación; `loaded: false` y `data: null` si no hay ninguno. |
| `GET /scenario/status` | — | Huella barata de la sesión (revisiones y resumen de la partida) para que los clientes sepan cuándo releer. |
| `POST /scenario/upload` | archivo `file` (multipart) o JSON | Valida y activa un escenario nuevo. |
| `POST /defense/plan` | — | Kruskal + selección de torres. 409 si el combate ya inició o no hay escenario. |
| `GET /defense/plan` | — | Último plan (o `null`). |
| `POST /simulation/reset` | — | Crea una partida nueva con el plan actual (puentes reparados). 409 sin plan. |
| `GET /simulation/state` | — | Foto completa: reloj, presupuesto, convoy, soldados, torres, puentes, bitácora. |
| `POST /simulation/tick` | `{"dt": segundos}` | Avanza el reloj lógico. |
| `POST /units/recruit` | `{"type": "infantry\|sniper\|gunner", "count": 1}` | Compra soldados (aparecen en la base). |
| `POST /transport/move` | `{"soldier_ids": [], "dest": "V_C1", "mode": "walk\|moto"}` | Traslado terrestre. |
| `POST /transport/helicopter` | `{"soldier_ids": [], "dest": "V_C1"}` | Vuelo con reparto de excedentes. |
| `GET /transport/path?src=&dst=&mode=` | — | Consulta la ruta mínima y su tiempo (sin modificar nada). |

---

## 10. Pruebas y verificación

- 232 pruebas automáticas en `backend/tests/` (una por sección del enunciado) y 91 en `desktop/tests/` (cliente Pygame).
  El comando `python verificar.py` ejecuta ambas y además revisa reglas del proyecto (sin librerías de grafos ni
  `heapq`, archivos de menos de 150 líneas, escenarios válidos).
- **Verificación contra fuerza bruta:** el MST se compara con todos los conjuntos posibles de V−1 aristas; Dijkstra
  contra todas las rutas simples y contra Bellman-Ford en grafos aleatorios; el montículo contra `sorted`.
- **Pruebas de propiedades (fuzz):** `test_fuzz_invariants.py` juega 48 partidas aleatorias (4 escenarios, convoy normal y lento, 6 semillas)
  con órdenes válidas e inválidas y, después de cada operación, comprueba los invariantes: capacidad de torre (ocupantes + reservas ≤ 3),
  dinero conservado (`inicial + ganado = disponible + reservado + gastado`) y nunca negativo, una recompensa por máquina,
  ningún soldado en dos operaciones a la vez, estados coherentes, puentes consistentes, traslados terrestres gratis, órdenes rechazadas
  sin efectos y actualizaciones detenidas al terminar. Rompiendo 10 reglas a propósito, el fuzz detectó 9 y las pruebas específicas la décima.
- **Auditoría punto a punto:** `python auditar_enunciado.py` inicia el servidor Flask real, lo maneja por HTTP como lo hacen Pygame y React
  y verifica 47 puntos del enunciado, con su informe en [`informe_auditoria.md`](informe_auditoria.md).
- **Pruebas de mutación manuales:** se rompieron a propósito reglas del código (orden de fin de partida, desgaste al
  caminar, recompensa duplicada, cuadrilla, medios no permitidos…) y se comprobó que alguna prueba falla. Resultado
  final: todas las mutaciones probadas fueron detectadas.
- Recorrido por la interfaz con valores esperados: [`guia_ejecucion_y_verificacion.md`](guia_ejecucion_y_verificacion.md).

## 11. Limitaciones conocidas

- La interfaz Pygame se verificó con pruebas sin ventana real (renderizado fuera de pantalla, clics simulados y capturas
  revisadas); conviene probarla en una pantalla real antes de la sustentación. La tipografía usa Segoe UI en Windows y la
  mejor fuente disponible en otros sistemas.
- Los clientes se sincronizan por sondeo cada 1.5 s (no hay *push*): un cambio hecho en uno aparece en el otro con ese retraso.
- Un solo usuario y estado en memoria; no hay persistencia entre reinicios.
- La obra de un puente no requiere desplazar a la cuadrilla hasta el lugar.
- El paso de 0.25 s cuantiza los eventos (un soldado que llega en 8.00 s dispara en 8.25 s); un `dt` menor que 0.25 s
  avanza igualmente un paso completo.
- Un único contador de usos para los helicópteros.

---

## 12. Cliente de escritorio (Pygame)

### 12.1 Papel dentro del sistema

El enunciado (§13) pide una interfaz gráfica en **Pygame**. El proyecto tiene tres piezas que se complementan:

```
┌─────────────────────┐        ┌───────────────────────────┐        ┌─────────────────────┐
│ Pygame (escritorio) │  HTTP  │ Flask (API + algoritmos)  │  HTTP  │ React (web)         │
│ interfaz principal  │ ◄────► │ única fuente de verdad:   │ ◄────► │ interfaz web y      │
│ del enunciado       │        │ grafos, plan, partida     │        │ panel de observación│
└─────────────────────┘        └───────────────────────────┘        └─────────────────────┘
```

- **Flask** guarda todo el estado (escenario, plan, partida) y ejecuta todos los algoritmos. No dibuja nada.
- **Pygame** y **React** son dos *clientes* de la misma API REST: piden el estado, lo dibujan y envían órdenes.
  Ninguno contiene reglas del juego. Por eso los algoritmos se verifican **sin ejecutar Pygame** (§2 del enunciado).
- Como comparten la sesión, se pueden usar a la vez: se puede jugar en Pygame y proyectar la partida en el navegador, o
  al revés. Cada cliente detecta los cambios del otro (ver 12.6).

### 12.2 Módulos (`desktop/tardo_ui/`)

| Archivo | Responsabilidad |
|---|---|
| `api.py` | `ApiClient`: un método por endpoint; transporte HTTP con la biblioteca estándar; errores como `ApiError` con el mensaje del backend. |
| `launcher.py` | Si no hay API escuchando, inicia Flask dentro del proceso (en un hilo); si ya corre, la reutiliza. |
| `store.py`, `commands.py` | Estado de la interfaz y operaciones (cargar, planificar, comprar, enviar, ruta, reloj, sincronizar). **Sin Pygame**: se prueban solas. |
| `ui.py`, `theme.py` | Widgets de modo inmediato (botón, tarjeta, texto, barra, insignia), paleta beige/negro, tipografías y la escala fluida `ui_scale`. |
| `effects.py`, `header.py` | Degradados y sombras con caché; barra superior con logotipo y pestañas. |
| `filepicker.py` | Selector de archivos dentro de la ventana (requisito §12: sin rutas fijas). |
| `map/view.py` | Transformación mundo → pantalla: un solo encuadre para GE y GM, y selección del vértice bajo el ratón. |
| `map/layers.py`, `map/units.py`, `map/canvas.py` | Dibujo: corredores con calor de peligro, caminos y puentes, vértices, torres, radios `Rv`, soldados, convoy, helicópteros. |
| `screens/` | `home.py`, `graphs.py`, `plan.py`, `sim.py` (+ `sim_controls.py`, `sim_transport.py`, `sim_convoy.py`), `common.py`. |
| `app.py` | Ventana, pestañas, cuadro (frame) y avisos. |
| `main.py` | Punto de entrada: `python desktop/main.py [--url URL] [--web]`. |

### 12.3 Un cuadro (frame)

1. Se leen los eventos de Pygame (ratón, teclado, rueda, cierre, cambio de tamaño).
2. `Ui.begin` toma el clic del cuadro; `Store.tick_real` avanza la partida si está en marcha o sincroniza si no.
3. Se dibuja la pantalla activa. En el **modo inmediato** cada botón se dibuja y devuelve `True` si fue pulsado, así que
   la lógica está junto al dibujo y no hace falta un árbol de widgets.
4. Si hay un diálogo abierto (selector de archivos) se dibuja encima y los controles de atrás ignoran el clic.
5. Se muestra el aviso (verde si salió bien, rojo con el motivo si el backend rechazó la orden).
6. Si la escala no es 1.0, el lienzo lógico se estira a la ventana (ver §13.2).

Cada botón se registra en `ui.hits` por nombre, lo que permite probar la interfaz pulsando botones por su nombre.

### 12.4 Dos relojes distintos

- **Reloj lógico** (segundos de la simulación): vive en Flask y avanza en pasos de 0.25 s con `POST /simulation/tick`.
- **Reloj de la aplicación** (tiempo real): cada 250 ms Pygame pide un avance de `0.25 × velocidad` segundos lógicos.
  Los cuadros se dibujan a 60 por segundo, pero **la simulación no depende de la frecuencia de dibujo** (§11).

### 12.5 Selector de archivos y escenario (§12)

Pygame no contiene ninguna ruta de escenario. El botón **Seleccionar archivo...** abre un navegador de carpetas dentro
de la ventana (carpetas y archivos `.json`, atajos a *Inicio*, *Ejemplos del proyecto* y las unidades de disco). Al elegir
un archivo, Pygame lo lee y lo envía a `POST /scenario/upload`; **es el backend quien lo valida** y devuelve el motivo si
se rechaza. El diálogo recuerda la última carpeta usada.

### 12.6 Sincronización entre clientes

`GET /scenario/status` devuelve una huella barata de la sesión: contadores de revisión (`scenario`, `plan`, `match`) y un
resumen de la partida (reloj, estado, número total de eventos, soldados y dinero). Cada 1.5 s, y solo cuando no está
ejecutando su propia partida, cada cliente compara la huella con la última que vio y, **solo si cambió**, vuelve a leer
escenario, plan y partida. Tras un cambio propio recuerda la nueva huella para no releer sin necesidad. Costo: una petición
pequeña por intervalo.

### 12.7 Qué pide la sección 13 y dónde está

| Requisito de §13 | En Pygame |
|---|---|
| Representar en 2D ambos grafos, base, candidatos, torres, soldados, convoy y puentes | Mapa (`map/`) en *Los grafos*, *Plan* y *Simulación* |
| Cargar y validar escenarios | *Inicio*: selector de archivos y tres insignias de validación; el motivo del rechazo aparece en un aviso |
| Inspeccionar árbol mínimo y distribución propuesta | *Plan*: árbol `T_E` (verde), radios `Rv`, corredores vigilados, tabla de torres, paso a paso de la selección voraz |
| Comprar soldados y ordenar transportes | *Simulación*: botones de compra; soldados, destino y medio (a pie, moto, helicóptero) |
| Consultar rutas y resultados algorítmicos | **Ver ruta**, tabla "¿Por qué ese camino?", pestaña **Corredores** (`t`, `P`, `w`), puntuaciones `S(p)` |
| Observar destrucción y habilitación de puentes | Etiquetas de los puentes (`n/n`, `X 30s`, `X sin cuadrilla`) y bitácora |
| Consultar indicadores y resultado final | Reloj, presupuesto, vida de las máquinas y cartel de resultado (**Jugar de nuevo** / **Ver mapa**) |
| Explicar qué operación ocurrió y por qué | Bitácora ("qué ocurrió y por qué") y avisos con el motivo de cada rechazo |

### 12.8 Decisiones

| Decisión | Por qué |
|---|---|
| Pygame es un cliente de la API, no importa el backend | Mantiene la separación lógica / algoritmos / interfaz y permite que Pygame y React compartan una sola partida. |
| El arranque inicia Flask si hace falta | Un solo comando abre el juego completo; si ya corre (por ejemplo junto a React), se reutiliza. |
| Interfaz de modo inmediato | Pocas líneas, la lógica junto al dibujo y fácil de probar por nombre de botón. |
| `store.py` y `commands.py` sin Pygame | El comportamiento se prueba sin ventana. |
| Selector de archivos propio | No depende de otra biblioteca gráfica y cumple "sin rutas fijas" dentro de la misma ventana. |
| Sondeo (polling) cada 1.5 s y no *push* | Sencillo y suficiente; no hay que mantener conexiones abiertas. |

### 12.9 Pruebas del cliente

91 pruebas en `desktop/tests/` que corren **sin ventana real** (controlador de vídeo `dummy` de SDL): se simulan clics,
teclas y rueda del ratón; se pulsan los botones por nombre; se comprueban píxeles del mapa (árbol verde, radios, puente caído en
rojo); se juegan partidas completas (victoria a los 14.25 s, derrota a los 23.0 s, victoria por resistencia) y se prueba el
arranque real con un servidor HTTP. Se rompieron a propósito 19 reglas del código del cliente y las 19 fueron detectadas.

---

## 13. Diseño visual y comportamiento responsive

Las dos interfaces comparten la paleta (beige "papel", negro "tinta" y tres acentos apagados: ocre = torres, terracota = enemigo,
salvia = defensores) y se adaptan a cualquier tamaño de pantalla con el mismo principio de **`clamp(mínimo, preferido, máximo)`**: un valor
que sigue al tamaño de la ventana, pero nunca baja de un mínimo legible ni sube de un máximo cómodo.

### 13.1 Web (React): tokens fluidos en `frontend/src/styles/`

| Archivo | Contenido |
|---|---|
| `base.css` | Tokens (paleta, escala tipográfica, espaciados, radios, sombras, área táctil), reinicio, rejillas y utilidades. |
| `nav.css` | Barra superior pegajosa con efecto de vidrio, logotipo y pestañas en píldora. |
| `ui.css` | Tarjetas, botones, insignias, alertas y controles de formulario. |
| `data.css` | Fichas de datos, tablas, barras, bloque didáctico y fórmulas. |
| `map.css`, `intro.css`, `sim.css` | Mapa SVG, pantalla de inicio y paneles de la simulación. |

- **Tipografía fluida:** ocho tamaños (`--fs-2xs` a `--fs-hero`) definidos con `clamp()`, por ejemplo `--fs-base: clamp(0.92rem, 0.86rem + 0.28vw, 1.06rem)`:
  el texto del cuerpo crece de unos 14.7 px en un teléfono de 320 px a unos 17 px en un monitor de 1920 px.
- **Espaciado fluido:** `--sp-1` a `--sp-6` y `--pad-x` con `clamp()`: los márgenes y huecos respiran más en pantallas grandes.
- **Radios, sombras y área táctil:** `--radius`, `--radius-sm` y `--tap` (40 a 48 px) también son fluidos. En pantallas táctiles
  (`@media (pointer: coarse)`) todos los controles miden al menos 44 px.
- **Rejillas fluidas:** `repeat(auto-fit, minmax(min(100%, clamp(...)), 1fr))` en pasos, conceptos y fichas: el número de columnas se ajusta solo.
  La disposición mapa + panel lateral aparece desde 62 rem; por debajo, todo se apila.
- **Mapa:** el SVG usa `viewBox`, así que sus etiquetas y figuras escalan con el contenedor; su altura máxima es `min(72vh, 46rem)`.
  En pantallas anchas el mapa queda fijo (`position: sticky`) mientras se recorren los paneles.
- **Teléfonos:** la barra superior se compacta (sin subtítulo y con el estado reducido a un punto) para no ocupar la pantalla.
- **Movimiento:** hay animaciones suaves de entrada y de pulso del convoy, y se desactivan con `prefers-reduced-motion`.
- **Sin estilos en línea de tamaño:** las clases utilitarias (`.note`, `.fine`, `.mt-*`, `.start`...) reemplazan los `style={{ fontSize }}`.

Comprobaciones: `python verificar.py` incluye "Web fluida" (cuenta los usos de `clamp()` y falla si aparece un `font-size` fijo en px o rem o un
`fontSize` en línea). Además se midió en el navegador, de 320 a 1920 px y en las cuatro pestañas, que no hay desborde horizontal.

### 13.2 Pygame: escala fluida de toda la ventana

La ventana de Pygame se puede redimensionar libremente (mínimo 840 × 560). La interfaz se dibuja en un **lienzo lógico** cuyo tamaño es el de la
ventana dividido por una escala `ui_scale(ancho, alto) = clamp(0.7, min(ancho/1360, alto/820), 1.8)` (`theme.py`):

- Cerca del tamaño de diseño (1360 × 820) la escala es exactamente 1.0 y se dibuja sin remuestrear, para que el texto quede nítido.
- En ventanas grandes todo crece hasta 1.8 veces y en ventanas pequeñas se reduce hasta 0.7; el diseño siempre llena la ventana completa.
- Los clics llegan en píxeles de la ventana y `App` los convierte al lienzo lógico; las pantallas no conocen la escala.

Pulido visual (`effects.py`, `header.py`, `ui.py`, `map/`): degradados y sombras suaves cacheados, cabecera con logotipo y pestañas en píldora, mapa con
rejilla de puntos y resplandor cálido, halo sobre las torres elegidas y un anillo que se expande alrededor del convoy.

Pruebas: `desktop/tests/test_ui_fluid.py` (16 pruebas) comprueba el recorte de la escala, su crecimiento sin saltos, que cada pantalla llene la ventana
en cinco tamaños, la conversión de clics, la reconstrucción del lienzo solo cuando cambia el tamaño y los efectos visuales.
