# 🛡️ La Derrota del Dictador General P. Tardo

Simulación defensiva y algorítmica para el segundo proyecto de Estructuras de Datos.

---

## 🏗️ Arquitectura del Proyecto

- **`backend/`**: Servidor en Python (Flask) implementando estructuras de grafos puras ($G_E$ y $G_M$) sin librerías externas (Zero NetworkX). Expone API REST con CORS.
- **`frontend/`**: Aplicación en React + Vite con paleta en tonos claros (Light Mode) para visualización e interacción 2D del terreno.
- **`docs/`**: Documentación técnica, reglas de gobernanza del equipo y división de trabajo para 2 personas.

---

## 🚀 Puesta en Marcha

### 1. Backend (Flask)
```bash
cd backend
python -m pip install -r requirements.txt
python run.py
```
El servidor arrancará en `http://localhost:5000`.

### 2. Frontend (React)
```bash
cd frontend
npm install
npm run dev
```
La aplicación estará disponible en `http://localhost:5173`.

---

## 👥 División de Tareas y Reglas
Consulta [`docs/project_division_team.md`](docs/project_division_team.md) y [`docs/rules/governance_and_team_rules.md`](docs/rules/governance_and_team_rules.md).
