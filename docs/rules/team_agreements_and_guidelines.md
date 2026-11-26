# 📐 Acuerdos Técnicos y Lineamientos del Equipo
**Proyecto:** La Derrota del Dictador General P. Tardo  
**Objetivo:** Consolidar las decisiones de diseño, justificaciones académicas y puntos críticos para la sustentación.

---

## 1. Decisiones Técnicas Acordadas

### A. Arranque Vacío (Carga Dinámica Obligatoria)
- **Decisión:** La aplicación inicia sin ningún escenario precargado (`state = None`).
- **Justificación:** Sección 12 del PDF (*«se prohíben rutas de entrada fijas»*). En la sustentación, el docente evaluará con un JSON nuevo. La interfaz web o ventana exige cargar el archivo mediante el botón de selección.

### B. Reloj Lógico Discreto ($\Delta t = 0.25\,\text{s}$)
- **Decisión:** El motor avanza en pasos discretos de $0.25$ segundos.
- **Justificación:** Sincroniza exactamente las cadencias de ataque sin errores de redondeo:
  - Infantería: $1.0\text{ atk/s} \rightarrow$ cada $4\text{ ticks}$.
  - Francotirador: $0.5\text{ atk/s} \rightarrow$ cada $2\text{ ticks}$.
  - Artillero: $0.2\text{ atk/s} \rightarrow$ cada $5\text{ ticks}$.
- **Orden de resolución temporal obligatorio (Sección 11):**
  1. Ejecución de ataques y cálculo de daño.
  2. Verificación de presencia de máquinas vivas en la salida (derrota).
  3. Comprobación del límite de tiempo de 300 segundos (victoria por resistencia).

### C. Uso de `heapq` (Cola de Prioridad)
- **Decisión:** Se utiliza `heapq` como estructura auxiliar para el Min-Heap en Dijkstra / Prim.
- **Justificación Académica:** El enunciado prohíbe librerías que calculen directamente grafos (e.g., `networkx`). `heapq` es solo un contenedor de prioridad de complejidad $O(\log n)$. El algoritmo de relajación de aristas y búsqueda de rutas es 100% propio.

### D. Interfaz Gráfica: React + Flask vs. Pygame
- **Decisión:** La lógica de algoritmos reside en el Backend Python desacoplada de la interfaz.
- **Acción:** Consultar al profesor si aprueba la interfaz web (React API REST). Si exige Pygame, se proveerá un visualizador auxiliar en Python reutilizando el mismo motor de dominio.

---

## 2. Checklist Crítico para la Sustentación Individual

Cada integrante debe dominar y poder responder sobre:
1. **Representación de Grafos:** Demostrar cómo se implementó la lista de adyacencia propia tanto para $G_E$ como para $G_M$.
2. **Cálculo de Peligro y Rutas:** Explicar la fórmula $w(e) = t(e) + \alpha \cdot P(e)$ y cómo el convoy recalcula en cada intersección evitando retrocesos innecesarios.
3. **Complejidad Algorítmica:**
   - Dijkstra con Min-Heap: $O((V + E) \log V)$.
   - MST (Kruskal) con Union-Find: $O(E \log E)$.
   - BFS de conectividad y caminos: $O(V + E)$.
4. **Puentes Dinámicos:** Explicar el ciclo de desgaste por motocicletas, colapso temporal y reconstrucción tras tiempo parametrizado.

