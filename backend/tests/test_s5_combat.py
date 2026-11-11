"""Section 5: defensive units and combat rules."""
from conftest import match, slow_convoy, station
from src.features.simulation.domain.units import SoldierStatus


def _target_at(sim, tower):
    """Put the whole convoy exactly on a tower so everything is in range."""
    sim.convoy.xy = sim.world.coords(tower)


def test_effective_range_uses_tower_height():
    sim, _ = match()
    (sid,) = station(sim, "infantry", "V_C1")        # z = 2, beta = 0.2, R_base = 5
    assert abs(sim.world.effective_range(sim.world.soldiers[sid]) - 5 * (1 + 0.2 * 2)) < 1e-9
    (sn,) = station(sim, "sniper", "V_C2")           # z = 5, R_base = 20
    assert abs(sim.world.effective_range(sim.world.soldiers[sn]) - 20 * (1 + 0.2 * 5)) < 1e-9


def test_infantry_and_sniper_hit_the_weakest_living_enemy_ties_by_id():
    sim, _ = match()
    by_id = {e.id: e for e in sim.world.enemies}
    by_id["TANK-1"].hp, by_id["TRUCK-1"].hp = 80, 80          # tie between two ids
    by_id["ROBOT_SOLDIER-1"].hp, by_id["ROBOT_SOLDIER-2"].hp = 40, 30
    (sid,) = station(sim, "sniper", "V_C1")
    _target_at(sim, "V_C1")
    sim.world.clock = 1.0
    sim.combat.update(sim.convoy.xy)
    assert by_id["ROBOT_SOLDIER-2"].hp == 0                   # 30 hp was the weakest (50 dmg)
    sim.world.soldiers[sid].next_attack = 0
    sim.combat.update(sim.convoy.xy)
    assert by_id["ROBOT_SOLDIER-1"].hp == 0                   # next weakest
    sim.world.soldiers[sid].next_attack = 0
    sim.combat.update(sim.convoy.xy)
    # TANK-1 and TRUCK-1 tie at 80 HP: "TANK-1" < "TRUCK-1", so the tank takes the hit
    assert by_id["TANK-1"].hp == 30 and by_id["TRUCK-1"].hp == 80


def test_tie_between_equal_hp_goes_to_smaller_id():
    sim, _ = match()
    for e in sim.world.enemies:
        e.hp = 60
    (sid,) = station(sim, "infantry", "V_C1")
    _target_at(sim, "V_C1")
    sim.world.clock = 1.0
    sim.combat.update(sim.convoy.xy)
    hit = [e.id for e in sim.world.enemies if e.hp < 60]
    assert hit == ["ROBOT_SOLDIER-1"]                          # smallest id among equals


def test_gunner_damages_every_living_enemy_in_range_only():
    sim, _ = match()
    station(sim, "gunner", "V_C1")
    _target_at(sim, "V_C1")
    sim.world.enemies[0].hp = 0                               # dead machines are skipped
    sim.world.clock = 1.0
    before = [e.hp for e in sim.world.enemies]
    sim.combat.update(sim.convoy.xy)
    after = [e.hp for e in sim.world.enemies]
    assert after[0] == 0 and all(a == max(0, b - 100) for a, b in zip(after[1:], before[1:]))


def test_out_of_range_means_no_attack_and_weapon_stays_ready():
    sim, _ = match()
    (sid,) = station(sim, "infantry", "V_C1")
    sim.convoy.xy = (200.0, 200.0)
    sim.world.clock = 5.0
    sim.combat.update(sim.convoy.xy)
    assert all(e.hp == e.max_hp for e in sim.world.enemies)
    assert sim.world.soldiers[sid].next_attack == 0.0


def test_attack_frequency_is_respected():
    sim, manager = match()
    slow_convoy(manager)
    (sid,) = station(sim, "sniper", "V_C1")                   # 0.5 attacks/s -> one every 2 s
    _target_at(sim, "V_C1")
    sim.convoy.update = lambda dt: None                        # keep the convoy on the tower
    hits = []
    for _ in range(40):                                        # 10 logical seconds
        before = sum(e.hp for e in sim.world.enemies)
        sim.tick(0.25)
        hits.append(before - sum(e.hp for e in sim.world.enemies))
    assert sum(1 for h in hits if h > 0) == 5                  # 5 attacks in 10 s


def test_soldier_cannot_attack_in_the_update_it_arrives():
    sim, manager = match()
    slow_convoy(manager)
    sim.recruit("sniper", 1)
    sim.ground.request(["S1"], "V_C1", "moto")                 # 8 s by motorcycle
    sim.convoy.update = lambda dt: None
    arrival = hit_at = None
    for _ in range(80):
        sim.convoy.xy = sim.world.coords("V_C1")
        sim.tick(0.25)
        s = sim.world.soldiers["S1"]
        if arrival is None and s.status == SoldierStatus.STATIONED:
            arrival = sim.world.clock
        if hit_at is None and any(e.hp < e.max_hp for e in sim.world.enemies):
            hit_at = sim.world.clock
    assert arrival is not None and hit_at is not None and hit_at > arrival


def test_soldiers_in_transit_do_not_attack():
    sim, _ = match()
    (sid,) = station(sim, "gunner", "V_C1")
    sim.world.soldiers[sid].status = SoldierStatus.MOVING     # on the road
    _target_at(sim, "V_C1")
    sim.world.clock = 1.0
    sim.combat.update(sim.convoy.xy)
    assert all(e.hp == e.max_hp for e in sim.world.enemies)


def test_reward_paid_once_and_dead_units_are_not_attacked_again():
    sim, _ = match()
    sim.world.enemies = sim.world.enemies[:1]                  # only TANK-1
    sim.world.enemies[0].hp = 20
    station(sim, "gunner", "V_C1", 3)
    _target_at(sim, "V_C1")
    sim.world.clock = 1.0
    before = sim.world.budget.available
    sim.combat.update(sim.convoy.xy)                           # 3 gunners fire in the same update
    assert sim.world.budget.available == before + 150          # a single reward
    hits = [e for e in sim.world.events if e["kind"] == "combat"]
    assert len(hits) == 1                                      # the other two had no living target
