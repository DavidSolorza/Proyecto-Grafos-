"""ScenarioManager orchestrating domain models and graphs."""
from typing import Any
from src.features.scenario.domain.scenario import ScenarioMetadata
from src.features.elevated_graph.domain.entities import VertexE, EdgeE, PositionType
from src.features.elevated_graph.domain.graph_e import GraphE
from src.features.labyrinth.domain.entities import VertexM, CorridorM
from src.features.labyrinth.domain.graph_m import GraphM


def _opt_float(x):
    """JSON null (or a missing key) means 'not allowed'."""
    return None if x is None else float(x)


def _opt_int(x):
    return None if x is None else int(x)


class ScenarioManager:
    """Central domain manager coordinating GE, GM and scenario configs."""

    def __init__(self, metadata: ScenarioMetadata) -> None:
        self.metadata = metadata
        self.graph_e = GraphE()
        self.graph_m = GraphM()
        self.candidates_meta: list[dict[str, Any]] = []
        self.convoy_config: dict[str, int] = {}
        self.defenders_config: dict[str, dict[str, Any]] = {}
        self.helicopter_config: dict[str, float] = {}
        self.raw: dict[str, Any] = {}
        self.initial_route: dict | None = None   # cheapest entry -> exit route before any danger (section 3)

    def populate_graph_e(self, raw_vertices: list[dict], raw_edges: list[dict]) -> None:
        """Instantiate and populate GraphE domain objects."""
        for v in raw_vertices:
            self.graph_e.add_vertex(VertexE(
                id=v["id"],
                coords=tuple(v["coords"]),
                type=PositionType(v["type"]),
                z=float(v.get("z", 0.0)),
            ))
        for e in raw_edges:
            self.graph_e.add_edge(EdgeE(
                id=e["id"],
                u=e["u"],
                v=e["v"],
                time_walk=_opt_float(e.get("time_walk")),
                time_moto=_opt_float(e.get("time_moto")),
                bridge_max_hp=_opt_int(e.get("bridge_max_hp")),
                bridge_current_hp=_opt_int(e.get("bridge_current_hp", e.get("bridge_max_hp"))),
            ))

    def populate_graph_m(self, raw_vertices: list[dict], raw_edges: list[dict]) -> None:
        """Instantiate and populate GraphM domain objects."""
        for v in raw_vertices:
            self.graph_m.add_vertex(VertexM(
                id=v["id"],
                coords=tuple(v["coords"]),
                is_entry=bool(v.get("is_entry", False)),
                is_exit=bool(v.get("is_exit", False)),
            ))
        for c in raw_edges:
            self.graph_m.add_corridor(CorridorM(
                id=c["id"],
                u=c["u"],
                v=c["v"],
                length=float(c["length"]),
                speed_allowed=float(c["speed_allowed"]),
            ))

    def validate_initial_state(self) -> dict[str, bool]:
        """Validate scenario graph invariants."""
        base = self.graph_e.get_base_vertex()
        base_connected = bool(base and len(self.graph_e.get_connected_component(base.id)) > 0)
        has_exit_path = self.graph_m.verify_initial_path()
        return {
            "has_base": base is not None,
            "base_connected": base_connected,
            "labyrinth_path_exists": has_exit_path,
        }

