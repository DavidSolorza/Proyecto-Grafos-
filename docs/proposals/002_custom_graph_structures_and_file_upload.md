# Technical Proposal: Custom Graph Structures & Dynamic Scenario Loading
**Document ID:** `PROP-002` | **Author:** Orchestrator & Staff Architect

---

## 1. Objective & Scope
Implement the pure custom graph data structures (zero `networkx`) for both $G_E$ (Elevated Graph) and $G_M$ (Labyrinth Graph), complying with:
- PDF Requirement §3: Custom representation with adjacency lists, component reachability, and validation.
- PDF Requirement §12: Dynamic JSON scenario loading from UI (no hardcoded file paths).
- Governance rules: Strict OOP, Vertical Slicing, < 150 lines per file.

---

## 2. Proposed Architecture & Components

### A. Backend (`backend/src/features/`):
1. **`elevated_graph/domain/graph_e.py` (< 150 lines):**
   - Pure OOP `GraphE` managing `vertices: dict[str, VertexE]` and `edges: dict[str, EdgeE]`.
   - Adjacency list representation using native Python dict/sets.
   - Custom BFS traversal for `get_connected_component(start_id: str) -> set[str]`.
2. **`labyrinth/domain/graph_m.py` (< 150 lines):**
   - Pure OOP `GraphM` managing `vertices: dict[str, VertexM]` and `corridors: dict[str, CorridorM]`.
   - `verify_initial_path() -> bool` using custom BFS/Dijkstra to ensure valid passage between `is_entry` and `is_exit`.
3. **`scenario/infrastructure/routes.py` update (< 150 lines):**
   - `POST /api/scenario/upload`: Accepts a JSON file or JSON payload from the user and validates initial states.
   - `GET /api/scenario/ge`: Returns elevated graph topology and bridge health.
   - `GET /api/scenario/gm`: Returns labyrinth corridors, entry, exit, and base times.

### B. Frontend (`frontend/src/`):
1. **`components/FileUploader.jsx` (< 150 lines):**
   - Light-themed drag & drop or file input allowing the user to select any `.json` scenario dynamically.
2. **`features/map/MapView.jsx` enhancement (< 150 lines):**
   - Interactive layer toggles (Show $G_E$, Show $G_M$, Show Combined).
   - Display node properties on hover/click (coordinates, types, heights $z$).

---

## 3. Impact & Verification
- Validates the initial state of the scenario directly on upload.
- Ensures total independence from external graph libraries.
- Ready for Dev A (MST & Towers) and Dev B (Convoy Dijkstra & Simulation).

