# La derrota del dictador General P. Tardo

Simulador de grafos para el segundo proyecto de Estructuras de Datos. Un convoy de máquinas recorre un
laberinto (grafo **GM**) y una resistencia humana lo detiene desde una red elevada de caminos y puentes
(grafo **GE**). Todo se implementó desde cero, sin NetworkX ni librerías de grafos.

## Qué hace

1. **Carga un escenario JSON** y comprueba que sea válido (una base, camino entrada → salida).
2. **Planifica la defensa**: árbol de expansión mínima (Kruskal + Union-Find) y elección voraz de torres con
   `S(p) = C(p) / (1 + D_T(B,p) / D₀)`.
3. **Simula el combate** con un reloj lógico: compra de soldados, traslado a pie / moto / helicóptero, puentes que
   se desgastan y se reconstruyen, y un convoy que recalcula su ruta (Dijkstra) en cada intersección.

## Cómo ejecutarlo

Backend (Flask, puerto 5000):

```bash
cd backend
python -m pip install -r requirements-dev.txt
python run.py
```

Frontend (React + Vite, puerto 5173):

```bash
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. La aplicación **arranca vacía**: el escenario se elige siempre desde la pantalla
**Inicio**. Hay cuatro para probar: `docs/escenario_general_p_tardo.json` (simple) y `docs/escenario_complejo.json` (ciclos, empates, un vértice aislado y rutas alternativas).
`docs/escenario_puentes.json` sirve para probar puentes que colapsan y `docs/escenario_cuadrilla.json` la reconstrucción que ocupa a N personas, las calles sin puente y los medios no permitidos. Se cargan desde la pantalla **Inicio**.

Pruebas de los algoritmos (170 pruebas, no necesitan Flask ni navegador):

```bash
cd backend
python -m pytest tests
```

O, mejor, un solo comando que revisa cada sección del enunciado y las reglas del proyecto:

```bash
python verificar.py
```

## Estructura

```
backend/src/core/structures/  MinHeap: cola de prioridad propia (montículo binario) para Dijkstra
backend/src/features/
  elevated_graph/   GE: entidades, grafo, Union-Find, Kruskal, selección de torres, Dijkstra a pie/moto
  labyrinth/        GM: entidades, grafo, peligro w(e), enrutador del convoy
  scenario/         carga y validación del JSON, sesión en memoria
  simulation/       mundo, reloj, convoy, combate, puentes, transporte terrestre y aéreo, API
frontend/src/
  features/         intro, graphs, plan, simulation, map (SVG reutilizable)
  hooks/            useScenario, useSimulation (estado + llamadas a la API)
  styles/           tokens de color y estilos por área
docs/               enunciado, propuestas, escenarios JSON y guía de exposición
```

Cada archivo tiene menos de 150 líneas y la lógica de grafos no depende de Flask: se prueba sola.

## Interfaz

Paleta beige y negro: fondo beige "papel", barra y mapa en negro, y tres acentos apagados (ocre = torres,
terracota = enemigo, salvia = defensores). Es responsive: en pantallas pequeñas los paneles se apilan debajo del
mapa y la navegación se desliza horizontalmente.

> Nota para el equipo: `docs/rules/governance_and_team_rules.md` pide "solo modo claro". La interfaz sigue siendo
> clara (fondo beige) pero usa negro para la barra y el mapa; si el equipo prefiere cambiar esa regla, hay que
> actualizarla en el documento.

## Documentación

- [`docs/guia_ejecucion_y_verificacion.md`](docs/guia_ejecucion_y_verificacion.md): **empieza aquí**: cómo correr el
  proyecto paso a paso, verificarlo con un comando y recorrerlo a mano.
- [`docs/guia_pruebas.md`](docs/guia_pruebas.md): cómo verificar cada punto del enunciado, paso a paso (automático y en la
  interfaz).
- [`docs/manual_usuario.md`](docs/manual_usuario.md) y [`docs/manual_tecnico.md`](docs/manual_tecnico.md): manuales
  exigidos por el enunciado (uso de la aplicación; dominio, JSON, invariantes, algoritmos y complejidad).
- [`docs/reporte_uso_ia.md`](docs/reporte_uso_ia.md): reporte de uso de inteligencia artificial.
- [`docs/guia_exposicion.md`](docs/guia_exposicion.md): explicación de estructuras, complejidades, guion de demo y
  limitaciones conocidas.
- [`docs/project_division_team.md`](docs/project_division_team.md) y
  [`docs/rules/governance_and_team_rules.md`](docs/rules/governance_and_team_rules.md): reparto y reglas del equipo.
