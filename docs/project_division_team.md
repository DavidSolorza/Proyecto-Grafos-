# 👥 Project Division & Responsibilities (2 Developers)
**Strategy:** Vertical Slicing — Both developers work on both Backend and Frontend.

---

## 🧑‍💻 Developer A: Defensive Infrastructure & Elevated Graph (GE)

### Backend (Python / Flask)
1. **Elevated Graph (GE) Engine:**
   - Entities: `VertexE`, `EdgeE`, `PositionType` (Base, Candidate, Transit, Heliport).
   - Dynamic bridges: HP degradation per motorcycle crossing, collapse, and timed reconstruction.
   - Ground & aerial transport: Pathfinding for foot/motorcycles, helicopter capacity and routing.
2. **Defense Planning & MST:**
   - Custom MST algorithm on the base connected component (using walk time as weight).
   - Greedy tower selection scoring algorithm:
     $$S(p) = \frac{C(p)}{1 + \frac{D_T(B,p)}{D_0}}$$
   - Tower management: Slot occupancy (max 3 soldiers), height modifier $R_{ef} = R_{base} \cdot (1 + \beta z)$.
3. **REST Endpoints (GE & Defenses):**
   - `GET /api/scenario/ge`: Return elevated graph nodes, edges, bridge states.
   - `POST /api/defense/plan`: Run MST and tower selection algorithm.
   - `POST /api/units/recruit`: Buy and position soldiers.
   - `POST /api/transport/dispatch`: Dispatch ground or aerial movements.

### Frontend (React - Light Mode)
1. **Elevated Graph Canvas / SVG:**
   - Visual rendering of vertices (Base, Candidates, Heliport) and edges/bridges.
   - Bridge visual indicators: Normal, Damaged, Collapsed/Reconstructing with countdown timers.
2. **Defenders & Towers Management Panel:**
   - UI for buying soldiers (Infantry, Sniper, Gunner) with budget checking.
   - Tower assignment modal and soldier relocation triggers.
3. **Defense Plan Visualizer:**
   - Toggle view for MST edges and surveillance radii ($R_v$) of candidate positions.

---

## 🧑‍💻 Developer B: Labyrinth Maze (GM), Convoy & Simulation

### Backend (Python / Flask)
1. **Labyrinth Graph (GM) Engine:**
   - Entities: `VertexM`, `CorridorM`, entry and exit verification.
   - Corridor weight formula incorporating active threat:
     $$w(e) = t(e) + \alpha \cdot P(e)$$
2. **Convoy Formation & Reactive Navigation:**
   - Convoy composition: Tanks, Trucks, Robot Soldiers with individual HP and rewards.
   - Reactive pathfinding: Recalculate shortest path at each intersection without backtracking loops.
3. **Simulation Clock & Combat Resolver:**
   - Discrete logical clock ($dt$ in seconds).
   - Spatial range intersection: Calculate active soldier attacks against enemy units.
   - Win/Loss condition evaluation:
     - Victory by Elimination (all machines destroyed).
     - Victory by Resistance (clock reaches 300s).
     - Defeat (at least one machine reaches exit).
4. **REST Endpoints (GM & Simulation):**
   - `GET /api/scenario/gm`: Return labyrinth nodes, corridors, and current danger weights.
   - `GET /api/simulation/state`: Real-time state of convoy, clock, budget, and game status.
   - `POST /api/simulation/tick`: Advance simulation by $dt$ seconds.
   - `POST /api/simulation/reset`: Reset simulation to initial scenario state.

### Frontend (React - Light Mode)
1. **Labyrinth Canvas / SVG Overlay:**
   - Visual rendering of corridors, entry/exit points, and current active convoy formation.
   - Danger heat map or indicator lines along corridors based on $w(e)$.
2. **Convoy Health & Threat Dashboard:**
   - Live status of each machine (HP bars, remaining armor, bounty rewards).
   - Real-time simulation log showing combat damage dealt per tick.
3. **Playback & Simulation Controls:**
   - Play, Pause, Step-by-Step ($dt$), Speed toggle (1x, 2x, 5x).
   - Final status banner (Victory / Defeat with cause).

---

## 🤝 Shared Core Responsibilities (Joint Integration)
- **Scenario Loader (`ScenarioManager`):** Parsing `escenario_general_p_tardo.json` and validating schema.
- **Combined Map View:** Spatial coordination aligning $G_E$ and $G_M$ on a single interactive view.
- **API Contracts:** Maintaining TypeScript interfaces and Flask schemas synchronized.

