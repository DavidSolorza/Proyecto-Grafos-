"""Sections 5, 7-11: random orders over long matches; the statement's invariants must hold after every operation."""
import random
from collections import Counter

import pytest

from conftest import load, slow_convoy
from src.core.errors.handlers import AppError
from src.features.elevated_graph.application.defense_planner import plan_defense
from src.features.simulation.application.engine import Simulation
from src.features.simulation.domain.units import SoldierStatus as St
from src.features.simulation.domain.world import STEP, TOWER_CAPACITY

SCENARIOS = ["escenario_general_p_tardo.json", "escenario_complejo.json", "escenario_puentes.json", "escenario_cuadrilla.json"]


def exclusive_groups(sim):
    """Soldiers that are in each kind of operation right now."""
    moving = Counter(s for t in sim.ground.transfers if t.status != "DONE" for s in t.soldier_ids)
    flying = Counter(s for f in sim.air.flights if f.status == "FLYING" for s in f.aboard)
    crews = Counter(s for crew in sim.bridges.crews.values() for s in crew)
    return moving, flying, crews


def check(sim, initial_budget):
    w, b = sim.world, sim.world.budget
    assert round(w.clock / STEP) * STEP == pytest.approx(w.clock)                      # the clock only moves in steps
    assert b.available >= -1e-9 and b.reserved >= -1e-9 and b.spent >= 0                # never a negative balance
    assert initial_budget + b.earned == pytest.approx(b.available + b.reserved + b.spent)   # money is conserved
    assert b.earned == sum(e.reward for e in w.enemies if not e.alive)                  # one reward per destroyed machine
    assert all(0 <= e.hp <= e.max_hp for e in w.enemies)
    moving, flying, crews = exclusive_groups(sim)
    base = w.manager.graph_e.get_base_vertex().id
    for s in w.soldiers.values():
        groups = (moving[s.id], flying[s.id], crews[s.id])
        assert sum(groups) <= 1, f"{s.id} is in two operations at once"                # never in two places at once
        assert (s.status in (St.MOVING, St.WAITING)) == bool(moving[s.id])
        assert (s.status == St.FLYING) == bool(flying[s.id])
        assert (s.status == St.REPAIRING) == bool(crews[s.id])
        if s.status == St.STATIONED:
            assert s.vertex in w.towers and tuple(s.xy) == w.coords(s.vertex)
        if s.status == St.AT_BASE:
            assert s.vertex == base and tuple(s.xy) == w.coords(base)
    for vid in w.towers:                                                               # occupants + reservations <= 3
        pending = sum(len(t.soldier_ids) for t in sim.ground.transfers if t.status != "DONE" and t.dest == vid)
        pending += sum(f.reserved for f in sim.air.flights if f.status == "FLYING" and f.target == vid)
        assert w.reserved.get(vid, 0) == pending
        assert 0 <= w.occupants(vid) + w.reserved.get(vid, 0) <= TOWER_CAPACITY
    for e in w.manager.graph_e.edges.values():                                         # bridges keep consistent data
        if e.is_bridge:
            assert (e.bridge_current_hp == 0) == e.is_destroyed
            assert 0 <= e.bridge_current_hp <= e.bridge_max_hp
        else:
            assert not e.is_destroyed
    assert sim.air.uses <= sim.air.max_uses


def state_of(sim):
    w = sim.world
    return (w.budget.available, w.budget.reserved, dict(w.reserved), {i: (s.status, s.vertex) for i, s in w.soldiers.items()},
            len(sim.ground.transfers), len(sim.air.flights), sim.air.uses, len(w.events))


def random_order(sim, rng):
    """One random command. Rejections must be clean: they leave the state untouched."""
    w = sim.world
    free = [s.id for s in w.soldiers.values() if s.status in (St.AT_BASE, St.STATIONED)]
    before = state_of(sim)
    try:
        roll = rng.random()
        if roll < 0.25:
            sim.recruit(rng.choice(["infantry", "sniper", "gunner"]), rng.randint(1, 2))
        elif free and roll < 0.85:
            ids = rng.sample(free, rng.randint(1, min(4, len(free))))
            dest = rng.choice([*w.towers, w.manager.graph_e.get_base_vertex().id])
            mode = rng.choice(["walk", "moto", "moto", "air"])
            money = (w.budget.available, w.budget.reserved, w.budget.spent)
            if mode == "air":
                sim.air.request(ids, dest)
            else:
                sim.ground.request(ids, dest, mode)
                assert (w.budget.available, w.budget.reserved, w.budget.spent) == money   # ground transport is free
    except AppError:
        assert state_of(sim) == before, "a rejected order changed the state"


@pytest.mark.parametrize("name", SCENARIOS)
@pytest.mark.parametrize("slow", [False, True], ids=["normal", "slow-convoy"])
@pytest.mark.parametrize("seed", range(6))
def test_invariants_hold_through_random_matches(name, slow, seed):
    rng = random.Random(f"{name}-{slow}-{seed}")
    manager = load(name)
    if slow:
        slow_convoy(manager, 0.05)                      # a long match: bridges collapse and are rebuilt several times
    sim = Simulation(manager, plan_defense(manager))
    initial = manager.metadata.initial_budget
    sim.world.budget.available += 3000                   # plenty of money so every kind of order happens
    initial += 3000
    last_clock = 0.0
    for _ in range(160):
        random_order(sim, rng)
        check(sim, initial)
        sim.tick(rng.choice([0.25, 0.5, 1, 2.5, 5]))
        check(sim, initial)
        assert sim.world.clock >= last_clock
        last_clock = sim.world.clock
        if sim.world.status.value in ("VICTORY_ELIMINATION", "VICTORY_RESISTANCE", "DEFEAT"):
            frozen = (sim.world.clock, len(sim.world.events), sim.world.budget.available)
            sim.tick(10)
            assert (sim.world.clock, len(sim.world.events), sim.world.budget.available) == frozen   # updates stop at the end
            break


def test_random_matches_reach_every_interesting_situation():
    """Meta-test: the random orders must actually produce collapses, rebuilds, flights and kills (else the fuzz is idle)."""
    seen = Counter()
    for name in SCENARIOS:
        for seed in range(6):
            rng = random.Random(f"meta-{name}-{seed}")
            manager = load(name)
            slow_convoy(manager, 0.05)
            sim = Simulation(manager, plan_defense(manager))
            sim.world.budget.available += 3000
            for _ in range(160):
                random_order(sim, rng)
                sim.tick(rng.choice([0.5, 1, 2.5, 5]))
            texts = " ".join(e["text"] for e in sim.world.events)
            seen["collapse"] += "colapsó" in texts
            seen["rebuilt"] += "fue reconstruido" in texts
            seen["flight"] += "aterrizó" in texts
            seen["surplus"] += "excedente" in texts
            seen["kill"] += "Destruido" in texts
            seen["blocked"] += "quedan detenidos" in texts
            seen["crew"] += "empiezan a reconstruir" in texts
    assert all(seen[k] > 0 for k in ("collapse", "rebuilt", "flight", "surplus", "kill", "blocked", "crew")), dict(seen)
