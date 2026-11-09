# Technical Proposal: Initial Base Setup & Architecture
**Document ID:** `PROP-001` | **Author:** Orchestrator & Staff Architect

---

## 1. Executive Summary & Objective
Establish the foundational infrastructure for the "La derrota del dictador General P. Tardo" simulation system. The project is split into two cleanly decoupled layers:
- `backend/`: Python with Flask providing REST API endpoints, custom graph structures, and domain entities.
- `frontend/`: React application using light-mode aesthetics to visualize graphs, manage defenses, and control the simulation.

---

## 2. Directory Structure (Vertical Slicing & Separation)
```plaintext
proyecto-grafos/
├── docs/
│   ├── rules/                       # Team rules & strict governance contract
│   ├── proposals/                   # Architectural proposals & ADRs
│   └── project_division_team.md     # 2-developer balanced workload
├── backend/
│   ├── requirements.txt             # Minimal dependencies (Flask, Flask-CORS)
│   ├── run.py                       # App runner (< 150 lines)
│   └── src/
│       ├── core/                    # Config and global error handling
│       └── features/
│           ├── scenario/            # JSON loader and validation
│           ├── elevated_graph/      # GE entities and custom graph
│           ├── labyrinth/           # GM entities and corridor weights
│           └── simulation/          # Clock and state endpoints
└── frontend/
    ├── package.json                 # React + Vite scaffolding
    ├── src/
    │   ├── api/                     # REST client connecting to backend
    │   ├── components/              # Shared light-theme UI elements
    │   └── features/
    │       ├── map/                 # 2D graph viewer (Light theme)
    │       └── dashboard/           # Simulation and budget controls
    └── index.html
```

---

## 3. Core Architectural Decisions (ADR)
- **ADR-001: Zero External Graph Libraries:** Adjacency list representation implemented from scratch without `networkx`.
- **ADR-002: Client-Server API Decoupling:** Communication strictly over HTTP REST with JSON payloads.
- **ADR-003: Light Theme Palette:** Soft neutral backgrounds (`#F8FAFC`, `#FFFFFF`), distinct accents for human forces (blue/cyan) and enemy convoy (amber/red).
- **ADR-004: File Limit Enforcement:** All files kept strictly under 150 lines.

