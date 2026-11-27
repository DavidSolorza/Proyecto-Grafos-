# DOCUMENTACIÓN TÉCNICA Y OPERATIVA POR FASES
## "La Derrota del Dictador General P. Tardo"
**Universidad de Caldas — Facultad de Inteligencia Artificial e Ingenierías**  
**Estructuras de Datos — Proyecto 2 (100% Conformidad con la Guía Oficial)**

---

## 📑 ÍNDICE GENERAL POR FASES

1. **[Fase 1: Representación de Estructuras de Datos Propias](#fase-1-representación-de-estructuras-de-datos-propias)**
2. **[Fase 2: Modelado Geométrico y Topológico de los Dos Grafos ($G_E$ y $G_M$)](#fase-2-modelado-geométrico-y-topológico-de-los-dos-grafos-g_e-y-g_m)**
3. **[Fase 3: Planificación de Defensas (Kruskal MST y Selección Voraz de Torres)](#fase-3-planificación-de-defensas-kruskal-mst-y-selección-voraz-de-torres)**
4. **[Fase 4: Unidades Defensivas, Fórmulas Balísticas y Reglas de Combate](#fase-4-unidades-defensivas-fórmulas-balísticas-y-reglas-de-combate)**
5. **[Fase 5: Dinámica del Convoy Enemigo, Estimación de Peligro y Navegación Reactiva](#fase-5-dinámica-del-convoy-enemigo-estimación-de-peligro-y-navegación-reactiva)**
6. **[Fase 6: Desplazamientos Terrestres, Desgaste de Puentes y Cuadrilla de Reparación](#fase-6-desplazamientos-terrestres-desgaste-de-puentes-y-cuadrilla-de-reparación)**
7. **[Fase 7: Transporte Aéreo (Helicópteros) y Algoritmo de Distribución de Excedentes](#fase-7-transporte-aéreo-helicópteros-y-algoritmo-de-distribución-de-excedentes)**
8. **[Fase 8: Gestión Presupuestal, Reloj Lógico en Segundos y Condiciones de Fin](#fase-8-gestión-presupuestal-reloj-lógico-en-segundos-y-condiciones-de-fin)**
9. **[Fase 9: Interfaz Gráfica Dual (Pygame Nativo Vectorial + React Web)](#fase-9-interfaz-gráfica-dual-pygame-nativo-vectorial--react-web)**
10. **[Fase 10: Auditoría, Suite del Profesor y Verificación al 100%](#fase-10-auditoría-suite-del-profesor-y-verificación-al-100)**

---

## FASE 1: REPRESENTACIÓN DE ESTRUCTURAS DE DATOS PROPIAS

### 1.1 Prohibición de Librerías Externas
El enunciado prohíbe explícitamente delegar la lógica a `NetworkX`, `igraph`, `graph-tool` o usar `heapq` de la biblioteca estándar para el cálculo algorítmico central.

### 1.2 Estructuras Implementadas
- **Cola de Prioridad Propia (`MinHeap`):**
  - Implementada en `src/features/planning/domain/entities/min_heap.py`.
  - Árbol binario balanceado en arreglo lineal indexado en 0.
  - Operaciones con análisis asintótico:
    - `insert(item, priority)`: $\mathcal{O}(\log V)$ con percolación hacia arriba (`sift_up`).
    - `extract_min()`: $\mathcal{O}(\log V)$ con percolación hacia abajo (`sift_down`).
    - `peek()`: $\mathcal{O}(1)$.
    - Desempate estricto: menor prioridad numérica, seguido de menor tiempo a pie y orden lexicográfico inmutable.
- **Estructura Union-Find (Disjoint-Set):**
  - Utilizada para el algoritmo de Kruskal en `src/features/elevated_graph/domain/union_find.py`.
  - Optimizaciones:
    - **Compresión de caminos (Path Compression):** Aplana la jerarquía durante `find(u)`.
    - **Unión por rango (Union by Rank):** Mantiene árboles de profundidad mínima.
    - Complejidad amortizada: $\mathcal{O}(\alpha(V))$ por operación, donde $\alpha$ es la función inversa de Ackermann.

---

## FASE 2: MODELADO GEOMÉTRICO Y TOPOLÓGICO DE LOS DOS GRAFOS ($G_E$ Y $G_M$)

### 2.1 Principio de Independencia Espacial
Ambos grafos comparten el mismo sistema cartesiano bidimensional $(x, y)$, pero **no existe ninguna arista que conecte un vértice de $G_E$ con uno de $G_M$**. La interacción ocurre exclusivamente por la proximidad euclidiana del alcance balístico de las tropas.

### 2.2 Grafo Elevado $G_E$ (Fuerzas Defensivas)
- **Vértices:** Posiciones terrestres con elevación $z \ge 0$.
  - `BASE`: Exactamente una base de mando por escenario ($z=0$). Punto de compra y spawn de tropas.
  - `CANDIDATE`: Ubicaciones candidatas a convertirse en torres de vigilancia.
  - `TRANSIT`: Puntos de paso intermedios para caminos o puentes.
  - `HELIPORT`: Helipuertos para operaciones aéreas.
- **Aristas:** No dirigidas, con tiempos positivos `time_walk` y `time_moto` (o `null` si el medio no se permite).
  - Los puentes cuentan con resistencia entera positiva `bridge_max_hp` y `bridge_current_hp`.

### 2.3 Grafo del Laberinto $G_M$ (Convoy Enemigo)
- **Vértices:** Intersecciones terrestres con una única `M_ENTRADA` y una única `M_SALIDA` ($\text{entrada} \ne \text{salida}$).
- **Corredores:** Aristas no dirigidas con longitud $l(e) > 0$ y velocidad permitida $v(e) > 0$.
  - Tiempo nominal de travesía:
    $$t(e) = \frac{l(e)}{v(e)}$$
  - Al iniciar el escenario se valida obligatoriamente la existencia de al menos un camino transitable entre la entrada y la salida.

---

## FASE 3: PLANIFICACIÓN DE DEFENSAS (KRUSKAL MST Y SELECCIÓN VORAZ)

### 3.1 Árbol de Expansión Mínima ($T_E$)
- Se calcula sobre la **componente conexa de $G_E$ que contiene a la base**, utilizando como peso el tiempo a pie (`time_walk`).
- Todo vértice fuera de dicha componente queda inhabilitado para ser torre.
- El árbol es una **referencia de conectividad garantizada** y **no elimina** las demás aristas del grafo.
- Complejidad: $\mathcal{O}(E \log E)$.

### 3.2 Algoritmo Voraz de Selección de Torres
En cada iteración $i \in [1, K]$, se calcula la puntuación $S(p)$ para cada posición candidata $p$:

$$S(p) = \frac{C(p)}{1 + \frac{D_T(B, p)}{D_0}}$$

Donde:
- $C(p)$: Longitud total de corredores de $G_M$ **aún no cubiertos** cuyo punto medio horizontal esté a distancia euclidiana $\le R_v(p)$.
- $D_T(B, p)$: Tiempo a pie desde la base $B$ hasta $p$ siguiendo **exclusivamente el árbol $T_E$** (calculado mediante recorrido BFS/Dijkstra sobre $T_E$).
- $D_0$: Tiempo de referencia positivo configurable del escenario.

**Criterios de desempate:**
1. Mayor puntuación $S(p)$.
2. Menor distancia $D_T(B, p)$.
3. Identificador lexicográfico inmutable (ej. `V_C1` < `V_C2`).

El proceso se detiene cuando se eligen $K$ torres o cuando ningún candidato aporta cobertura nueva ($C(p) = 0$).

---

## FASE 4: UNIDADES DEFENSIVAS, FÓRMULAS BALÍSTICAS Y COMBATE

### 4.1 Capacidad y Tropas
Cada torre seleccionada admite un **máximo de 3 soldados**, independientemente de su especialidad.

| Unidad | Costo | Daño ($d_s$) | Alcance Base ($R_{\text{base}}$) | Frecuencia ($f_s$) |
|---|:---:|:---:|:---:|:---:|
| **Infantería** | \$100 | 10 HP | 5.0 u | 1.0 ataque/s |
| **Francotirador** | \$300 | 50 HP | 20.0 u | 0.5 ataques/s |
| **Artillero** | \$500 | 100 HP | 15.0 u | 0.2 ataques/s |

### 4.2 Alcance Efectivo por Altura Balística
El alcance efectivo $R_{\text{ef}}$ se potencia proporcionalmente a la altura $z$ del vértice de la torre:
$$R_{\text{ef}} = R_{\text{base}} \cdot (1 + \beta \cdot z)$$
Donde $\beta \ge 0$ es el coeficiente balístico definido en la configuración del escenario.

### 4.3 Reglas de Prioridad de Ataque
- **Infantería y Francotirador:** Atacan a la unidad enemiga viva con **menor resistencia actual**, rompiendo empates por identificador del enemigo.
- **Artillero:** Aplica su daño de área (**AOE**) a **todas** las unidades vivas dentro de su radio de alcance efectivo.
- Los soldados en tránsito no pueden atacar.
- Cada enemigo destruido genera su recompensa financiera una sola vez.

---

## FASE 5: DINÁMICA DEL CONVOY, ESTIMACIÓN DE PELIGRO Y NAVEGACIÓN REACTIVA

### 5.1 Estimación de Peligro en Corredores
Para cada corredor $e$, se evalúa la tasa de daño en 3 puntos: inicio ($q_0$), punto medio ($q_m$) y final ($q_1$).

$$D(q) = \sum_{s \in \text{alcance}(q)} d_s \cdot f_s$$

- La tasa del artillero se cuenta una sola vez por soldado en la estimación.
- El peligro promedio es $\bar{D} = \frac{D(q_0) + D(q_m) + D(q_1)}{3}$.
- El daño potencial es $P(e) = \bar{D} \cdot t(e)$.
- El peso dinámico del corredor que rige las decisiones del convoy es:
$$w(e) = t(e) + \alpha \cdot P(e)$$
Donde $\alpha \ge 0$ convierte el daño estimado en penalización equivalente de tiempo.

### 5.2 Navegación Reactiva
- En cada intersección de $G_M$, el convoy ejecuta **Dijkstra propio** con pesos $w(e)$ para determinar el camino más seguro hacia `M_SALIDA`.
- **Prevención de retrocesos:** Si la ruta óptima exige regresar al vértice inmediatamente anterior, el convoy verifica si existe una ruta alternativa con inicio diferente y selecciona la más conveniente; sólo retrocede si no hay otra vía hacia la salida.

---

## FASE 6: DESPLAZAMIENTOS TERRESTRES Y PUENTES DINÁMICOS

### 6.1 Desplazamiento Terrestre
- **A pie:** 1 soldado por orden. No desgasta puentes.
- **En motocicleta:** 1 o 2 soldados juntos por moto. Velocidad más rápida según `time_moto`.

### 6.2 Desgaste y Reconstrucción de Puentes
- Cada motocicleta que termina de cruzar un puente reduce su resistencia actual en 1 unidad:
$$\text{HP}_{\text{actual}} \leftarrow \text{HP}_{\text{actual}} - 1$$
- Al llegar a $\text{HP}=0$, el puente colapsa:
  - Queda inhabilitado inmediatamente para nuevos cruces.
  - Los cruces ya iniciados pueden finalizar su tránsito.
  - Se activa la **cuadrilla de reconstrucción**, restaurando el puente tras un tiempo configurable `bridge_repair_time`.
  - Soldados en tránsito que queden cortados recalculan ruta desde el siguiente nodo seguro o se detienen temporalmente hasta su reparación.

---

## FASE 7: TRANSPORTE AÉREO Y DISTRIBUCIÓN DE EXCEDENTES

### 7.1 Reglas del Helicóptero
- Transporta hasta un máximo de **4 soldados** entre posiciones válidas del grafo elevado.
- Duración del vuelo según distancia euclidiana directa:
$$t_{\text{vuelo}} = \frac{\text{distancia}(u, v)}{v_{\text{heli}}}$$
- Requiere helipuerto disponible, presupuesto suficiente y no superar el número máximo de usos configurados.

### 7.2 Algoritmo de Distribución de Excedentes
Al arribar a la torre destino:
1. Desembarca soldados hasta agotar la capacidad libre (considerando reservas previas).
2. Si quedan soldados excedentes a bordo:
   - Se buscan sucesivamente otras torres habilitadas en orden de **menor distancia euclidiana** desde la posición actual del helicóptero.
   - En caso de empate en distancia, se desempatan por orden lexicográfico.
   - Si ninguna torre puede recibir soldados, los excedentes retornan a la base de manera segura.
3. Todo el trayecto de distribución y regreso pertenece a la misma operación sin consumir usos extra.

---

## FASE 8: PRESUPUESTO, RELOJ LÓGICO Y CONDICIONES DE FIN

### 8.1 Finanzas e Invariantes
- Presupuesto inicial parametrizado en JSON.
- Se distingue rigurosamente entre **presupuesto disponible** y **presupuesto reservado** (para vuelos o compras en curso).
- Saldo jamás negativo: toda orden que exceda los fondos es rechazada sin alterar el estado.

### 8.2 Reloj Lógico y Simultaneidad
- El reloj de simulación avanza en intervalos discretos de **$\Delta t = 0.25$ segundos**.
- En coincidencias temporales se aplica el siguiente orden de resolución estricto:
  1. Resolución de ataques balísticos de tropas sobre máquinas.
  2. Verificación de presencia de máquinas vivas en la salida (`M_SALIDA`).
  3. Límite de tiempo lógico (`time_limit`).

### 8.3 Condiciones de Finalización
1. **Victoria por Eliminación:** Todas las unidades enemigas del convoy son destruidas.
2. **Victoria por Resistencia:** Se alcanzan los 300 s (o el tiempo límite configurado) sin que ninguna máquina viva llegue a la salida.
3. **Derrota:** Al menos una máquina viva del convoy alcanza `M_SALIDA`.

---

## FASE 9: INTERFAZ GRÁFICA DUAL (PYGAME + REACT WEB)

### 9.1 Cliente Pygame (`desktop/main.py`)
- **100% Vectorial procedural:** Implementado exclusivamente con `pygame.draw`, `pygame.Surface` y `pygame.font`. Cero imágenes PNG/SVG.
- **Selector nativo:** Integra `tkinter.filedialog.askopenfilename` para seleccionar dinámicamente cualquier JSON sin rutas fijas.
- **Diseño en 3 Zonas:**
  - **Barra Superior (Top Bar):** Control de reloj, velocidad, presupuesto, estado de conexión y botones de capas ($T_E$, $R_v$, Audio).
  - **Lienzo Central (72% de pantalla):** Renderizado de ambos grafos con márgenes amplios (padding), puentes con rieles paralelos y 3 ranuras circulares indicadoras de tropas en las torres.
  - **Panel Lateral Derecho (28% de pantalla):** Panel superior de reclutamiento y órdenes de transporte; panel inferior con bitácora de eventos con scroll.

### 9.2 Cliente Web React (`frontend/`)
- Construido con React 18, Vite y arquitectura de Vertical Slicing.
- Sintetizador procedimental de audio Web Audio API (sin dependencias externas).
- Paleta visual clara en modo táctico con animaciones suaves de combate.

---

## FASE 10: AUDITORÍA, SUITE DEL PROFESOR Y VERIFICACIÓN AL 100%

### 10.1 Suite de Examen del Profesor (`test_simulador_profesor.py`)
Diseñada específicamente en la rama `prueba` para evaluar los 10 puntos críticos de la especificación académica:
1. `test_profesor_01`: Ausencia absoluta de librerías externas de grafos.
2. `test_profesor_02`: Independencia topológica entre $G_E$ y $G_M$.
3. `test_profesor_03`: Kruskal con tiempos a pie y fórmula voraz $S(p)$.
4. `test_profesor_04`: Fórmula balística $R_{\text{ef}}$ y prioridades de daño (menor HP y AOE).
5. `test_profesor_05`: Cálculo dinámico de peligro $w(e)$ y re-enrutamiento reactivo.
6. `test_profesor_06`: Desgaste exclusivo por motocicletas y reconstrucción de puentes.
7. `test_profesor_07`: Capacidad de 4 soldados en helicóptero y distribución de excedentes.
8. `test_profesor_08`: Integridad presupuestal y recompensas únicas.
9. `test_profesor_09`: Reloj lógico de 0.25 s y resolución de condiciones de fin.
10. `test_profesor_10`: Arranque vacío y validación de esquemas JSON.

### 10.2 Resultados de la Auditoría Integral
- **Backend:** 232 pruebas pasando (100%).
- **Auditoría de Enunciado:** 47 de 47 puntos verificados contra servidor HTTP real.
- **Suite Pygame:** 91 pruebas pasando (100%).
- **Límite de Gobernanza:** Todos los archivos de código fuente cumplen el límite estricto de **menos de 150 líneas**.
