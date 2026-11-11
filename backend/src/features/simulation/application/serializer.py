"""Turns the simulation into plain JSON for the frontend."""
from src.features.simulation.application.engine import Simulation


def simulation_to_dict(sim: Simulation) -> dict:
    """Full snapshot: clock, budget, convoy, soldiers, towers, bridges, operations, log."""
    w, cv = sim.world, sim.convoy
    weights = cv.refresh_weights()  # keeps danger values in sync with the defenders now
    return {
        "clock": round(w.clock, 2),
        "time_limit": w.manager.metadata.time_limit,
        "status": w.status.value,
        "end_reason": w.end_reason,
        "budget": {"available": w.budget.available, "reserved": w.budget.reserved,
                   "spent": w.budget.spent, "earned": w.budget.earned},
        "convoy": {
            "xy": cv.xy, "vertex": cv.vertex, "corridor": cv.corridor.id if cv.corridor else None,
            "from": cv.from_v, "to": cv.to_v, "decision": cv.decision,
            "enemies": [{"id": e.id, "type": e.type.value, "hp": e.hp, "max_hp": e.max_hp,
                         "reward": e.reward, "alive": e.alive} for e in w.enemies],
        },
        "soldiers": [{"id": s.id, "type": s.type.value, "status": s.status.value, "vertex": s.vertex,
                      "xy": s.xy, "damage": s.damage, "frequency": s.frequency,
                      "ref": w.effective_range(s) if s.vertex in w.towers else s.base_range}
                     for s in w.soldiers.values()],
        "towers": [{"vertex_id": t.vertex_id, "xy": t.xy, "z": t.z, "rv": t.rv,
                    "occupants": w.occupants(t.vertex_id), "reserved": w.reserved.get(t.vertex_id, 0),
                    "capacity": 3} for t in w.towers.values()],
        "bridges": [{"id": e.id, "hp": e.bridge_current_hp, "max_hp": e.bridge_max_hp,
                     "destroyed": e.is_destroyed, "repair_left": round(e.repair_timer, 1),
                     "crew": e.occupied_by_repair_units, "waiting_crew": e.id in sim.bridges.waiting}
                    for e in w.manager.graph_e.edges.values() if e.is_bridge],  # plain roads are not bridges
        "corridors": [{"id": c.id, "time": c.base_time, "danger": c.current_danger,
                       "weight": weights[c.id]} for c in w.manager.graph_m.corridors.values()],
        "transfers": [{"id": t.id, "soldiers": t.soldier_ids, "mode": t.mode, "dest": t.dest,
                       "status": t.status, "route": t.vertices} for t in sim.ground.transfers
                      if t.status != "DONE"],
        "flights": [{"id": f.id, "soldiers": f.aboard, "target": f.target, "xy": f.xy}
                    for f in sim.air.flights if f.status == "FLYING"],
        "helicopter": {"speed": sim.air.speed, "cost": sim.air.cost,
                       "uses_left": sim.air.max_uses - sim.air.uses},
        "defenders_config": w.manager.defenders_config,
        "events": w.events[-60:],
    }
