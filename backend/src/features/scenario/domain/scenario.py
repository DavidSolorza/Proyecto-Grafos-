"""Scenario domain representation."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScenarioMetadata:
    """Metadata parameters for the scenario."""
    title: str
    d0: float
    alpha: float
    beta: float
    max_towers_k: int
    initial_budget: int
    bridge_repair_time: float
    time_limit: float = 300.0
    bridge_repair_crew: int = 0      # people a repair keeps busy (0 = nobody needed)


@dataclass
class ScenarioData:
    """Parsed scenario data model."""
    metadata: ScenarioMetadata
    graph_e: dict[str, Any]
    graph_m: dict[str, Any]
    candidates_meta: list[dict[str, Any]]
    convoy: dict[str, int]
    defenders_config: dict[str, dict[str, Any]]

