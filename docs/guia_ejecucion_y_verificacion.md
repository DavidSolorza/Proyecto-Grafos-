# Cómo ejecutar el proyecto y comprobar que todo funciona

Esta guía tiene tres partes: **(A)** poner el proyecto a correr, **(B)** comprobarlo en 2 minutos con un solo
comando y **(C)** recorrerlo a mano en unos 15 minutos con los valores esperados. Para el detalle fino de cada
regla del enunciado, ver [`guia_pruebas.md`](guia_pruebas.md); para exponerlo, [`guia_exposicion.md`](guia_exposicion.md).

> Los comandos están escritos para **Windows (PowerShell)**; en Linux/macOS son los mismos cambiando `python` por
> `python3` si hace falta.

---

## A. Ejecutar el proyecto paso a paso

### A.1 Requisitos (se instalan una sola vez)

| Programa | Versión mínima | Cómo comprobar |
|---|---|---|
| Python | 3.10 | `python --version` |
| Node.js (incluye npm) | 18 | `node --version` |

Si un comando dice "no se reconoce", instala el programa desde su web oficial y **abre una terminal nueva**.

### A.2 Backend (terminal 1)

Desde la carpeta del proyecto (`Proyecto-Grafos-`):

```bash
cd backend
```

```bash
python -m pip install -r requirements-dev.txt
```

```bash
python run.py
```

Debe quedar corriendo y mostrar `Starting Flask API on http://0.0.0.0:5000` y `Running on http://127.0.0.1:5000`. **No cierres esta terminal.**
Comprobación rápida: abre <http://localhost:5000/api/health> en el navegador; debe decir `"status": "healthy"`.

### A.3 Frontend (terminal 2, otra ventana)

Desde la carpeta del proyecto:

```bash
cd frontend
```

```bash
npm install
```

```bash
npm run dev
```

Mostrará `Local: http://localhost:5173/`. **No cierres esta terminal.**

### A.4 Abrir la aplicación

Abre <http://localhost:5173>. Debes ver:

- Arriba a la derecha el punto verde **"Backend conectado"**.
- La pantalla **Inicio** con **"Sin escenario cargado"**: la aplicación **arranca vacía** a propósito (el enunciado
  prohíbe rutas de archivo fijas). Todo empieza cargando un JSON, ver C.1.

### A.5 Abrir la ventana Pygame (interfaz principal)

Con el backend ya corriendo (o sin él: Pygame lo inicia si no lo encuentra), en una **tercera terminal**, desde la carpeta
del proyecto:

```bash
python desktop/main.py
```

Se abre la ventana **"La derrota del dictador General P. Tardo"** con las mismas cuatro pestañas (Inicio, Los grafos, Plan de
defensa, Simulación), la insignia **Backend conectado** y la pantalla de Inicio vacía. Opciones:

| Comando | Qué hace |
|---|---|
| `python desktop/main.py` | Abre Pygame; reutiliza el backend si ya corre, o lo inicia por su cuenta. |
| `python desktop/main.py --web` | Además abre el cliente React (`npm run dev`, necesita `npm install` una vez). |
| `python desktop/main.py --url http://127.0.0.1:5055` | Se conecta a un backend en otro puerto. |

**Pygame y la web comparten la misma partida**: carga un escenario en una y míralo aparecer en la otra en un par de
segundos. Si necesitas instalar Pygame por separado: `python -m pip install -r desktop/requirements.txt`.

### A.6 Detenerlo

En cada terminal pulsa `Ctrl + C`; la ventana Pygame se cierra con su botón de cerrar. Para volver a empezar limpio basta con detener y volver a correr `python run.py`
(el estado vive en memoria).

### A.7 Si algo falla

| Síntoma | Causa probable | Solución |
|---|---|---|
| "Backend sin conexión" (punto rojo) | El backend no está corriendo o usa otro puerto | Mira la terminal 1; debe estar en el puerto **5000**. Reinicia `python run.py`. |
| `Address already in use` / puerto 5000 ocupado | Otra instancia del backend abierta | Cierra la otra terminal (o reinicia el equipo) y vuelve a correrlo. |
| `No module named flask` | No se instalaron dependencias | `python -m pip install -r requirements-dev.txt` dentro de `backend`. |
| `No module named pytest` | Faltan las dependencias de pruebas | El mismo comando de arriba. |
| `npm: command not found` | Node.js no está instalado | Instala Node 18+ y abre una terminal nueva. |
| La página queda en blanco | Falta `npm install` o el servidor de Vite no corre | Repite A.3 y recarga con `Ctrl + F5`. |
| Datos raros o cambios que "no se ven" (otro escenario, otro plan) | Quedó un servidor viejo escuchando el mismo puerto: en Windows dos procesos pueden compartir el 5000 y las peticiones se reparten entre ambos | Cierra **todas** las terminales con `python run.py` o `npm run dev` anteriores (o reinicia el equipo). Para probar sin tocar nada, usa otros puertos: `PORT=5055 python run.py`, `VITE_PORT=5188 VITE_BACKEND_URL=http://127.0.0.1:5055 npm run dev` y `python desktop/main.py --url http://127.0.0.1:5055`. |
| La ventana Pygame no abre (`No module named pygame`) | Falta Pygame | `python -m pip install -r requirements-dev.txt` dentro de `backend`. |
| Cambié el código del backend y no se nota | Se corre con `FLASK_DEBUG=false` (sin recarga automática) | Detén y vuelve a correr `python run.py`. |

---

## B. Verificación automática (2 minutos, sin navegador)

El enunciado exige que los algoritmos se verifiquen **sin interfaz gráfica**: las 232 pruebas del backend no abren ninguna
ventana. Las 91 pruebas de la interfaz Pygame tampoco abren una ventana real (usan un controlador de vídeo falso de SDL y
clics simulados). Con el backend preparado (A.2):

```bash
cd backend
```

```bash
python verificar.py
```

Resultado esperado: una línea ✔ por cada sección del enunciado (incluida la interfaz Pygame, §13) y, al final,

```
✔ Sin librerías de grafos ni heapq
✔ Todos los archivos tienen menos de 150 líneas
✔ 4 escenarios de ejemplo válidos
Suite del backend: 232 passed
✔ §13     Interfaz Pygame: mapa, plan, compra, transporte, rutas, puentes y resultado
          91 passed
RESULTADO: TODO CORRECTO
```

También ejecuta la **auditoría punto a punto** del enunciado (47 puntos contra un servidor real) y revisa que los comentarios del código
estén en inglés. Para ver la auditoría completa y guardar su informe:

```bash
python auditar_enunciado.py --informe ../docs/informe_auditoria.md
```

Si alguna línea sale con ✘ te dice cuál sección falla. Para ver las pruebas una por una:

```bash
python -m pytest tests -v
```

Para una sola sección (por ejemplo el combate):

```bash
python -m pytest tests/test_s5_combat.py -v
```

Para las pruebas de la interfaz Pygame:

```bash
cd ../desktop
```

```bash
python -m pytest tests -v
```

---

## C. Recorrido manual (≈15 minutos)

Marca cada paso. Los números esperados están verificados y son **los mismos en Pygame y en la web**: haz el recorrido en
Pygame (`python desktop/main.py`) y repite los pasos que quieras en el navegador. **Reinicia el backend antes de empezar**
para partir vacío. Los primeros pasos usan el escenario simple (`docs/escenario_general_p_tardo.json`).

En Pygame, los nombres de los botones son los mismos que en la web, salvo que "Iniciar/Pausar" no llevan símbolo y la
tecla `Espacio` también inicia o pausa. En el paso C.1, **Seleccionar archivo...** abre el selector de la propia ventana:
pulsa **Ejemplos del proyecto** y elige el archivo.

### C.1 Arranque vacío y carga del JSON (§12)

1. En **Inicio** dice **"Sin escenario cargado"**. Las pestañas *Los grafos*, *Plan de defensa* y *Simulación* muestran
   "Aún no hay un escenario cargado" con un botón para volver aquí.
2. En **Cargar escenario** → **Seleccionar archivo** → elige `docs/escenario_general_p_tardo.json`.
3. Aparece el resumen: presupuesto **$2000**, K = **3**, D₀ = **50 s**, α = **1.5**, β = **0.2**, reparar puente **30 s**,
   convoy de 1 tanque + 1 camión + 2 robots, y tres insignias verdes (una base, componente conexa, camino entrada → salida).
4. **Archivo inválido**: crea `malo.json` con el texto `esto no es json` y súbelo → mensaje rojo
   **"El archivo no es un JSON válido"** y el escenario activo no cambia.

### C.2 Los dos grafos (§3, §13)

Pestaña **Los grafos**: alterna *Ambas capas / Red elevada GE / Laberinto GM*. Con el escenario simple, la franja ocre y el texto muestran el
**camino inicial de menor costo**: `M_ENTRADA > M_N1 > M_N2 > M_SALIDA (t = 23 s)`. Haz clic en un vértice para ver su
id, tipo, altura y coordenadas. Debe verse GE (base cuadrada, candidatas rombo, helipuerto con **H**) y GM
(entrada ▶, salida ⚑).

### C.3 Plan de defensa: árbol y torres (§4)

Pestaña **Plan de defensa** → **Calcular plan**. Esperado: **2 torres (`V_C1`, `V_C2`), cobertura 100 %,
árbol mínimo de 4 aristas y 45 s**; puntuaciones `V_C1` = **53.57** y `V_C2` = **23.53**. Abre "Paso a paso" para ver
cada iteración de la selección voraz y, bajo la tabla de torres, **Corredores vigilados: 3 de 3 (115 de 115 u.)**.

### C.4 Derrota si no defiendes (§11)

Pestaña **Simulación**. Sin comprar nada pulsa **▶ Iniciar** (usa **5×** para ir rápido). A los **23.0 s**:
**Derrota: una máquina viva llegó a la salida**.

### C.5 Victoria por eliminación (§5, §7, §10, §11)

1. **↺ Reiniciar**. Compra **2 Francotiradores** (presupuesto baja a $1400).
2. Selecciona `S1` y `S2`, Destino `V_C1`, Medio **Moto** → **Enviar**.
3. **▶ Iniciar**. Llegan a los **8.0 s**, el primer disparo es a los **8.25 s** (no atacan al llegar) y la partida
   termina a los **14.25 s** con **Victoria por eliminación** y **$1750** disponibles.
4. En la **Bitácora** lees cada disparo, cada destrucción y la recompensa (una sola vez por máquina).

### C.6 Peligro y ruta del convoy (§6)

**Reiniciar**, compra **1 Francotirador**, mándalo a `V_C1` en moto y avanza 9 s con **+1 s**. En el panel **Convoy enemigo**
mira la tabla **"¿Por qué ese camino?"** y la tabla de corredores: `M_C1` muestra **t = 8.0, P = 133.3, w = 208.0**
(con dos francotiradores el peligro se duplica). En el mapa los corredores
cambian de arena a terracota según el peligro.

### C.7 Helicóptero y presupuesto (§9, §10)

1. **Reiniciar**, compra **4 Infanterías**, selecciona las cuatro, Destino `V_C1`, Medio **Helicóptero** → **Enviar**.
2. Inmediatamente: **$1400 disponible, $200 reservado**; los chips dicen *volando*.
3. Pulsa **+1 s** unas 3 veces: aterriza en `V_C1` (bajan **3**, queda 1), el excedente va a `V_C2` y baja ahí.
   Final: **V_C1 = 3/3, V_C2 = 1/3, reservado $0** y los $200 pasan a gastado.
4. Rechazos (no cambian nada): un quinto soldado, o presupuesto menor a $200.

### C.8 Torres llenas (§5, §11)

Intenta mandar un cuarto soldado a una torre con 3: error **"no tiene capacidad libre (ocupantes + reservas)"**.

### C.9 Torres no se reubican (§4, §10)

Con la partida ya iniciada, vuelve a **Plan de defensa** y pulsa **Recalcular plan** → error
**"El enfrentamiento ya inició: las torres no se pueden reubicar"**.

### C.10 Puentes que colapsan (§8) — `docs/escenario_puentes.json`

Sube el archivo, calcula el plan, ve a Simulación, compra **3 Infanterías**: `S1` a pie a `V_C1`; `S2` y `S3` en
moto a `V_C1`; **5×** + **Iniciar**. Esperado: `E_E1` pasa de 3/3 a **2/3** a los 5 s (la moto desgasta una vez,
aunque lleven dos), `E_E2` colapsa a los 8 s (**✕ 30 s**), `S1` queda **detenido** en `V_T1`, el puente se
reconstruye a los **38 s** y `S1` **reanuda solo**. Tabla completa en `guia_pruebas.md` §2.8.

### C.11 Reconstrucción que ocupa a N personas (§3, §8) — `docs/escenario_cuadrilla.json`

Sube el archivo (el resumen dice *Personas por reparación: 2*), calcula el plan (árbol **35 s**, 3 aristas; `V_H1`
queda inalcanzable a pie porque `E_E4` solo admite moto). En Simulación compra 3 Infanterías y manda `S1` a `V_C1`
en moto. Bitácora esperada: colapso a los **8.00 s**; a los **8.25 s** *"S2, S3 empiezan a reconstruir E_E2 y quedan
ocupados"* (sus chips dicen *reconstruyendo*); a los **38.00 s** el puente se reconstruye y quedan libres. Si
compras solo 1 Infantería, la obra **espera** ("✕ sin cuadrilla") y el puente no se arregla.

### C.12 Escenario complejo (§4, §6) — `docs/escenario_complejo.json`

Sube el archivo y calcula el plan: torres **`V_C4`** (S ≈ 73.85) y luego **`V_C3`** (≈ 16.34), cobertura **72.2 %**,
árbol de **7 aristas y 85 s**, y **`V_ISLA` inalcanzable** (aparece en la lista de excluidos: no puede ser torre).

### C.13 Rómpelo tú (§3, §12)

Copia un escenario, cambia **una** cosa y súbelo; debe salir un mensaje rojo claro y el escenario activo no cambia.
Ejemplos: un segundo vértice `"type": "BASE"`, `"D0": 0`, `"time_walk": 0`, una arista a un vértice inexistente.
Lista completa con los mensajes esperados en `guia_pruebas.md` §3.

### C.14 Pygame y la web a la vez (§13)

Abre la ventana Pygame y el navegador (`http://localhost:5173`) con el mismo backend. En Pygame carga el escenario simple,
calcula el plan, compra 2 Francotiradores y envíalos en moto a `V_C1`; avanza unos segundos. **Sin tocar el navegador**,
en un par de segundos debe mostrar el mismo escenario, el mismo plan y la misma partida (reloj, presupuesto, soldados en
`V_C1` y la bitácora). Lo contrario también funciona: lo que compres en la web aparece en Pygame.

### C.15 Diseño fluido y responsive (§13)

**Web:** abre las herramientas del navegador (`F12`) → modo dispositivo y prueba los anchos **320, 375, 768, 1024 y 1920 px** en las cuatro pestañas:
no debe haber barra de desplazamiento horizontal, el texto debe crecer suavemente (cuerpo de ~14.7 px a ~17 px), la barra superior se compacta en teléfono
(solo el punto de conexión) y, a partir de ~990 px, el mapa queda fijo a la izquierda mientras se recorren los paneles.

**Pygame:** arrastra el borde de la ventana: la interfaz se escala de 0.7× a 1.8× y siempre llena la ventana (mínimo 840 × 560).

**Anterior (solo web):**

Abre las herramientas del navegador (`F12`) → modo dispositivo → ancho **375 px**: sin scroll horizontal, las pestañas
se deslizan y los paneles pasan debajo del mapa.

---

## D. Qué pide el enunciado y dónde se comprueba

| Sección | Qué pide | Estado | Dónde |
|---|---|---|---|
| §2 | Estructuras propias, sin NetworkX, algoritmos verificables sin interfaz | ✔ Lista de adyacencia, Union-Find y montículo binario propios | B (`verificar.py`) |
| §3 | Grafos GE/GM con sus reglas (medios permitidos, puentes y calles, una base, entrada ≠ salida) | ✔ | C.1, C.2, C.11, C.13 |
| §4 | MST sobre la componente de la base, selección voraz `S(p)`, torres fijas | ✔ | C.3, C.9, C.12 |
| §5 | Soldados, `Ref = Rbase·(1+β·z)`, blancos, artillero de área | ✔ | C.5 |
| §6 | Convoy, peligro `D(q)`, `w(e)`, navegación reactiva | ✔ | C.6 |
| §7 | Traslado terrestre con validaciones sin efectos | ✔ | C.5, C.8, C.10 |
| §8 | Puentes: desgaste por moto, colapso, reconstrucción que ocupa N personas | ✔ | C.10, C.11 |
| §9 | Helicóptero, excedentes, reservas | ✔ | C.7 |
| §10 | Presupuesto disponible/reservado, nunca negativo | ✔ | C.5, C.7 |
| §11 | Reloj lógico (0.25 s), prioridades y condiciones de fin | ✔ | C.4, C.5 |
| §12 | JSON elegido desde la interfaz, sin rutas fijas | ✔ | C.1 |
| §13 | Interfaz Pygame con mapa 2D, cargar y validar, árbol y torres, comprar, transportar, rutas, puentes, resultado | ✔ **Pygame** (principal) + **React** (web), ambos sobre **Flask** y con la misma partida | todo C, en especial C.14 |
| §14 | Código en Git, manual de usuario y técnico, dos escenarios, videos | ✔ Código, escenarios (4), manual de usuario, manual técnico, reporte de uso de IA y [distribución de tareas](distribucion_tareas.md) (completa los campos **[completar]** del reporte). **Faltan los dos videos**, que deben grabar ambos integrantes. Haz `git commit` de tus cambios para que queden en el historial. | — |
