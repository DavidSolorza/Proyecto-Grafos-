# Guía de pruebas paso a paso

Sirve para comprobar tú mismo cada punto del enunciado (`docs/grafos project.pdf`) y para mostrarlo en la
sustentación. Está en tres capas: **automática** (códigos), **manual** (interfaz) y **"rómpelo tú"** (ver que el
sistema se defiende).

Escenarios que se usan (todos en `docs/`):

| Archivo | Para qué |
|---|---|
| `escenario_general_p_tardo.json` | Simple y lineal. La app arranca vacía: tú lo subes desde **Inicio**. |
| `escenario_complejo.json` | Ciclos, empates, un vértice aislado (`V_ISLA`), rutas alternativas. |
| `escenario_puentes.json` | Puentes frágiles (`E_E1` = 3 usos, `E_E2` = 1 uso) y convoy lento. Para puentes y soldados detenidos. |
| `escenario_cuadrilla.json` | Como el anterior, pero la reconstrucción ocupa a **2 personas**, `E_E3` es una calle (sin puente) y `E_E4` solo admite moto. |

---

## 0. Preparación

Necesitas Python 3.10+ y Node 18+. Abre **dos terminales** en la carpeta del proyecto.

Terminal 1 (backend):

```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```

Terminal 2 (frontend):

```bash
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. Arriba a la derecha debe decir **Backend conectado** (punto verde). Si dice "sin
conexión", el backend no está corriendo en el puerto 5000.

---

## 1. Pruebas automáticas (2 minutos)

No necesitan servidor ni navegador (así lo pide el enunciado: los algoritmos se verifican sin interfaz).

```bash
cd backend
python -m pytest tests -v
```

Resultado esperado: **170 passed**. (Si `pytest` no está instalado: `python -m pip install -r requirements-dev.txt`.) Cada archivo cubre una sección del PDF:

| Archivo | Sección | Qué comprueba |
|---|---|---|
| `test_validation.py` | §3, §12 | 33 escenarios inválidos son rechazados con mensaje claro; los 2 válidos pasan. |
| `test_s3_graphs.py` | §3 | Aristas no dirigidas, una sola base, puente destruido conserva datos, `t(e)=l/v`, camino mínimo = fuerza bruta. |
| `test_s4_planning.py` | §4 | MST de peso mínimo (contra fuerza bruta), distancia sobre el árbol, desempates, `K`, radio `Rv` incluido en el borde. |
| `test_s5_combat.py` | §5 | `Ref = Rbase·(1+β·z)`, blanco de menor vida, artillero de área, frecuencia, sin ataque al llegar, una sola recompensa. |
| `test_s6_convoy.py` | §6 | Composición del convoy, `D(q)`, `w(e)=t(e)+α·P(e)`, no retroceder si hay alternativa, no cambia a mitad de corredor. |
| `test_edge_rules.py` | §3 | Medios no permitidos (`null`), calles vs puentes, Kruskal solo a pie, validaciones nuevas. |
| `test_repair_crew.py` | §3, §8 | La reconstrucción ocupa a N personas: espera sin cuadrilla, estados, liberación, no sale de torres. |
| `test_s7_ground.py` | §7, §8 | Validaciones sin tocar el estado, tiempos a pie/moto, desgaste solo en moto, colapso, reconstrucción, recálculo y reanudación. |
| `test_s9_air_budget.py` | §9, §10 | Capacidad 4, duración = distancia/velocidad, reparto de excedentes, retorno a base, presupuesto nunca negativo. |
| `test_s11_end.py` | §11 | Victoria/derrota, prioridad en empates (ataques → salida → tiempo), el reloj se detiene. |
| `test_s12_api.py` | §12 | Carga del JSON desde la API, errores 400/409 limpios, flujo completo. |
| `test_min_heap.py` | §3, §13 | Montículo propio: orden, desempates, vacío, operaciones mezcladas; Dijkstra de GE y GM = Bellman-Ford en grafos aleatorios; el código no importa `heapq`. |
| `test_algorithms.py` | varias | Pruebas de humo del arranque. |

Para ver solo una sección: `python -m pytest tests/test_s5_combat.py -v`.

---

## 2. Pruebas manuales en la interfaz

Todas empiezan igual: reinicia el backend (Ctrl+C y `python run.py`) para partir limpio y, como la app arranca
vacía, sube el escenario que indique cada prueba desde **Inicio** (o usa **Reiniciar** dentro de la simulación).

### 2.1 Cargar y validar escenarios (§12, §13)

1. Pestaña **01 Inicio** recién arrancada: dice **"Sin escenario cargado"**. Las pestañas Grafos, Plan y Simulación
   muestran "Aún no hay un escenario cargado" con un botón para volver a Inicio (arranque vacío, §12).
2. En **Cargar escenario** pulsa **Seleccionar archivo** y elige `docs/escenario_general_p_tardo.json`. Aparece el
   resumen con tres insignias verdes: *Exactamente una base*, *La base tiene componente conexa*,
   *Existe camino entrada → salida*.
   Luego sube `docs/escenario_complejo.json` para ver que lo reemplaza.
   - Esperado: mensaje verde "Escenario 'Escenario complejo: la tenaza del laberinto' cargado correctamente" y el
     título de la tarjeta cambia.
3. Crea un archivo `malo.json` con el texto `esto no es json` y súbelo.
   - Esperado: mensaje rojo **"El archivo no es un JSON válido"**. El escenario activo **no cambia**.

### 2.2 Los dos grafos (§3, §13)

1. Pestaña **02 Los grafos**. Alterna **Ambas capas / Red elevada GE / Laberinto GM**.
2. Haz clic en cualquier vértice: abajo aparecen id, tipo, altura `z` y coordenadas.
3. Forma de los símbolos: cuadrado = base, rombo = candidata, círculo con **H** = helipuerto, punto = tránsito;
   en GM, ▶ entrada (verde) y ⚑ salida (roja).
4. Abre "¿Qué es la componente conexa de la base?": con el escenario complejo dice **8 de 9 vértices alcanzables**
   (falta `V_ISLA`).

### 2.3 Plan de defensa: MST y torres (§4, §13)

**Escenario simple** (`escenario_general_p_tardo.json`):

1. Pestaña **03 Plan de defensa** → **Calcular plan**.
2. Esperado: **2 torres, 100 % de cobertura, peso del MST 45 s, 4 aristas**. Torres `V_C1` (S = 53.57, D_T = 20) y
   `V_C2` (S = 23.53, D_T = 35).
3. Abre "Paso a paso de la selección voraz". Iteración 1: `V_C1` C = 75, S = 53.57 y `V_C2` C = 75, S = 44.12; gana
   `V_C1`. Iteración 2: solo queda `M_C3` sin vigilar, `V_C2` aporta C = 40.
4. Activa/desactiva **Árbol T_E** (verde) y **Radios Rv** (círculos punteados).
5. Verifica a mano: `S(V_C1) = 75 / (1 + 20/50) = 53.57`.

**Escenario complejo** (súbelo antes, ver 2.1):

1. Calcula el plan. Esperado: **7 aristas en el árbol, peso 85 s**, torres `V_C4` (S = 73.8) y luego `V_C3`
   (S = 16.3), **cobertura 72.2 %**.
2. Aparece el aviso **"Fuera de la componente de la base: V_ISLA"** (nunca puede ser torre, aunque tenga radio 40).
3. Observa que **no hay obligación de usar las 3 torres (K)**: se detiene al no haber cobertura nueva.
4. En el mapa, la arista `E03` (BASE–C4) **no es verde**: el árbol no la usa, pero sigue existiendo (los soldados
   pueden caminar por ella).

### 2.4 Compra y presupuesto (§10)

1. Pestaña **04 Simulación** (si pide, **Crear simulación**). Presupuesto: **$2000 disponible, $0 reservado**.
2. Pulsa **Infantería** → baja a $1900 y aparece el chip `S1 INF · en base V_BASE` (los soldados aparecen en la base).
3. Compra hasta agotar: 4 **Artillero** = $2000. Con $0 los botones se desactivan; nunca queda saldo negativo.

### 2.5 Transporte terrestre (§7)

Con soldados comprados (escenario simple):

1. Selecciona dos chips y elige Medio **A pie** → **Enviar**. Esperado: error rojo
   **"A pie va 1 soldado; en moto pueden ir 1 o 2"** y *nada cambia*.
2. Selecciona `S1`, Destino `V_C1`, Medio **A pie** → **Ver ruta**:
   `V_BASE → V_T1 → V_C1 (20s)`. Con **Moto**: `(8s)`.
3. Prueba destino que no es torre (no aparece en la lista: solo torres y base) y una torre llena: llena `V_C1`
   con 3 soldados y manda un cuarto → error "no tiene capacidad libre (ocupantes + reservas)".
4. Envía a `S1` a pie y pulsa **+1 s** 20 veces: en el instante 20 el chip pasa a `en torre V_C1`. Con moto, en 8.
5. Mientras un soldado está "en camino" sus ataques no cuentan (ver 2.6).

### 2.6 Combate (§5)

Escenario simple. Compra **1 Francotirador** (S1), destino `V_C1`, **Moto**, **Enviar**. Pulsa **+1 s** 8 veces.

Esperado en la **Bitácora**:

```
 8.00  S1 llegaron a V_C1.
 8.25  S1 (SNIPER) golpea a ROBOT_SOLDIER-1: -50 HP → 0. ¡Destruido! +$50.
10.25  S1 (SNIPER) golpea a ROBOT_SOLDIER-2: -50 HP → 0. ¡Destruido! +$50.
12.25  S1 (SNIPER) golpea a TRUCK-1: -50 HP → 50.
14.25  S1 (SNIPER) golpea a TRUCK-1: -50 HP → 0. ¡Destruido! +$100.
```

Qué verificar:

- **No ataca al llegar**: llega en 8.00 y dispara en 8.25 (siguiente actualización).
- **Frecuencia**: 0.5 ataques/s = un disparo cada 2 s (8.25, 10.25, 12.25…).
- **Menor vida primero** (robots de 50) y **empate por id** (`ROBOT_SOLDIER-1` antes que `-2`).
- **Una recompensa por máquina**: el presupuesto sube $50, $50, $100 una sola vez.
- **Alcance** `Ref = 20·(1 + 0.2·2) = 28` (torre `V_C1`, z = 2).

Artillero: compra 1 artillero y ponlo en `V_C2` (z = 5, alcance 15·2 = 30): cuando varias máquinas están en rango, la
bitácora muestra **varios golpes seguidos en el mismo instante** (daño de área).

### 2.7 Peligro y ruta del convoy (§6)

1. Con el francotirador anterior en `V_C1`, mira el panel **Convoy enemigo**:
   - Tabla **¿Por qué ese camino?**: en cada intersección lista las opciones con su costo `w + resto`.
   - Tabla de corredores, tras llegar el soldado: `M_C1  t = 8.0  P = 133.3  w = 208.0`.
2. Verifica a mano: puntos (0,0), (15,7.5), (30,15); el francotirador está en (30,20) con alcance 28 y tasa
   `50 × 0.5 = 25`. Distancias 36.1 (fuera), 19.5 (dentro), 5 (dentro) → promedio `(0+25+25)/3 = 16.67`;
   `P = 16.67 × 8 = 133.3`; `w = 8 + 1.5 × 133.3 = 208`. ✔
3. En el **mapa**, los corredores se tiñen de arena a terracota según el peligro.
4. **Escenario complejo** (hay ramas alternativas): compra francotiradores y colócalos solo cerca de una rama; en la
   tabla "¿Por qué ese camino?" verás que el convoy elige la otra rama aunque sea más larga.

### 2.8 Puentes dinámicos (§8) — escenario de puentes

Sube `escenario_puentes.json`, calcula el plan, ve a Simulación y:

1. Compra **3 Infanterías**.
2. `S1`: Destino `V_C1`, **A pie**, **Enviar**. Luego `S2` y `S3`: Destino `V_C1`, **Moto**, **Enviar**.
3. Velocidad **5×** y **Iniciar**. Mira las etiquetas de los puentes en el mapa:

| Tiempo | Qué debe pasar |
|---|---|
| 0–5 s | `E_E1` muestra **3/3**. |
| 5 s | La moto terminó de cruzar `E_E1`: **2/3** (desgaste 1, aunque van 2 pasajeros). |
| 8 s | La moto cruza `E_E2` (1 uso): se destruye, etiqueta **✕ 30 s** con cuenta regresiva. `S2` y `S3` llegan a la torre. |
| ≈12 s | `S1` (a pie, no desgastó nada) llega a `V_T1` y **queda "detenido"**: no hay ruta. |
| 38 s | `E_E2` se **reconstruye** y vuelve a **1/1**. |
| ≈46 s | `S1` reanuda solo y **llega a `V_C1`**. |

Esto prueba: solo la moto desgasta, un cruce = −1, colapso, no se inicia un cruce nuevo, reconstrucción en el tiempo
configurado, soldado detenido que reanuda al cambiar la conectividad. Ver el registro en la **Bitácora** (eventos
`bridge` en amarillo).

Con el escenario complejo hay rutas alternativas: usa motos hacia `V_C3` y `V_C4` hasta que algún puente se
destruya; el soldado en camino **recalcula** y llega por otro lado en vez de detenerse.

### 2.8b Reconstrucción que ocupa a N personas (§3, §8) — escenario de cuadrilla

Sube `escenario_cuadrilla.json` (en **Inicio** el resumen dice *Personas por reparación: 2*), calcula el plan
(MST **35 s**, 3 aristas; `V_H1` aparece como inalcanzable a pie porque `E_E4` solo admite moto) y ve a Simulación.

1. Compra **3 Infanterías** (`S1`, `S2`, `S3`). `S1`: Destino `V_C1`, **Moto**, **Enviar**. Pulsa **+1 s** unas 40 veces.
2. Bitácora esperada:

```
 8.00  El puente E_E2 (V_T1-V_C1) colapsó. Reconstrucción: 30s con 2 persona(s) de la base.
 8.00  S1 llegaron a V_C1.
 8.25  S2, S3 empiezan a reconstruir E_E2 y quedan ocupados.
38.00  El puente E_E2 fue reconstruido y vuelve a estar habilitado.
```

3. Entre 8.25 y 38 s los chips de `S2` y `S3` dicen **reconstruyendo**: sus casillas están desactivadas (no reciben
   órdenes). Al terminar vuelven a **en base**.
4. En el mapa solo `E_E1` y `E_E2` muestran vida (`E_E3` y `E_E4` son calles, sin etiqueta).
5. **Sin cuadrilla**: pulsa **Reiniciar**, compra solo **1 Infantería** y envíala igual. A los 8.25 s la bitácora dice
   "La reconstrucción de E_E2 espera: necesita 2 persona(s) en la base y hay 0", la etiqueta del puente dice
   **✕ sin cuadrilla** y el reloj de la obra **no avanza** (el puente sigue caído aunque pasen 60 s).

### 2.9 Helicóptero (§9) — escenario simple

1. Compra 4 Infanterías. Selecciona `S1..S4`, Destino `V_C1`, Medio **Helicóptero** → **Enviar**.
2. Esperado inmediatamente: Presupuesto **$1400 disponible, $200 reservado** (compra $400 + vuelo $200 reservado);
   los chips dicen **volando**; en el mapa aparece el icono ✚; la insignia dice `helicópteros: 2 · $200`.
3. Pulsa **+1 s** unas 3 veces. Bitácora esperada:

```
0.0  Helicóptero H1 despega de V_BASE hacia V_C1 con 4 soldado(s). Costo reservado: $200.
1.5  H1 aterrizó en V_C1: bajan 3, quedan 1 a bordo.          (22.4 de distancia / 15 de velocidad)
1.5  H1 lleva 1 excedente(s) hacia V_C2.
3.0  H1 aterrizó en V_C2: bajan 1, quedan 0 a bordo.
```

4. Al aterrizar el último: **reservado $0**, y los $200 pasan a gastado. **V_C1 = 3/3**, **V_C2 = 1/3**.
5. Pruebas de rechazo: más de 4 soldados, presupuesto menor a $200, o gastar los 3 usos → mensaje rojo y nada cambia.
6. Retorno a base: compra 7 Infanterías y haz tres vuelos: `S1–S4` → `V_C1`; luego `S5, S6` → `V_C2`
   (quedan ambas torres en 3/3); por último `S7` → `V_C1`. Esperado en la bitácora:
   `H3 aterrizó en V_C1: bajan 0, quedan 1 a bordo`, `H3 lleva 1 excedente(s) hacia V_BASE` y `S7` queda **en base**.
   Los 3 vuelos gastan los 3 usos ($600): disponible final **$700**, reservado **$0** (la vuelta a la base no cobra
   un vuelo extra).

### 2.10 Fin de la partida (§11)

| Resultado | Cómo provocarlo (escenario simple) | Esperado |
|---|---|---|
| **Derrota** | No compres nada, **Iniciar**. | A los **23.0 s**, "Derrota: una máquina viva llegó a la salida". |
| **Victoria por eliminación** | 2 Francotiradores → `V_C1` en moto, **Iniciar**. | A los **14.25 s**, ganas; presupuesto final **$1750** (2000 − 600 + 350). |
| **Victoria por resistencia** | Sube `escenario_puentes.json` con `"time_limit": 30` en `metadata` y no compres nada. | A los **30.0 s** ("Se resistió 30 s"). |

Tras el final: el reloj se detiene, aparece el cartel con **Jugar de nuevo** y **Ver mapa** (para mirar el estado
final). **Reiniciar** vuelve a empezar con puentes reparados.

Con solo 3 Infanterías (2 en moto a `V_C1`, 1 a pie a `V_C2`; daño 10 y alcance corto) pierdes igualmente a los
23.0 s: sirve para mostrar que una defensa débil no basta.

### 2.11 Torres no se reubican (§4, §10)

1. Inicia la simulación (cualquier ▶ o +1 s).
2. Vuelve a **03 Plan de defensa** y pulsa **Recalcular plan**.
3. Esperado: error rojo **"El enfrentamiento ya inició: las torres no se pueden reubicar"**. El plan mostrado no cambia.

### 2.12 Interfaz responsive (§13)

1. En el navegador abre las herramientas (F12) → modo dispositivo → ancho **375 px**.
2. Esperado: sin barra de desplazamiento horizontal, las pestañas se deslizan, los paneles pasan debajo del mapa y
   los controles quedan antes de la bitácora.

---

## 3. "Rómpelo tú": el sistema se defiende

Copia `docs/escenario_general_p_tardo.json` a otro nombre, haz **un** cambio y súbelo en **Inicio**. Debe aparecer
un mensaje rojo y el escenario activo no debe cambiar.

| Cambio en el JSON | Mensaje esperado (contiene) |
|---|---|
| Un segundo vértice con `"type": "BASE"` | `GE: debe haber exactamente una BASE` |
| `"coords": [-5, 10]` en un vértice de GE | `las coordenadas deben ser dos números finitos positivos` |
| Dos vértices con el mismo `id` | `el id '...' está repetido` |
| `"time_walk": 0` en una arista | `time_walk debe ser positivo` |
| `"bridge_max_hp": 0` y `"bridge_current_hp": 0` | `la resistencia del puente debe ser entera, positiva` |
| `"v": "NOPE"` en una arista | `une vértices que no existen` |
| `"is_entry": true` en la salida | `debe haber exactamente una entrada y una salida` |
| `"speed_allowed": 0` en un corredor | `speed_allowed debe ser positivo` |
| `"D0": 0` | `metadata.D0 debe ser mayor que 0` |
| `"max_towers_K": 0` | `max_towers_K debe ser un entero positivo` |
| `"time_walk": null` **y** `"time_moto": null` en la misma arista | `debe permitir al menos un medio` |
| `"bridge_repair_crew": -1` en `metadata` | `bridge_repair_crew debe ser un entero >= 0` |
| Convoy con todo en 0 | `convoy: debe tener al menos una máquina` |
| Borrar el último corredor de GM | `No hay camino entre la ENTRADA y la SALIDA del laberinto` |

---

## 4. Comprobar que las pruebas sí detectan errores (opcional, buena para exponer)

Una prueba que nunca falla no demuestra nada. Prueba esto:

1. Abre `backend/src/features/elevated_graph/application/tower_selector.py` y cambia `<= rv_by_vertex` por
   `< rv_by_vertex` (el borde del radio deja de contar).
2. Corre `python -m pytest tests -q`. Debe fallar `test_corridor_is_watched_when_midpoint_distance_equals_rv`.
3. Devuélvelo y vuelve a pasar todo.

Otras reglas que puedes romper de la misma forma (cada una hace fallar al menos una prueba):

| Archivo | Cambio | Debe fallar |
|---|---|---|
| `engine.py` | Revisar la llegada a la salida antes que la eliminación | `test_same_instant_attacks_are_resolved_before_the_exit_check` |
| `ground.py` | Que `wear` se llame también al caminar (quitar el `if t.mode == "moto"`) | `test_walking_never_wears_bridges...` |
| `combat.py` | `targets = in_range[:1]` para el artillero | `test_gunner_damages_every_living_enemy...` |
| `world.py` | Quitar `- self.reserved.get(...)` en `free_slots` | `test_full_tower_counts_present_soldiers...` |
| `router.py` | Cambiar `if best["to"] == previous:` por `if False:` | `test_backtrack_is_replaced...` |

---

## 5. Matriz del enunciado → dónde se verifica

| Requisito del PDF | Automática | Manual |
|---|---|---|
| §3 Grafos GE y GM con estructuras propias | `test_s3_graphs.py` | 2.2 |
| §3 Validar entrada/salida y camino inicial | `test_validation.py` | 2.1, 3 |
| §4 MST sobre la componente de la base, desempates | `test_s4_planning.py` | 2.3 |
| §4 Selección voraz `S(p)`, `K`, radio `Rv` | `test_s4_planning.py` | 2.3 |
| §5 Unidades, `Ref`, blancos, artillero | `test_s5_combat.py` | 2.6 |
| §6 Convoy, peligro `P(e)`, `w(e)`, navegación reactiva | `test_s6_convoy.py` | 2.7 |
| §7 Terrestre, validaciones sin efectos, detenidos | `test_s7_ground.py` | 2.5, 2.8 |
| §8 Puentes: desgaste, colapso, reconstrucción | `test_s7_ground.py` | 2.8 |
| §3/§8 La reconstrucción ocupa a N personas; medios no permitidos; calles | `test_repair_crew.py`, `test_edge_rules.py` | 2.8b |
| §9 Helicópteros, excedentes, reservas | `test_s9_air_budget.py` | 2.9 |
| §10 Presupuesto disponible/reservado, sin saldo negativo | `test_s9_air_budget.py` | 2.4, 2.9 |
| §11 Reloj, prioridades, condiciones de fin | `test_s11_end.py` | 2.10 |
| §12 JSON elegido desde la interfaz | `test_s12_api.py` | 2.1 |
| §13 Interfaz: cargar, MST, comprar, transportar, rutas, puentes, resultado | — | 2.1 a 2.12 |

## 6. Límites que debes conocer

- El enunciado menciona **Pygame**; este proyecto usa **React + Flask** (decisión del equipo desde la propuesta
  inicial). Confírmalo con el docente.
- La cola de prioridad de Dijkstra es un **montículo binario propio** (`backend/src/core/structures/min_heap.py`);
  no se usa `heapq`. Una prueba revisa que ningún archivo de `backend/src` lo importe.
- La aplicación **arranca vacía**: no hay ninguna ruta de escenario fija; el JSON se elige siempre desde la interfaz.
  Kruskal sí usa `sorted` de Python para ordenar aristas (ordenar no calcula el árbol).
- La cuadrilla de reconstrucción sale de los soldados que están **en la base** y la obra no requiere viaje. `max_uses`
  del helicóptero es el total de vuelos. Ver `docs/guia_exposicion.md`, sección 7.
- El tiempo avanza en pasos de 0.25 s: los eventos se alinean a esa cuadrícula (por ejemplo, el ataque ocurre en
  8.25 s y no en 8.00 s).
