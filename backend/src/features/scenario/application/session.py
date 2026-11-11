"""In-memory session: the active scenario, its defense plan and the running simulation."""
from typing import Optional
from src.core.errors.handlers import AppError
from src.features.elevated_graph.application.defense_planner import plan_defense
from src.features.scenario.application.loader import ScenarioLoader
from src.features.scenario.domain.scenario_manager import ScenarioManager
from src.features.simulation.application.engine import Simulation


class Session:
    """Single-user state shared by the REST routes."""

    def __init__(self) -> None:
        self._manager: Optional[ScenarioManager] = None
        self.plan: Optional[dict] = None
        self.simulation: Optional[Simulation] = None

    @property
    def has_scenario(self) -> bool:
        return self._manager is not None

    @property
    def manager(self) -> ScenarioManager:
        """The app starts empty: nothing works until the user uploads a JSON (requirement §12)."""
        if self._manager is None:
            raise AppError("Primero carga un escenario JSON", 409)
        return self._manager

    def load(self, manager: ScenarioManager) -> None:
        """A new scenario replaces everything that depended on the old one."""
        self._manager, self.plan, self.simulation = manager, None, None

    def calculate_plan(self) -> dict:
        """Towers cannot change after the fight starts, so planning is blocked then."""
        sim = self.simulation
        if sim is not None and sim.world.clock > 0:
            raise AppError("El enfrentamiento ya inició: las torres no se pueden reubicar", 409)
        self.plan = plan_defense(self.manager)
        self.simulation = None  # a new plan needs a new match
        return self.plan

    def new_simulation(self) -> Simulation:
        """Start a fresh match from the current plan (the scenario file is reloaded)."""
        if self.plan is None:
            raise AppError("Primero calcula el plan de defensa", 409)
        self.manager_reset()
        self.simulation = Simulation(self.manager, self.plan)
        return self.simulation

    def manager_reset(self) -> None:
        """Rebuild graphs from the raw data so destroyed bridges and weights start clean."""
        raw = self.manager.raw
        self._manager = ScenarioLoader.load_from_dict(raw)

    def require_simulation(self) -> Simulation:
        if self.simulation is None:
            raise AppError("Primero crea la simulación (plan + reiniciar)", 409)
        return self.simulation


session = Session()
