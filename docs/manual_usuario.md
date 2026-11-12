# Manual de usuario

**"La derrota del dictador General P. Tardo" — simulador de defensa con grafos**

Este manual explica cómo usar el simulador (ventana **Pygame** o navegador **web**, que funcionan igual), pantalla por
pantalla, y cómo jugar una partida completa. No necesitas saber programar. Para instalar y ejecutar el programa, sigue
[`guia_ejecucion_y_verificacion.md`](guia_ejecucion_y_verificacion.md) (sección A). Para entender cómo está construido,
ver el [manual técnico](manual_tecnico.md).

---

## 1. ¿De qué trata?

Un **convoy de máquinas** (tanques, camiones y soldados robot) avanza por un laberinto hacia una salida. Tú diriges a
la **resistencia humana**, que se defiende desde una red elevada de caminos y puentes. Tu trabajo es:

1. **Planificar:** la aplicación propone dónde construir las torres.
2. **Reclutar:** compras soldados con un presupuesto limitado.
3. **Posicionar:** envías a los soldados a las torres a pie, en moto o en helicóptero.
4. **Resistir:** las torres disparan al convoy cuando pasa a su alcance.

Ganas si destruyes todas las máquinas o si aguantas 300 segundos sin que ninguna llegue a la salida. Pierdes si
una máquina viva llega a la salida.

Los dos mapas son **independientes**: el convoy camina por el laberinto (grafo **GM**) y tus soldados se mueven por la red
elevada (grafo **GE**). Solo se relacionan por la **distancia**: una torre dispara a las máquinas que quedan a su alcance.

## 2. Las dos interfaces y cómo abrirlas

El simulador tiene dos pantallas que muestran **la misma partida** (las dos hablan con el mismo servidor Flask):

| Interfaz | Cómo se abre | Para qué |
|---|---|---|
| **Pygame** (ventana de escritorio) | `python desktop/main.py` | Es la interfaz principal pedida por el enunciado. Si el servidor no está corriendo, el propio programa lo inicia. |
| **Web** (navegador) | Abre `http://localhost:5173` con el servidor y `npm run dev` corriendo | La misma aplicación en el navegador; sirve también para proyectar o vigilar la partida. |

Puedes usar **las dos a la vez**: lo que haces en una (cargar, comprar, enviar, avanzar el reloj) aparece en la otra en
menos de dos segundos. Para abrir las tres piezas con un solo comando: `python desktop/main.py --web`. Los pasos de
instalación están en [`guia_ejecucion_y_verificacion.md`](guia_ejecucion_y_verificacion.md) (sección A).

**Particularidades de la ventana Pygame**

- Se puede cambiar de tamaño libremente (mínimo 840 × 560): la interfaz se adapta y se escala sola, sin cortar ningún panel.
- **Seleccionar archivo...** abre un selector dentro de la ventana: haz clic en una carpeta para entrar, en `..` para subir
  y en un archivo `.json` para elegirlo. Los botones de arriba llevan a *Inicio*, a *Ejemplos del proyecto* y a las
  unidades de disco. **Cancelar** o la tecla `Esc` lo cierran.
- En *Simulación*, la tecla `Espacio` inicia o pausa el reloj. La rueda del ratón desplaza la bitácora y la lista de archivos.
- Bajo el mapa hay dos pestañas: **Bitácora** (qué ocurrió y por qué) y **Corredores** (tiempo, peligro y peso de cada
  corredor del laberinto).
- Haz clic en un vértice para ver sus datos; el aviso verde o rojo de abajo explica el resultado de cada operación.

## 3. Primer vistazo

La aplicación **arranca vacía**: no hay ningún escenario cargado hasta que tú elijas un archivo. Arriba a la derecha
verás un punto verde con **"Backend conectado"** (si está rojo, el servidor no está corriendo). La barra superior tiene
cuatro secciones:

| Sección | Para qué sirve |
|---|---|
| **01 Inicio** | Cargar el escenario y ver su resumen. |
| **02 Los grafos** | Ver los dos mapas y entender su estructura. |
| **03 Plan de defensa** | Calcular el árbol mínimo y las torres. |
| **04 Simulación** | Comprar, mover soldados y ver el combate. |

Si entras a una sección sin haber cargado un escenario, verás "Aún no hay un escenario cargado" y un botón para volver a Inicio.

## 4. Paso 1 — Cargar un escenario (Inicio)

1. En el cuadro **Cargar escenario**, pulsa **Seleccionar archivo** (en Pygame se abre el selector de la ventana; en la web,
   el del navegador) y elige un archivo `.json`.
2. Si es válido, verás un mensaje verde y el **resumen**: presupuesto, número máximo de torres (K), tiempo de referencia
   D₀, coeficientes α (peligro) y β (altura), tiempo de reparación de puentes, personas por reparación, composición del convoy y
   tres insignias de comprobación (una sola base, la base tiene componente conexa y existe camino entrada → salida).
3. Si el archivo tiene errores, verás un mensaje rojo que explica qué falló (por ejemplo "debe haber exactamente
   una BASE") y **el escenario anterior no cambia**.

Escenarios incluidos en la carpeta `docs/`:

| Archivo | Descripción |
|---|---|
| `escenario_general_p_tardo.json` | Simple y lineal. Ideal para aprender. |
| `escenario_complejo.json` | Ciclos, empates, una posición aislada y rutas alternativas en el laberinto. |
| `escenario_puentes.json` | Puentes frágiles que se destruyen rápido. |
| `escenario_cuadrilla.json` | La reconstrucción de puentes ocupa a 2 personas; incluye calles y un camino solo para motos. |

Puedes cargar otro escenario en cualquier momento: reemplaza el actual y reinicia el plan y la partida.
Para crear el tuyo, copia uno de estos archivos y modifícalo (el significado de cada campo está en el
[manual técnico](manual_tecnico.md), sección 4).

## 5. Paso 2 — Mirar los grafos (Los grafos)

Muestra los dos mapas en el mismo plano. Con los botones **Ambas capas / Red elevada GE / Laberinto GM** eliges
qué ver. Haz **clic en un vértice** para ver su identificador, tipo, altura y coordenadas.

**Cómo leer el mapa**

| Símbolo | Significa |
|---|---|
| Cuadrado claro | **Base** de la resistencia (de aquí salen los soldados). |
| Rombo | **Candidata** a torre. |
| Rombo dorado | **Torre elegida** por el plan. |
| Círculo con **H** | **Helipuerto**. |
| Punto gris | Posición de tránsito. |
| Líneas claras | Caminos y puentes de GE. Los puentes muestran su resistencia (por ejemplo `3/3`). |
| Líneas de terracota | Corredores del laberinto (GM). Se tiñen más rojos cuanto más peligrosos son. |
| ▶ verde / ⚑ rojo | **Entrada** y **salida** del laberinto. |

La franja **ocre** bajo los corredores es el **camino inicial de menor costo** de la entrada a la salida, calculado al cargar el
escenario (por ejemplo, `M_ENTRADA → M_N1 → M_N2 → M_SALIDA`, 23 s en el escenario simple). Se puede mostrar u ocultar con el botón
**Camino inicial** (Pygame) y su texto aparece también en el resumen de Inicio.

Hay también un recuadro desplegable que explica qué es la componente conexa de la base (las posiciones a las que se
puede llegar caminando desde la base: solo en ellas se pueden poner torres).

## 6. Paso 3 — Calcular el plan de defensa

En **Plan de defensa** pulsa **Calcular plan**. La aplicación ejecuta dos cosas:

1. **Árbol de expansión mínima (T_E):** la forma más barata, en tiempo a pie, de conectar todas las posiciones
   alcanzables desde la base.
2. **Elección de torres:** en cada ronda elige la candidata con mejor puntuación
   `S(p) = C(p) / (1 + D_T(B,p) / D₀)`, que premia vigilar mucho corredor nuevo y penaliza estar lejos de la base por el árbol.
   Se detiene al llegar a K torres o cuando ninguna candidata vigila corredores nuevos.

Verás:

- Los botones **Árbol T_E** y **Radios R_v** para mostrar u ocultar el árbol (en verde) y el radio de vigilancia de cada torre.
- La **tabla de torres** con su puntuación, la **cobertura total** (porcentaje del laberinto vigilado) y la lista
  de posiciones inalcanzables (que no pueden ser torres).
- La lista de **corredores vigilados** (cuántos son, qué longitud cubren y cuáles) y, en cada iteración del paso a paso, los corredores
  que pasan a estar vigilados.
- El **"Paso a paso de la selección voraz"**: las puntuaciones de cada candidata en cada ronda, para entender por qué ganó una.

Una vez iniciado el combate, **las torres ya no se pueden cambiar**: si intentas recalcular el plan verás el mensaje
"El enfrentamiento ya inició: las torres no se pueden reubicar".

Cuando estés conforme, pulsa **Ir a la simulación →**.

## 7. Paso 4 — La simulación

La pantalla tiene el **mapa** a la izquierda y los **paneles** a la derecha (en el celular, los paneles quedan debajo del mapa).

### 7.1 Controles del reloj

| Botón | Qué hace |
|---|---|
| **Iniciar / Pausar** (en la web con ▶ y ❚❚; en Pygame también la tecla `Espacio`) | Corre o detiene el tiempo. Al iniciar, el combate comienza y las torres quedan fijas. |
| **+1 s** | Avanza exactamente un segundo (solo con el reloj detenido). |
| **1× / 2× / 5×** | Velocidad de la simulación. |
| **↺ Reiniciar** | Empieza una partida nueva con el mismo plan (puentes reparados, presupuesto inicial). |

El tiempo se mide en **segundos lógicos** (pasos de 0.25 s) y no depende de la velocidad de tu computador.
Arriba aparecen el estado (Listo, En combate, Victoria o Derrota), el reloj (`12.0s / 300s`) y una barra de progreso hacia el límite de tiempo.

### 7.2 Presupuesto y compra de soldados

El panel **Presupuesto** muestra el dinero **disponible**, el **reservado** (vuelos de helicóptero autorizados que aún no
terminan) y el **gastado**. Pulsa uno de los tres botones para comprar:

| Soldado | Costo | Daño | Alcance base | Frecuencia |
|---|---|---|---|---|
| Infantería | $100 | 10 | 5 | 1 ataque/s |
| Francotirador | $300 | 50 | 20 | 0,5 ataques/s |
| Artillero | $500 | 100 | 15 | 0,2 ataques/s |

(Valores del escenario simple; cada escenario puede cambiarlos.) Los soldados comprados **aparecen en la base**.
Nunca puedes quedar con saldo negativo: si no alcanza, el botón se desactiva o verás un mensaje. Cada máquina
destruida te da una **recompensa** (tanque $150, camión $100, robot $50).

Los soldados en una torre alcanzan más lejos cuanto más alta es la torre: `alcance = base × (1 + β × altura)`.

### 7.3 Mover soldados (panel "Soldados y transporte")

1. Haz clic en uno o más **chips de soldado** para seleccionarlos (`S1 INF · en base V_BASE`).
2. Elige el **Destino** (una torre del plan o la base) y el **Medio**:

| Medio | Capacidad | Costo | Notas |
|---|---|---|---|
| A pie | 1 soldado | Gratis | No desgasta los puentes. |
| Moto | 1 o 2 soldados | Gratis | Más rápida, pero **cada moto que termina de cruzar un puente le quita 1 de resistencia**. |
| Helicóptero | Hasta 4 | Costo fijo por vuelo | Vuela en línea recta; reparte a los sobrantes en otras torres o los devuelve a la base. |

3. **Ver ruta** muestra el camino más rápido y su tiempo sin mover a nadie. **Enviar** da la orden.

**Reglas que debes conocer**

- Cada torre admite **3 soldados como máximo**, contando a los que ya están y a los que van en camino.
- Un soldado **en tránsito no ataca**. Empieza a disparar en el instante siguiente a su llegada.
- Si una orden no es válida (torre llena, ruta inexistente, soldado ocupado, dinero insuficiente), verás un mensaje rojo y
  **no cambia nada**.
- Los chips de soldados en camino, volando o reconstruyendo un puente están desactivados: no reciben órdenes.
- Hay un número máximo de vuelos (se muestra como `helicópteros: n · $costo`).

### 7.4 Puentes

Cada puente muestra su resistencia en el mapa (`3/3`). Cuando llega a cero se **destruye**: aparece `✕` con una cuenta
regresiva y nadie puede iniciar un cruce nuevo (los que ya estaban cruzando terminan). Después del tiempo de
reconstrucción, el puente recupera su resistencia y vuelve a funcionar.

- Si un soldado en camino se queda sin ruta, **se detiene** y reanuda solo cuando el puente se reconstruye.
- En escenarios con "personas por reparación", la obra necesita esa cantidad de soldados **en la base**; mientras
  trabajan aparecen como **reconstruyendo** y no pueden atacar ni moverse. Si no hay suficientes, el mapa dice
  **✕ sin cuadrilla** y la obra espera.
- Las **calles** (sin número) nunca se destruyen.

### 7.5 El convoy y el peligro

El panel **Convoy enemigo** lista cada máquina con su vida. El convoy avanza como una sola formación y, en
**cada intersección**, calcula un costo para cada corredor: `tiempo + α × daño esperado`. Elige el de menor costo, de modo
que **rodea las zonas peligrosas** si hay un camino alternativo razonable. La tabla **"¿Por qué ese camino?"** muestra las
opciones y el costo de cada una, y la tabla de corredores muestra su tiempo, su peligro y su peso.

### 7.6 La bitácora

Registra cada hecho con su tiempo y su explicación: compras, salidas y llegadas de soldados, disparos y destrucciones,
colapsos y reconstrucciones de puentes, vuelos, decisiones del convoy y el resultado final. Si algo ocurre en el
mapa y no sabes por qué, búscalo allí.

### 7.7 Fin de la partida

| Resultado | Cuándo ocurre |
|---|---|
| **Victoria por eliminación** | Todas las máquinas fueron destruidas. |
| **Derrota** | Al menos una máquina viva llega a la salida. |
| **Victoria por resistencia** | Se alcanza el límite de tiempo (300 s por defecto) sin que llegue ninguna. |

Si varias cosas ocurren en el mismo instante, se resuelven en ese orden: primero los ataques, luego la llegada a la
salida y por último el tiempo. Al terminar, el reloj se detiene y aparece un cartel con **Jugar de nuevo** y **Ver
mapa** (para mirar el estado final).

## 8. Una partida de ejemplo (escenario simple)

1. Inicio → carga `escenario_general_p_tardo.json`.
2. Plan de defensa → **Calcular plan** (dos torres: `V_C1` y `V_C2`, 100 % de cobertura).
3. Simulación → compra **2 Francotiradores** ($600; quedan $1400).
4. Selecciona `S1` y `S2`, destino `V_C1`, medio **Moto**, **Enviar**.
5. **Iniciar**. A los 8 s llegan; a los 8.25 s empiezan a disparar. A los **14.25 s** ganas por eliminación
   con $1750 disponibles.

Si no compras nada, el convoy llega a la salida a los **23 s** y pierdes: la derrota también se puede probar.

## 9. Mensajes frecuentes

| Mensaje | Qué significa y qué hacer |
|---|---|
| "Primero carga un escenario JSON" | Aún no hay escenario: ve a Inicio y sube un archivo. |
| "El archivo no es un JSON válido" | El texto no tiene formato JSON; revisa comas, llaves y comillas. |
| "Escenario inválido: …" | El archivo rompe una regla del escenario; el mensaje indica cuál. |
| "Primero calcula el plan de defensa" | La simulación necesita las torres: ve a Plan de defensa. |
| "El enfrentamiento ya inició: las torres no se pueden reubicar" | Ya empezó el combate; pulsa **Reiniciar** para otra partida. |
| "Presupuesto insuficiente…" | No alcanza el dinero para esa compra o ese vuelo. |
| "A pie va 1 soldado; en moto pueden ir 1 o 2" | Elegiste demasiados soldados para ese medio. |
| "La torre … no tiene capacidad libre" | La torre ya tiene 3 soldados entre presentes y reservados. |
| "No existe una ruta válida" | Un puente destruido o una conexión inexistente impide llegar. |
| "Algún soldado está ocupado…" | Ese soldado va en camino, vuela o reconstruye un puente. |
| "No quedan usos de helicóptero" | Ya agotaste los vuelos permitidos. |

## 10. Preguntas frecuentes

- **¿Se guarda mi partida?** No. El estado vive en la memoria del servidor; si lo reinicias, vuelves a empezar vacío.
- **¿Puedo reubicar una torre?** Solo recalculando el plan **antes** de iniciar el combate.
- **¿Por qué mis soldados no disparan?** Revisa que estén **en una torre** (no en camino) y que el convoy esté a su alcance
  efectivo; la bitácora dice cuándo llegaron.
- **¿Por qué el convoy cambió de camino?** Porque un corredor se volvió más peligroso; mira "¿Por qué ese camino?".
- **¿Puedo usar Pygame y la web al mismo tiempo?** Sí. Comparten la partida: lo que hagas en una aparece en la otra en
  menos de dos segundos. Avanza el reloj desde una sola de las dos: si lo inicias en ambas a la vez, las dos avanzan la misma partida y el tiempo correría el doble de rápido.
- **¿Funciona en el celular?** Sí. La web se adapta a cualquier ancho (de 320 px a pantallas grandes): el texto, los espacios y los botones
  crecen o se reducen de forma fluida, con paneles apilados debajo del mapa en pantallas pequeñas y botones de al menos 44 px en pantallas táctiles.
