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
| Integrantes | Juan Sebastián Naranjo Verdugo y David Josué Solorza Viera (reparto en [`distribucion_tareas.md`](distribucion_tareas.md)). **[completar: qué revisó y ejecutó cada uno]** |
| Fechas de trabajo | **[completar]** |

## 2. Qué hizo la IA

| Área | Aporte de la IA |
|---|---|
| Análisis | Leyó el enunciado completo y lo convirtió en una lista de requisitos verificables. |
| Backend | Implementó los algoritmos y la simulación: validación del JSON, Union-Find, Kruskal, selección voraz de torres, Dijkstra, montículo binario propio, peligro y navegación reactiva, combate, puentes con cuadrilla, transporte terrestre y aéreo, presupuesto, reloj lógico y API REST. |
| Diseño visual | Rehízo los estilos web con una escala fluida basada en `clamp()` (tipografía, espacios, radios, rejillas, áreas táctiles), pulió ambas interfaces y añadió escala fluida a la ventana Pygame. |
| Frontend (React) | Rediseñó la interfaz web (paleta beige y negro, diseño responsive): vistas de inicio, grafos, plan y simulación, mapa SVG, paneles y bitácora. Añadió la sincronización con el cliente Pygame. |
| Cliente Pygame | Construyó la interfaz de escritorio que pide el enunciado (§13): cliente de la API, widgets, mapa 2D, cuatro pantallas, selector de archivos y arranque que inicia Flask. Añadió el endpoint `/scenario/status` para sincronizar clientes. |
| Pruebas | Escribió las 232 pruebas del backend y las 91 del cliente Pygame, y el comando `verificar.py`. Hizo pruebas de mutación y recorridos de la interfaz. |
| Documentación | Redactó la guía de ejecución y verificación, la guía de pruebas, la guía de exposición, el manual de usuario, el manual técnico, la distribución de tareas y este reporte. |

## 3. Qué decidieron las personas

Las decisiones de rumbo las tomaron los integrantes, dando instrucciones a la IA en cada sesión:

| Decisión | Quién |
|---|---|
| Hacer el proyecto "fácil de entender, manejar y exponer", que pareciera hecho por estudiantes, responsive, con paleta negro/beige y estilo moderno y didáctico | Integrante (petición inicial) |
| Probar punto por punto todo el enunciado y recibir una guía para repetirlo | Integrante |
| No hacer `commit` hasta indicarlo (se respetó; el `commit` se hizo cuando se pidió) | Integrante |
| Que la aplicación **arranque vacía** (sin escenario fijo) y que Dijkstra use una **cola de prioridad propia** en lugar de `heapq` | Integrante |
| Verificar de nuevo que todos los puntos estuvieran completos y generar los entregables | Integrante |
| Usar **Pygame** como interfaz (como pide el enunciado) y conservar Flask y React, de modo que los tres se complementen | Integrante (petición posterior) |
| Repartir las tareas entre Juan Sebastián Naranjo Verdugo y David Josué Solorza Viera, e incluir el uso de Pygame en los entregables | Integrante |

Reparto interno del trabajo y revisión del código por cada integrante: **[completar]**.

## 4. Cómo se verificó el trabajo de la IA

El código generado por una IA puede ser incorrecto aunque parezca razonable, así que no se aceptó sin comprobarlo:

1. **Pruebas automáticas (232 del backend y 91 de Pygame).** Una por sección del enunciado. Los algoritmos se comparan contra implementaciones
   independientes: Kruskal contra fuerza bruta (todos los conjuntos de V−1 aristas), Dijkstra contra la búsqueda de todas
   las rutas simples y contra Bellman-Ford en grafos aleatorios, el montículo contra `sorted`.
2. **Pruebas de mutación manuales.** Se rompieron a propósito reglas del código (orden de fin de partida, desgaste al caminar,
   recompensa duplicada, cuadrilla de reparación, medios no permitidos…) y se comprobó que al menos una prueba fallara.
   Las mutaciones que sobrevivieron al principio revelaron pruebas débiles y se reforzaron.
3. **Recorrido en la interfaz real.** Se cargaron escenarios válidos e inválidos, se compró, se movió, se hicieron colapsar
   puentes y se llegó a cada resultado final, comparando con valores calculados aparte (por ejemplo derrota a 23.0 s y
   victoria por eliminación a 14.25 s con $1750 en el escenario simple).
4. **Cliente Pygame sin ventana real.** Las 91 pruebas dibujan en una superficie en memoria (controlador de vídeo `dummy` de SDL), simulan
   clics, teclas y rueda del ratón, pulsan los botones por su nombre, comprueban píxeles y juegan partidas completas contra un
   servidor Flask real por HTTP. Además se revisaron capturas de cada pantalla. Se rompieron a propósito 19 reglas del código
   del cliente y las 19 fueron detectadas.
5. **Diseño fluido.** En el navegador se midió, de 320 a 1920 px y en las cuatro pestañas, que no hay desborde horizontal; que el cuerpo crece de 14.7 a 17 px; y que en móvil
   los controles miden 44 px. Se jugó una partida completa por la interfaz web rediseñada. `verificar.py` incluye la comprobación "Web fluida" y 16 pruebas de la escala de Pygame.
6. **Auditoría ejecutable y pruebas de propiedades.** `python auditar_enunciado.py` verifica 47 puntos del enunciado contra un servidor Flask real por HTTP; `test_fuzz_invariants.py` juega
   48 partidas aleatorias comprobando los invariantes (capacidad, dinero conservado, un soldado = una operación, rechazos sin efectos). Se rompieron reglas a propósito para comprobar que ambas
   detectan fallos. Un escaneo automático confirma que los comentarios del código están en inglés.
7. **Pygame, Flask y React a la vez.** Se operó una partida desde el cliente Pygame (por HTTP real) y se comprobó en el navegador
   que React mostraba el mismo escenario, plan, soldados, reloj y bitácora sin tocarlo.
8. **Reglas del proyecto automatizadas.** `python verificar.py` revisa que no haya librerías de grafos ni `heapq`, que cada
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
| En Pygame, el clic que abría el selector de archivos también elegía un archivo del diálogo recién abierto | Prueba del selector con muchos archivos | El clic se consume al abrir el diálogo. |
| En Pygame, el cartel de resultado dejaba seleccionar vértices del mapa que había debajo | Prueba del cartel final | El mapa ignora clics mientras el cartel está visible. |
| Tipografía de la ventana Pygame demasiado delgada (resolvía a Segoe UI Light), leyenda con un color invisible y textos solapados | Revisión de capturas | Fuentes regulares explícitas, borde en la leyenda y diseño ajustado. |
| El enunciado pide **calcular** el camino de menor costo entre entrada y salida y solo se comprobaba que existiera | Segunda auditoría frase por frase del PDF | Se calcula con Dijkstra al cargar el escenario y se muestra en Pygame y React. |
| El validador aceptaba candidatas sin radio de vigilancia (quedaban inservibles sin avisar) | Segunda auditoría del PDF | Cada candidata debe tener su `rv`. |
| Pygame no mostraba la lista de corredores vigilados | Segunda auditoría del PDF | Resumen y lista en el plan. |
| Un atributo nuevo de la interfaz (`show_route`) pisaba un método del mismo nombre | Pruebas del cliente Pygame | Renombrado a `show_initial_route`. |
| Mi primera auditoría ejecutable tenía fallos propios (orden de pasos, límite de 30 s por petición, un puente ya destruido en una consulta) y dos puntos que no podía detectar rompiendo el código | Mutaciones sobre la propia auditoría | Se corrigió el guion, se agregó un escenario de 3 torres y las pruebas del instante simultáneo. |
| En el rediseño, las negritas del héroe oscuro salían en tinta oscura y no se leían; los botones pequeños medían 30 px en móvil; el resplandor del mapa Pygame era una "media luna" dura | Revisión de capturas y medición en el navegador | Color propio para el héroe, mínimos táctiles de 44 px y resplandor en capas suaves. |
| Mi comprobación de "web fluida" nunca detectaba nada: un `\b` mal escapado dejó un carácter de control en la expresión regular | Mutación (añadir un `font-size: 14px` a propósito) | Corregida; ahora la mutación se detecta. |
| Un servidor de pruebas antiguo seguía escuchando el mismo puerto y devolvía datos viejos | Datos inconsistentes entre clientes | Se verificó en otros puertos y se hizo configurable el puerto de Vite (`VITE_PORT`, `VITE_BACKEND_URL`); la guía advierte de este caso. |

## 6. Limitaciones y riesgos que se declaran

- La IA propuso algunas **decisiones de diseño** donde el enunciado deja libertad (quién forma la cuadrilla, el significado
  de `max_uses`, el paso de 0.25 s). Están en la sección 7 del [manual técnico](manual_tecnico.md) para que cada integrante
  las pueda defender o cambiar.
- La interfaz Pygame se verificó sin ventana real (renderizado fuera de pantalla, clics simulados y capturas revisadas), no por una
  persona usándola en pantalla: los integrantes deben abrirla y recorrerla antes de la sustentación.
- En Pygame la escala fluida estira un lienzo lógico a la ventana; fuera del tamaño de diseño el texto puede verse ligeramente suave. El aspecto se revisó con capturas, no con una persona frente a la pantalla.
- Pygame y React se sincronizan por sondeo cada 1.5 s; un cambio en uno aparece en el otro con ese retraso.
- Las pruebas verifican el comportamiento descrito en el enunciado tal como se interpretó; una interpretación distinta
  del docente podría requerir ajustes.
- Los videos de explicación y de funcionamiento **no los produce la IA**: los deben grabar los integrantes.
- El historial de Git refleja los cambios hechos con asistencia de IA; cada commit incluye la línea `Co-Authored-By`
  con la herramienta. Los aportes individuales de cada integrante dependen de quién ejecutó y confirmó cada cambio.

## 7. Cómo asegurar que cada integrante domina lo entregado

La sustentación exige que cada integrante explique las estructuras, justifique decisiones y analice efectos. Recomendación
de estudio, en orden:

1. [`distribucion_tareas.md`](distribucion_tareas.md) — qué parte debe dominar cada uno.
2. [`guia_exposicion.md`](guia_exposicion.md) — estructuras, algoritmos, preguntas probables.
3. [`manual_tecnico.md`](manual_tecnico.md) — modelo de dominio, invariantes, complejidad y cliente Pygame (§12).
4. Ejecutar [`guia_ejecucion_y_verificacion.md`](guia_ejecucion_y_verificacion.md) y repetir los experimentos de
   "rómpelo tú" y de mutación de [`guia_pruebas.md`](guia_pruebas.md) §3 y §4 para ver cómo reaccionan el código y las pruebas.
5. Leer, en el código, `min_heap.py`, `disjoint_set.py`, `mst_service.py`, `tower_selector.py`, `router.py`, `bridges.py` y
   `desktop/tardo_ui/store.py` (cómo Pygame usa la API):
   son los archivos sobre los que más probablemente pedirán cambios en vivo.

## 8. Declaración

Los integrantes declaran que usaron una herramienta de IA generativa como se describe arriba, que revisaron y
comprendieron el código entregado y que se responsabilizan de su contenido.

**[completar: nombres, firmas o confirmación de cada integrante y fecha]**
