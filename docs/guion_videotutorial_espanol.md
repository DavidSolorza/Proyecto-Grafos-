# GUION DEL VIDEOTUTORIAL: SISTEMA EN FUNCIONAMIENTO
## "La Derrota del Dictador General P. Tardo"
**Formato:** Video Demostrativo / Tutorial en Pantalla  
**Idioma:** Español  
**Duración Estimada:** 8 a 10 minutos  
**Participantes:** Todos los integrantes del equipo  

---

## 🎯 OBJETIVO DEL VIDEO
Demostrar el funcionamiento completo del simulador desarrollado para el segundo proyecto de Estructuras de Datos, mostrando tanto la interfaz gráfica nativa en **Pygame** como la interfaz interactiva en **React**, evidenciando el cumplimiento estricto de todas las reglas del enunciado oficial: carga dinámica de escenarios, cálculo de árbol mínimo ($T_E$), selección voraz de torres, despliegue táctico, desgaste de puentes y condiciones de victoria/derrota.

---

## 🎬 ESCALETA Y ESTRUCTURA TEMPORAL

```
00:00 - 01:15  |  Sección 1: Introducción y Arquitectura Desacoplada
01:15 - 02:45  |  Sección 2: Carga Dinámica de Escenarios y Validación Previa
02:45 - 04:30  |  Sección 3: Fase 1 - Árbol de Expansión Mínima (MST) y Selección Voraz
04:30 - 06:45  |  Sección 4: Fase 2 - Simulación en Vivo, Combate y Movilidad
06:45 - 08:30  |  Sección 5: Dinámica de Puentes, Cuadrillas y Helicóptero con Excedentes
08:30 - 10:00  |  Sección 6: Resolución de Fin de Partida y Conclusión
```

---

## 🎙️ GUION DETALLADO PASO A PASO

### SECCIÓN 1: INTRODUCCIÓN Y ARQUITECTURA (00:00 - 01:15)
- **Visual en pantalla:** Plano general del proyecto, terminal ejecutando `python desktop/main.py` y navegador con `http://localhost:5173`.
- **Voz en off / Presentador 1:**
  > *"Hola a todos y bienvenidos a la presentación del sistema 'La derrota del dictador General P. Tardo', desarrollado para la asignatura de Estructuras de Datos en la Universidad de Caldas.*  
  > *El núcleo de nuestro proyecto está concebido bajo una separación estricta: un motor backend en Python con estructuras de datos desarrolladas enteramente por nosotros —sin librerías externas de grafos como NetworkX ni colas como heapq— y dos clientes gráficos independientes: una aplicación de escritorio nativa en Pygame con renderizado vectorial procedural y un cliente web táctico en React.*  
  > *Veamos a continuación el flujo completo paso a paso."*

---

### SECCIÓN 2: CARGA DINÁMICA DE ESCENARIOS (01:15 - 02:45)
- **Visual en pantalla:** Ventana de Pygame arrancando vacía. El cursor hace clic en "Seleccionar archivo". Se abre la ventana nativa de Tkinter `filedialog.askopenfilename`. Se selecciona `docs/escenario_gran_ciudadela.json`.
- **Voz en off / Presentador 2:**
  > *"Cumpliendo con la Sección 12 del enunciado, la aplicación arranca completamente vacía: no existen rutas de archivo fijas o quemadas en el código.*  
  > *Al hacer clic en el botón 'Seleccionar archivo', invocamos el selector nativo del sistema operativo. Vamos a cargar nuestro escenario más desafiante: 'La Gran Fortaleza de la Ciudadela', compuesto por 12 vértices en la red elevada y 10 en el laberinto.*  
  > *Inmediatamente, el motor de validación comprueba la existencia de exactamente una base, coordenadas positivas, conexidad y que exista un camino inicial factible de entrada a salida antes de admitir el escenario en memoria."*

---

### SECCIÓN 3: FASE 1 - MST Y SELECCIÓN VORAZ DE TORRES (02:45 - 04:30)
- **Visual en pantalla:** Navegación a la pestaña "Plan de defensa". Clic en "Calcular plan". Se iluminan las aristas del árbol $T_E$ en cian. Se proyectan los radios de vigilancia $R_v$.
- **Voz en off / Presentador 3:**
  > *"Nos encontramos en la Fase 1, previa al combate. Al presionar 'Calcular plan', entran en acción dos algoritmos fundamentales:*  
  > *Primero, nuestro algoritmo de Kruskal con Union-Find propio —implementando compresión de caminos y unión por rango— construye el Árbol de Expansión Mínima $T_E$ sobre la componente conexa de la base utilizando el tiempo a pie como peso.*  
  > *Segundo, un algoritmo voraz evalúa cada candidato con la fórmula oficial:*  
  > $$S(p) = \frac{C(p)}{1 + \frac{D_T(B, p)}{D_0}}$$  
  > *Donde $C(p)$ es la longitud de corredores aún sin vigilar cubiertos por el radio $R_v$, y $D_T$ es la distancia a pie siguiendo estrictamente el árbol $T_E$.*  
  > *La tabla lateral detalla cada iteración y el orden lexicográfico ante empates. Las torres seleccionadas quedan fijas para el resto de la partida."*

---

### SECCIÓN 4: FASE 2 - COMBATE Y NAVEGACIÓN REACTIVA (04:30 - 06:45)
- **Visual en pantalla:** Transición a la pestaña "Simulación". Clic en "Crear simulación" y luego inicio del reloj. Reclutamiento de Infantería ($100), Francotirador ($300) y Artillero ($500). El convoy avanza por el laberinto.
- **Voz en off / Presentador 4:**
  > *"Iniciamos la Fase 2: el combate en tiempo lógico coordinado en intervalos de 0.25 segundos.*  
  > *En el panel de mando compramos soldados. Noten los 3 slots circulares debajo de cada torre elegida: reflejan exactamente la capacidad máxima de 3 tropas permitida por la Sección 5.*  
  > *Cuando el convoy entra en rango, se ejecuta el cálculo de alcance efectivo balístico:*  
  > $$R_{\text{ef}} = R_{\text{base}} \cdot (1 + \beta \cdot z)$$  
  > *Los francotiradores atacan con prioridad a la máquina viva de menor HP, mientras que el artillero aplica daño de área a todas las unidades a su alcance.*  
  > *Miren cómo en cada intersección el convoy recalcula su ruta con Dijkstra según el peligro ponderado:*  
  > $$w(e) = t(e) + \alpha \cdot P(e)$$  
  > *La bitácora inferior nos explica en tiempo real por qué el convoy desvía su trayectoria para esquivar a nuestras tropas."*

---

### SECCIÓN 5: PUENTES DINÁMICOS Y HELICÓPTERO (06:45 - 08:30)
- **Visual en pantalla:** Despacho de 2 soldados en motocicleta por un puente. El puente reduce su HP de 3 a 2, luego a 0. Colapso en rojo punteado con contador de reconstrucción. Despacho de helicóptero con 4 soldados hacia una torre llena; redistribución automática.
- **Voz en off / Presentador 1:**
  > *"Veamos la infraestructura dinámica: enviamos dos soldados en motocicleta a través de un puente.*  
  > *Como lo estipula la Sección 8, cada motocicleta que cruza descuenta exactamente 1 punto de resistencia. Al llegar a cero, el puente colapsa, impidiendo nuevos cruces y mostrando la cuenta regresiva de la cuadrilla de reparación.*  
  > *Simultáneamente, probamos el helicóptero de la Sección 9: despachamos 4 soldados. Como la torre de destino se llena, el algoritmo de distribución de excedentes busca de inmediato la siguiente torre más cercana por distancia euclidiana, garantizando que ninguna tropa quede desamparada ni sobreocupe una torre."*

---

### SECCIÓN 6: FINALIZACIÓN Y CONCLUSIÓN (08:30 - 10:00)
- **Visual en pantalla:** Se destruye la última máquina del convoy. Aparece el modal de fin de partida: "Victoria por eliminación". Se muestran indicadores: tiempo transcurrido, dinero ganado y balance final.
- **Voz en off / Presentador 2:**
  > *"Al caer la última máquina enemiga, el reloj se detiene y se activa la primera condición de victoria: 'Victoria por eliminación'. En caso de resistencia prolongada a los 300 segundos, se otorgaría la victoria por resistencia, mientras que si una máquina alcanza la salida, el desenlace es la derrota.*  
  > *Todas las transacciones respetaron la invariante de presupuesto positivo, los grafos demostraron su reactividad y las interfaces gráfica y algorítmica operaron en perfecta armonía.*  
  > *Con esto demostramos el 100% de cumplimiento de los requisitos exigidos. Muchas gracias por su atención."*
