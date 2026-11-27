"""Values the statement fixes: a scenario may repeat them but not change them."""

# Section 5: cost, damage, base range and attacks per second of every defender
DEFENDER_TABLE = {
    "infantry": {"cost": 100, "damage": 10, "base_range": 5, "frequency": 1},
    "sniper": {"cost": 300, "damage": 50, "base_range": 20, "frequency": 0.5},
    "gunner": {"cost": 500, "damage": 100, "base_range": 15, "frequency": 0.2},
}
TIME_LIMIT = 300      # section 11: seconds of resistance needed to win
