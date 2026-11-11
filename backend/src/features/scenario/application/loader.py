"""Scenario JSON loader and validator with domain integration."""
import json
from pathlib import Path
from typing import Any
from src.core.errors.handlers import AppError
from src.features.scenario.domain.scenario import ScenarioMetadata
from src.features.scenario.domain.scenario_manager import ScenarioManager
from src.features.scenario.application.validator import validate_scenario


class ScenarioLoader:
    """Loads and validates scenario files into a ScenarioManager."""

    @staticmethod
    def load_from_file(filepath: Path | str) -> ScenarioManager:
        """Read and parse a JSON scenario file into a ScenarioManager."""
        path = Path(filepath)
        if not path.exists():
            raise AppError(f"Scenario file not found: {path}", 404)

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_data: dict[str, Any] = json.load(f)
        except json.JSONDecodeError as exc:
            raise AppError(f"Invalid JSON format: {exc}", 400) from exc

        return ScenarioLoader.load_from_dict(raw_data)

    @staticmethod
    def load_from_dict(raw: dict[str, Any]) -> ScenarioManager:
        """Validate, then parse the raw dictionary into a ScenarioManager."""
        errors = validate_scenario(raw)
        if errors:
            shown = "; ".join(errors[:6]) + (f" (y {len(errors) - 6} más)" if len(errors) > 6 else "")
            raise AppError(f"Escenario inválido: {shown}", 400)
        meta = raw.get("metadata", {})
        metadata = ScenarioMetadata(
            title=meta.get("title", "Untitled Scenario"),
            d0=float(meta.get("D0", 50.0)),
            alpha=float(meta.get("alpha", 1.5)),
            beta=float(meta.get("beta", 0.2)),
            max_towers_k=int(meta.get("max_towers_K", 3)),
            initial_budget=int(meta.get("initial_budget", 2000)),
            bridge_repair_time=float(meta.get("bridge_repair_time", 30.0)),
            time_limit=float(meta.get("time_limit", 300.0)),
            bridge_repair_crew=int(meta.get("bridge_repair_crew", 0)),
        )

        manager = ScenarioManager(metadata)
        manager.raw = raw  # kept so a match can be restarted from clean data
        ge_data = raw.get("graph_e", {})
        manager.populate_graph_e(
            ge_data.get("vertices", []), ge_data.get("edges", [])
        )

        gm_data = raw.get("graph_m", {})
        manager.populate_graph_m(
            gm_data.get("vertices", []), gm_data.get("edges", [])
        )

        manager.candidates_meta = raw.get("candidates_meta", [])
        manager.convoy_config = raw.get("convoy", {})
        manager.defenders_config = raw.get("defenders_config", {})
        manager.helicopter_config = {
            "speed": 15.0, "cost": 200, "max_uses": 3,
            **raw.get("helicopter", {}),
        }

        return manager
