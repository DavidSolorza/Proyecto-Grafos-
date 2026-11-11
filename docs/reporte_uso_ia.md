# Reporte de uso de inteligencia artificial

**Proyecto 2 de Estructuras de Datos — "La derrota del dictador General P. Tardo"**

El enunciado (sección 14) pide un reporte del uso de IA. Este documento declara qué herramienta se usó, para qué,
qué produjo, cómo se verificó y qué decidieron las personas. Está redactado a partir de lo que realmente ocurrió en las
sesiones de trabajo. Los campos marcados con **[completar]** solo pueden llenarlos los integrantes.

---

## 1. Herramienta y alcance

| Dato | Detalle |
|---|---|
| Herramienta | **Claude Code** (de Anthropic), en su aplicación de escritorio. |
| Modelo | Claude (familia Claude 5; en la sesión figuraba como *Claude Sonnet 5.5*). |
| Modo de uso | Asistente con acceso al repositorio: leyó el enunciado y el código, escribió y editó archivos, ejecutó pruebas y manejó el navegador integrado para probar la interfaz. |
| Punto de partida | La base del proyecto (commit `f66deda`, "initial project base with decoupled Flask backend and React frontend") y los documentos de propuesta y reglas de `docs/` ya existían antes de estas sesiones. |
| Integrantes | **[completar: nombres y qué parte coordinó cada uno]** |
| Fechas de trabajo | **[completar]** |

## 2. Qué hizo la IA

| Área | Aporte de la IA |
|---|---|
| Análisis | Leyó el enunciado completo y lo convirtió en una lista de requisitos verificables. |
| Backend | Implementó los algoritmos y la simulación: validación del JSON, Union-Find, Kruskal, selección voraz de torres, Dijkstra, montículo binario propio, peligro y navegación reactiva, combate, puentes con cuadrilla, transporte terrestre y aéreo, presupuesto, reloj lógico y API REST. |
| Frontend | Rediseñó la interfaz (paleta beige y negro, diseño responsive): vistas de inicio, grafos, plan y simulación, mapa SVG, paneles y bitácora. |
| Pruebas | Escribió las 170 pruebas automáticas y el comando `verificar.py`. Hizo pruebas de mutación y recorridos de la interfaz en el navegador. |
| Documentación | Redactó la guía de ejecución y verificación, la guía de pruebas, la guía de exposición, el manual de usuario, el manual técnico y este reporte. |

## 3. Qué decidieron las personas

Las decisiones de rumbo las tomaron los integrantes, dando instrucciones a la IA en cada sesión:

| Decisión | Quién |
|---|---|
| Hacer el proyecto "fácil de entender, manejar y exponer", que pareciera hecho por estudiantes, responsive, con paleta negro/beige y estilo moderno y didáctico | Integrante (petición inicial) |
| Probar punto por punto todo el enunciado y recibir una guía para repetirlo | Integrante |
| No hacer `commit` hasta indicarlo (se respetó; el `commit` se hizo cuando se pidió) | Integrante |
| Que la aplicación **arranque vacía** (sin escenario fijo) y que Dijkstra use una **cola de prioridad propia** en lugar de `heapq` | Integrante |
| Verificar de nuevo que todos los puntos estuvieran completos y generar los entregables | Integrante |
| Mantener React + Flask en lugar de Pygame | Equipo (propuesta inicial). **[completar: confirmación del docente]** |

Reparto interno del trabajo y revisión del código por cada integrante: **[completar]**.

## 4. Cómo se verificó el trabajo de la IA

El código generado por una IA puede ser incorrecto aunque parezca razonable, así que no se aceptó sin comprobarlo:

1. **Pruebas automáticas (170).** Una por sección del enunciado. Los algoritmos se comparan contra implementaciones
   independientes: Kruskal contra fuerza bruta (todos los conjuntos de V−1 aristas), Dijkstra contra la búsqueda de todas
   las rutas simples y contra Bellman-Ford en grafos aleatorios, el montículo contra `sorted`.
2. **Pruebas de mutación manuales.** Se rompieron a propósito reglas del código (orden de fin de partida, desgaste al caminar,
   recompensa duplicada, cuadrilla de reparación, medios no permitidos…) y se comprobó que al menos una prueba fallara.
   Las mutaciones que sobrevivieron al principio revelaron pruebas débiles y se reforzaron.
3. **Recorrido en la interfaz real.** Se cargaron escenarios válidos e inválidos, se compró, se movió, se hicieron colapsar
   puentes y se llegó a cada resultado final, comparando con valores calculados aparte (por ejemplo derrota a 23.0 s y
   victoria por eliminación a 14.25 s con $1750 en el escenario simple).
4. **Reglas del proyecto automatizadas.** `python verificar.py` revisa que no haya librerías de grafos ni `heapq`, que cada
   archivo tenga menos de 150 líneas y que los escenarios de ejemplo sean válidos.

## 5. Errores de la IA que se encontraron y corrigieron

Declarar los errores es parte del uso responsable de la herramienta:

| Error | Cómo se detectó | Corrección |
|---|---|---|
| La validación del JSON aceptaba 12 de 15 escenarios inválidos (por ejemplo `D0 = 0`, que luego dividiría por cero) | Pruebas de escenarios inválidos | Validador completo, con 33 casos de rechazo. |
| El convoy trataba un callejón sin salida como "ruta alternativa" | Prueba de navegación con ramas | Las rutas alternativas son caminos simples (no pasan otra vez por el vértice de decisión). |
| Usaba `heapq` de la biblioteca estándar en Dijkstra | Observación del integrante al revisar el enunciado | Montículo binario propio y una prueba que impide importar `heapq`. |
| Cargaba un escenario de ejemplo al arrancar (ruta fija) | Revisión del requisito de la sección 12 | La aplicación arranca vacía. |
| No modelaba medios de transporte no permitidos ni calles sin puente, y la reconstrucción no ocupaba a N personas | Segunda lectura completa del enunciado | Se implementaron (`null` en el tiempo, aristas sin `bridge_max_hp`, `bridge_repair_crew`) con pruebas. |
| Varias pruebas propias eran débiles (siempre verdaderas o con un destino equivocado) | Revisión y pruebas de mutación | Se reescribieron. |
| Leyenda del mapa ilegible sobre el fondo beige; botones de compra en orden alfabético; error 409 espurio al recargar | Recorrido en el navegador | Corregidos. |

## 6. Limitaciones y riesgos que se declaran

- La IA propuso algunas **decisiones de diseño** donde el enunciado deja libertad (quién forma la cuadrilla, el significado
  de `max_uses`, el paso de 0.25 s). Están en la sección 7 del [manual técnico](manual_tecnico.md) para que cada integrante
  las pueda defender o cambiar.
- El enunciado pide **Pygame**; la interfaz usa React. Es una decisión de equipo que debe confirmarse con el docente.
- Las pruebas verifican el comportamiento descrito en el enunciado tal como se interpretó; una interpretación distinta
  del docente podría requerir ajustes.
- Los videos de explicación y de funcionamiento **no los produce la IA**: los deben grabar los integrantes.
- El historial de Git refleja los cambios hechos con asistencia de IA; cada commit incluye la línea `Co-Authored-By`
  con la herramienta. Los aportes individuales de cada integrante dependen de quién ejecutó y confirmó cada cambio.

## 7. Cómo asegurar que cada integrante domina lo entregado

La sustentación exige que cada integrante explique las estructuras, justifique decisiones y analice efectos. Recomendación
de estudio, en orden:

1. [`guia_exposicion.md`](guia_exposicion.md) — estructuras, algoritmos, preguntas probables.
2. [`manual_tecnico.md`](manual_tecnico.md) — modelo de dominio, invariantes, complejidad.
3. Ejecutar [`guia_ejecucion_y_verificacion.md`](guia_ejecucion_y_verificacion.md) y repetir los experimentos de
   "rómpelo tú" y de mutación de [`guia_pruebas.md`](guia_pruebas.md) §3 y §4 para ver cómo reaccionan el código y las pruebas.
4. Leer, en el código, `min_heap.py`, `disjoint_set.py`, `mst_service.py`, `tower_selector.py`, `router.py` y `bridges.py`:
   son los archivos sobre los que más probablemente pedirán cambios en vivo.

## 8. Declaración

Los integrantes declaran que usaron una herramienta de IA generativa como se describe arriba, que revisaron y
comprendieron el código entregado y que se responsabilizan de su contenido.

**[completar: nombres, firmas o confirmación de cada integrante y fecha]**
