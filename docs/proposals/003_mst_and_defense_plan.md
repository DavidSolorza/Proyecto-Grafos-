# Technical Proposal: Minimum Spanning Tree (MST) & Greedy Tower Selection
**Document ID:** `PROP-003` | **Author:** Orchestrator & Staff Architect

---

## 1. Executive Summary & Objective
Implement the defensive planning phase specified in Section §4 of the project requirements:
1. **Custom Minimum Spanning Tree (MST):** Build tree $T_E$ over the connected component containing the base in $G_E$, using walk time (`time_walk`) as weight, without any external graph libraries.
2. **Greedy Tower Selection:** Iteratively select up to $K$ candidate positions maximizing:
   $$S(p) = \frac{C(p)}{1 + \frac{D_T(B, p)}{D_0}}$$
   where $C(p)$ is the uncovered corridor length within surveillance radius $R_v$, and $D_T(B, p)$ is the distance on $T_E$ from the Base $B$ to candidate $p$.
3. **Surveillance & Tower Constraints:** Corridors are monitored if the horizontal distance from $p$ to the corridor midpoint is $\le R_v$. Towers hold at most 3 soldiers.

---

## 2. Proposed Architecture & Modules

### A. Backend (`backend/src/features/elevated_graph/`):
- **`application/disjoint_set.py` (< 150 lines):** Custom Disjoint-Set / Union-Find data structure with path compression and rank.
- **`application/mst_service.py` (< 150 lines):** Custom Kruskal's algorithm on the base connected component of $G_E$. Returns tree edges and path distance $D_T(B, p)$ using BFS on tree $T_E$.
- **`application/tower_selector.py` (< 150 lines):** Computes corridor midpoints, tests $R_v$ coverage, calculates $S(p)$, and selects up to $K$ towers with tie-breaking rules.
- **`infrastructure/routes.py` (< 150 lines):**
  - `POST /api/defense/plan`: Runs MST and tower selection, returning selected towers, surveillance coverage, and $T_E$ edges.

### B. Frontend (`frontend/src/`):
- **`features/defense/DefensePanel.jsx` (< 150 lines):** Button to trigger and inspect defense planning, showing chosen towers and total corridor coverage.
- **`features/map/MapView.jsx` update (< 150 lines):** Renders $T_E$ tree edges in green and displays circular surveillance ranges ($R_v$) around candidate towers.

---

## 3. Impact & Governance
- 100% compliant with 150-line file limit and strict OOP.
- Zero dependencies on `networkx`.
- Integrates seamlessly with the light-mode UI.

