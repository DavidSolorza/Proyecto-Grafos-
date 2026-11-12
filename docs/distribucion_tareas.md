# Distribución de tareas del equipo

**Proyecto 2 de Estructuras de Datos — "La derrota del dictador General P. Tardo"**

| Integrante | Rol en el proyecto |
|---|---|
| **Juan Sebastián Naranjo Verdugo** | Integrante A: red elevada (GE), planificación de la defensa, validación del escenario y núcleo del cliente Pygame. |
| **David Josué Solorza Viera** | Integrante B: laberinto (GM), convoy, combate, reloj lógico, transporte aéreo y pantalla de simulación. |

Este reparto desarrolla el que ya existía en [`project_division_team.md`](project_division_team.md) (Developer A y
Developer B) y lo extiende al cliente Pygame, a las pruebas y a los entregables. Sigue la estrategia de *rebanadas
verticales*: **cada integrante responde por una parte completa del sistema**, desde la estructura de datos hasta lo que
se ve en pantalla, y ambos conocen el resto lo suficiente para defenderlo.

> **Sobre el origen del código.** El código y los documentos se desarrollaron con asistencia de IA (ver
> [`reporte_uso_ia.md`](reporte_uso_ia.md)). Esta distribución define **quién es responsable de cada parte**: quién la
> debe dominar, defender en la sustentación y mantener. No pretende afirmar quién escribió cada línea.

---

## 1. Resumen visual

```
                      Juan Sebastián (A)                         David Josué (B)
            ┌───────────────────────────────┐        ┌───────────────────────────────────┐
 Datos      │ GE · Union-Find · Kruskal     │        │ GM · peligro w(e) · Dijkstra del  │
 y          │ Selección voraz de torres     │        │ convoy · combate · reloj lógico   │
 algoritmos │ Dijkstra de soldados · puentes│        │ helicóptero · presupuesto         │
            └───────────────────────────────┘        └───────────────────────────────────┘
            ┌───────────────────────────────┐        ┌───────────────────────────────────┐
 API Flask  │ escenario · plan · sesión     │        │ simulación · unidades · transporte│
            └───────────────────────────────┘        └───────────────────────────────────┘
            ┌───────────────────────────────┐        ┌───────────────────────────────────┐
 Pygame     │ núcleo, mapa GE, selector JSON│        │ pantalla de simulación, unidades  │
            │ Inicio · Grafos · Plan        │        │ comandos de la partida            │
            └───────────────────────────────┘        └───────────────────────────────────┘
            ┌───────────────────────────────┐        ┌───────────────────────────────────┐
 React      │ Inicio · Grafos · Plan        │        │ Simulación · sincronización       │
            └───────────────────────────────┘        └───────────────────────────────────┘
```

## 2. Juan Sebastián Naranjo Verdugo — Integrante A

**Responsabilidad:** que el escenario sea válido, que el plan de defensa sea correcto y que el usuario pueda cargarlo,
verlo y planificar desde la interfaz.

### 2.1 Backend (`backend/src/features/`)

| Área | Archivos | Secciones del enunciado |
|---|---|---|
| Grafo elevado GE | `elevated_graph/domain/entities.py`, `graph_e.py` | §3 |
| Validación y carga del JSON | `scenario/application/validator.py`, `validator_params.py`, `loader.py`, `scenario/domain/` | §3, §12 |
| Estructuras propias | `core/structures/min_heap.py`, `elevated_graph/application/disjoint_set.py` | §2 |
| Árbol de expansión mínima | `elevated_graph/application/mst_service.py` | §4 |
| Selección voraz de torres | `elevated_graph/application/tower_selector.py`, `defense_planner.py` | §4 |
| Camino mínimo de soldados | `elevated_graph/application/ge_paths.py` | §7 |
| Traslado terrestre | `simulation/application/ground.py` | §7 |
| Puentes y cuadrilla de N personas | `simulation/application/bridges.py` | §3, §8 |
| Sesión y API de escenario y plan | `scenario/application/session.py`, `scenario/infrastructure/routes.py`, `elevated_graph/infrastructure/routes.py` | §12 |

### 2.2 Cliente Pygame (`desktop/tardo_ui/`)

| Área | Archivos |
|---|---|
| Cliente de la API y arranque del backend | `api.py`, `launcher.py`, `main.py` |
| Estado y operaciones de la interfaz | `store.py` |
| Widgets y tema | `ui.py`, `theme.py` |
| Selector de archivos JSON (sin rutas fijas) | `filepicker.py` |
| Mapa: transformación y capas de GE | `map/view.py`, `map/layers.py` (caminos, puentes, vértices), `map/canvas.py` |
| Pantallas Inicio, Los grafos y Plan de defensa | `screens/home.py`, `graphs.py`, `plan.py`, `common.py` |
| Ventana principal, pestañas y avisos | `app.py`, `header.py` |
| Escala fluida (`clamp`) y efectos visuales | `theme.py` (`ui_scale`), `effects.py`, `ui.py`, `map/canvas.py` |

### 2.3 Cliente React (`frontend/src/`)

Vistas de Inicio, Grafos y Plan (`features/intro`, `features/graphs`, `features/plan`), componentes `FileUploader`,
`ScenarioSummary`, `NoScenario` y el mapa compartido (`features/map`). Sistema de diseño fluido: `styles/base.css`, `nav.css`, `ui.css`, `data.css` e `intro.css`
(tokens con `clamp()`, rejillas y barra superior).

### 2.4 Pruebas

`test_validation.py`, `test_s3_graphs.py`, `test_s3_initial_route.py`, `test_edge_rules.py`, `test_s4_planning.py`, `test_min_heap.py`,
`test_repair_crew.py`, `test_s7_ground.py` (backend), `audit/c_scenario_plan.py` (auditoría de §3, §4 y §12) y, en `desktop/tests/`, `test_ui_store.py`, `test_ui_filepicker.py`,
`test_ui_map.py`.

### 2.5 Escenarios y documentos

- Escenarios: `escenario_general_p_tardo.json` (simple) y `escenario_puentes.json`.
- Documentos: [`manual_tecnico.md`](manual_tecnico.md) §3–§5, §6.1–§6.3, §6.6–§6.7 y §12.1–§12.6 (cliente Pygame: arquitectura, selector, sincronización);
  [`guia_ejecucion_y_verificacion.md`](guia_ejecucion_y_verificacion.md).

### 2.6 Qué debe poder explicar y modificar en la sustentación

- Cómo se guarda el grafo (lista de adyacencia) y qué cuesta cada operación.
- Kruskal con Union-Find: por qué el desempate por id hace determinista el árbol y cuál es su complejidad.
- La fórmula `S(p)`, por qué se redondea al comparar y qué pasa si dos candidatas empatan.
- El montículo binario propio: `push`, `pop`, y por qué Dijkstra usa entradas obsoletas.
- La validación: qué se rechaza y por qué antes de construir los grafos.
- El ciclo de vida de un puente (desgaste, colapso, cuadrilla, reconstrucción) y de un soldado detenido.
- Cómo el cliente Pygame habla con Flask sin tocar los algoritmos.

---

## 3. David Josué Solorza Viera — Integrante B

**Responsabilidad:** que la partida se comporte según las reglas (convoy, peligro, combate, tiempo, dinero, helicóptero) y
que el usuario pueda comprar, ordenar y observar todo eso en pantalla.

### 3.1 Backend (`backend/src/features/`)

| Área | Archivos | Secciones del enunciado |
|---|---|---|
| Laberinto GM | `labyrinth/domain/entities.py`, `graph_m.py` | §3 |
| Peligro y pesos de corredores | `labyrinth/application/danger.py` | §6 |
| Navegación reactiva del convoy | `labyrinth/application/router.py`, `simulation/application/convoy.py` | §6 |
| Combate | `simulation/application/combat.py`, `simulation/domain/units.py` | §5 |
| Mundo, presupuesto y torres | `simulation/domain/world.py` | §5, §10 |
| Reloj lógico y fin de partida | `simulation/application/engine.py` | §11 |
| Helicóptero y reparto de excedentes | `simulation/application/air.py` | §9 |
| Estado para la interfaz | `simulation/application/serializer.py` | §13 |
| API de simulación y huella de sesión | `simulation/infrastructure/routes.py`, `/api/scenario/status` | §12, §13 |

### 3.2 Cliente Pygame (`desktop/tardo_ui/`)

| Área | Archivos |
|---|---|
| Comandos de la partida (comprar, elegir, enviar, ruta, reloj) | `commands.py` |
| Unidades en el mapa y corredores con peligro | `map/units.py`, `map/layers.py` (corredores) |
| Pantalla de simulación y cartel final | `screens/sim.py` |
| Paneles de control, compra, transporte, convoy y bitácora | `screens/sim_controls.py`, `sim_transport.py`, `sim_convoy.py` |
| Sincronización con otros clientes | `store.py` (`sync`, `tick_real`) |

### 3.3 Cliente React (`frontend/src/`)

Vista de Simulación y sus paneles (`features/simulation`), `useSimulation`, `useSync` (sincronización con Pygame) y
`SimOverlay` del mapa, con sus estilos `styles/sim.css` y `styles/map.css`.

### 3.4 Pruebas

`test_s5_combat.py`, `test_s6_convoy.py`, `test_s9_air_budget.py`, `test_s11_end.py`, `test_s12_api.py`,
`test_s12_empty_start.py`, `test_fuzz_invariants.py` (backend), `audit/c_combat_convoy.py`, `audit/c_bridges_air_time.py`, `audit/c_extra.py`
(auditoría de §5 a §11) y, en `desktop/tests/`, `test_ui_screens.py`, `test_ui_commands.py`, `test_ui_sync.py`, `test_ui_integration.py`,
`test_ui_s13_audit.py`.

### 3.5 Escenarios y documentos

- Escenarios: `escenario_complejo.json` y `escenario_cuadrilla.json`.
- Documentos: [`manual_usuario.md`](manual_usuario.md); [`manual_tecnico.md`](manual_tecnico.md) §6.4–§6.5, §6.8–§6.9,
  §9, §10 y §12.7–§12.9 (requisitos de §13 y pruebas del cliente); [`guia_exposicion.md`](guia_exposicion.md).

### 3.6 Qué debe poder explicar y modificar en la sustentación

- `D(q)`, `P(e)` y `w(e) = t(e) + α·P(e)`; por qué el convoy recalcula en cada intersección y cómo evita retroceder.
- Por qué las rutas alternativas son caminos simples (el caso del callejón sin salida).
- Orden de un paso del reloj y prioridad de fin de partida (ataques → salida → tiempo).
- Reglas de combate: alcance efectivo `R_ef`, blanco de menor vida, artillero de área, recompensa única.
- Helicóptero: reservas de cupo, reparto de excedentes y por qué el uso y el costo se cuentan una sola vez.
- Presupuesto disponible/reservado y por qué nunca queda negativo.
- Cómo la interfaz Pygame explica cada decisión (bitácora y tabla "¿Por qué ese camino?").

---

## 4. Tareas compartidas

| Tarea | Cómo se reparte |
|---|---|
| Decisiones de diseño abiertas (tabla de la §7 del manual técnico) | Se discuten juntos; cada uno defiende las de su parte. |
| Contrato de la API REST (`manual_tecnico.md` §9) | A mantiene escenario y plan; B mantiene simulación y estado. Todo cambio se avisa al otro. |
| Auditoría del enunciado | Cada uno mantiene las comprobaciones de `backend/audit/` de su parte y ambos ejecutan `python verificar.py` antes de cada entrega. |
| Revisión cruzada | A revisa el código de B y B el de A antes de cada entrega, ejecutando `python verificar.py`. |
| Reporte de uso de IA | Lo completan ambos: nombres, fechas, qué revisó cada uno y la declaración final. |
| Repositorio Git | Cada uno hace *commits* de lo que ejecuta y revisa, con mensajes descriptivos, para que los aportes sean verificables. |
| Preparación de la sustentación | Ambos ensayan la demo completa (Pygame, React y Flask funcionando juntos). |

## 5. Entregables del enunciado (sección 14) y responsables

| Entregable | Responsable principal | Apoyo |
|---|---|---|
| Código fuente en Git con instrucciones y comentarios en inglés | Ambos (cada uno su parte) | `README.md`, `guia_ejecucion_y_verificacion.md` |
| Manual de usuario | David Josué | Juan Sebastián revisa la parte del plan y de la carga |
| Manual técnico (dominio, grafos, JSON, invariantes, decisiones, complejidad) | Juan Sebastián (grafos, JSON, MST, torres) y David Josué (convoy, combate, reloj, aire) | Revisión cruzada |
| Reporte de uso de IA | Ambos | — |
| Dos escenarios JSON de distinta complejidad | Juan Sebastián: simple y puentes. David Josué: complejo y cuadrilla | — |
| Video de explicación en una segunda lengua (estructuras y algoritmos) | **Ambos participan** | Cada uno explica su parte (secciones 2.6 y 3.6) |
| Videotutorial del sistema funcionando | **Ambos participan** | Guion: `guia_ejecucion_y_verificacion.md` §C |

## 6. Orden de trabajo sugerido

1. **Juntos:** ejecutar la guía de ejecución (Pygame, React y Flask) y `python verificar.py`.
2. **Cada uno** lee los archivos de su parte (secciones 2 y 3) y repite los experimentos de "rómpelo tú" y de mutación de
   [`guia_pruebas.md`](guia_pruebas.md) que correspondan a su parte.
3. **Intercambio:** cada uno explica su parte al otro durante 15 minutos y responde las preguntas de las secciones 2.6 y 3.6.
4. **Ensayo de sustentación:** el docente puede pedir cambios en vivo; cada uno practica modificar una regla de su parte
   (por ejemplo, el desempate de torres o la prioridad de fin de partida) y comprobar que alguna prueba falla.
5. **Videos y entrega:** grabar con la participación de ambos y completar los campos pendientes del reporte de IA.
