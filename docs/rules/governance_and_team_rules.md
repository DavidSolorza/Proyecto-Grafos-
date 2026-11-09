# 🏛️ Team & Technical Governance Rules
**Version:** 2026.4.0 | **Project:** La Derrota del Dictador General P. Tardo

---

## 1. Golden Rules (Non-Negotiable)
1. **150-Line Limit:** No source file (`.py`, `.ts`, `.tsx`, `.js`, etc.) may exceed 150 lines. Decompose using SRP and modular design.
2. **Custom Graph Structures Only:** External graph libraries that compute MST, shortest paths, or graph traversals (e.g., `networkx`) are strictly prohibited. All graphs and algorithms must be custom-built.
3. **Architecture Decoupling:** Complete separation between Backend (Flask REST API) and Frontend (React).
4. **Light Mode Interface Only:** The UI must strictly use clean, light themes (whites, soft grays, high-contrast readable colors). Dark mode is prohibited.
5. **Pure REST Communication:** All client-server interactions must occur via JSON over HTTP endpoints.

---

## 2. Team Workflow & Git Standards
- **Branching Strategy:** 
  - `main`: Production-ready, stable releases.
  - `dev`: Staging and active integration.
  - `feature/[module-name]-[dev-name]`: Working branches.
- **Pull Requests (PR):**
  - Every PR requires review and approval from the other teammate.
  - Verify line count checks (< 150 lines per file) before merging.
- **Commit Conventions (English):**
  - `feat: add custom mst algorithm for elevated graph`
  - `fix: correct convoy danger weight calculation`
  - `test: add unit test for bridge durability`

---

## 3. Code Quality & Conventions
- **Backend (Python / Flask):**
  - Strong typing with `dataclasses` or Python type hints (`typing`).
  - Strict OOP: Domain entities, Application use-cases, and Infrastructure controllers.
  - Document all public methods with clear docstrings.
- **Frontend (React):**
  - Functional components with hooks and clean state management.
  - Atomic UI design, reusable graph canvas/SVG components.
  - Explicit states for Loading, Error, and Success.

