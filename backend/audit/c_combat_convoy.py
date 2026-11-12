"""Audit checks for sections 5, 6 and 7: soldiers and combat, the convoy and its danger, ground transport."""
from audit.core import Match, check, hits

BASE_LEN = {"infantry": 100, "sniper": 300, "gunner": 500}


def sniper_in_tower(api, tower="V_C1", **options):
    m = Match(api, **options)
    m.buy("sniper")
    m.move(["S1"], tower, "moto")
    return m


@check("§5", "Las torres admiten tres soldados como máximo, de cualquier especialidad (ocupantes + reservas)")
def capacity(api):
    m = Match(api)
    m.buy("infantry", 2)
    m.buy("sniper", 2)
    m.buy("gunner", 1)
    for sid in ("S1", "S3", "S5"):
        m.move([sid], "V_C1", "walk")
    m.rejected("/transport/move", {"soldier_ids": ["S2"], "dest": "V_C1", "mode": "walk"}, "no tiene capacidad libre")


@check("§5", "Alcance efectivo Ref = Rbase * (1 + beta*z): francotirador (20) en V_C1 (z = 2, beta = 0.2) alcanza 28")
def effective_range(api):
    m = sniper_in_tower(api)
    state = m.tick(8)
    assert [s["ref"] for s in state["soldiers"]] == [28.0] and state["soldiers"][0]["status"] == "STATIONED"


@check("§5", "Tras llegar a una torre puede atacar en el siguiente instante de actualización, no en el mismo")
def attacks_next_instant(api):
    m = sniper_in_tower(api)
    state = m.tick(8.25)
    arrived = next(e["t"] for e in state["events"] if "llegaron" in e["text"])
    first = min(e["t"] for e in hits(state))
    assert arrived == 8.0 and first == 8.25


@check("§5", "Infantería y francotirador atacan a la máquina viva de menor resistencia (empate por identificación)")
def weakest_first(api):
    state = sniper_in_tower(api).tick(15)
    targets = [e["text"].split(" golpea a ")[1].split(":")[0] for e in hits(state)]
    assert targets[:2] == ["ROBOT_SOLDIER-1", "ROBOT_SOLDIER-2"] and targets[2].startswith("TRUCK")   # 50 hp, 50 hp, 100 hp


@check("§5", "Frecuencia de ataque: el francotirador (0,5 ataques/s) dispara cada 2 s")
def frequency(api):
    times = [e["t"] for e in hits(sniper_in_tower(api).tick(15))]
    assert times == [8.25, 10.25, 12.25, 14.25]


@check("§5", "El artillero aplica su daño a todas las máquinas vivas que alcance (área)")
def gunner_area(api):
    m = Match(api)
    m.buy("gunner")
    m.move(["S1"], "V_C2", "moto")
    state = m.tick(16)
    first = hits(state)[0]["t"]
    same_instant = [e for e in hits(state) if e["t"] == first]
    assert len(same_instant) >= 2, f"only {len(same_instant)} hit at {first}"


@check("§5/§10", "Cada máquina destruida genera una única recompensa (tanque 150, camión 100, robot 50)")
def single_reward(api):
    m = Match(api)
    m.buy("sniper", 2)
    m.move(["S1", "S2"], "V_C1", "moto")
    state = m.tick(30)
    assert state["status"] == "VICTORY_ELIMINATION" and state["budget"]["earned"] == 150 + 100 + 50 + 50
    assert state["budget"]["available"] == 2000 - 600 + 350 and state["clock"] == 14.25


@check("§6", "El JSON define las cantidades del convoy; cada máquina tiene identidad y resistencia propias (200/100/50 HP)")
def convoy_composition(api):
    enemies = Match(api).state()["convoy"]["enemies"]
    assert sorted((e["type"], e["max_hp"], e["reward"]) for e in enemies) == [
        ("ROBOT_SOLDIER", 50, 50), ("ROBOT_SOLDIER", 50, 50), ("TANK", 200, 150), ("TRUCK", 100, 100)]
    assert len({e["id"] for e in enemies}) == 4


@check("§6", "Peligro: D(q) = suma d*f de los soldados que alcanzan q; P(e) = media de 3 puntos * t(e); w(e) = t(e) + alfa*P(e)")
def danger_and_weight(api):
    state = sniper_in_tower(api).tick(9)
    m_c1 = next(c for c in state["corridors"] if c["id"] == "M_C1")
    assert m_c1["time"] == 8.0 and round(m_c1["danger"], 2) == 133.33 and m_c1["weight"] == 208.0   # (0+25+25)/3*8 ; 8+1.5*133.33


@check("§6", "Navegación reactiva: en cada intersección elige el primer corredor de la mejor ruta y explica las opciones")
def reactive_choice(api):
    state = Match(api).tick(8.25)
    decision = state["convoy"]["decision"]
    assert decision["at"] == "M_N1" and decision["chosen"]["corridor"] == "M_C2" and len(decision["options"]) >= 1
    assert any(e["kind"] == "convoy" and "toma M_C2" in e["text"] for e in state["events"])


@check("§6", "Sin defensas, el convoy tarda exactamente el tiempo del camino inicial de menor costo (23 s)")
def undefended(api):
    state = Match(api).tick(100)
    assert state["status"] == "DEFEAT" and state["clock"] == 23.0


@check("§7", "Cada soldado adquirido aparece en la base")
def appears_at_base(api):
    soldier = Match(api).buy("infantry")["soldiers"][0]
    assert soldier["status"] == "AT_BASE" and soldier["vertex"] == "V_BASE"


@check("§7", "A pie va un soldado por operación; en moto uno o dos")
def transport_capacity(api):
    m = Match(api)
    m.buy("infantry", 3)
    m.rejected("/transport/move", {"soldier_ids": ["S1", "S2"], "dest": "V_C1", "mode": "walk"}, "A pie va 1 soldado")
    m.rejected("/transport/move", {"soldier_ids": ["S1", "S2", "S3"], "dest": "V_C1", "mode": "moto"}, "en moto pueden ir 1 o 2")
    assert m.move(["S1", "S2"], "V_C1", "moto")["transfers"][0]["soldiers"] == ["S1", "S2"]


@check("§7", "Antes de aceptar: origen y destino, ruta válida, soldados disponibles y capacidad; si falla, el estado no cambia")
def validations_leave_state(api):
    m = Match(api)
    m.buy("infantry")
    m.rejected("/transport/move", {"soldier_ids": ["S1"], "dest": "NOPE", "mode": "walk"}, "destino")
    m.rejected("/transport/move", {"soldier_ids": ["S9"], "dest": "V_C1", "mode": "walk"}, "no existe")
    m.rejected("/transport/move", {"soldier_ids": ["S1"], "dest": "V_BASE", "mode": "walk"}, "mismo")
    m.move(["S1"], "V_C1", "walk")
    m.rejected("/transport/move", {"soldier_ids": ["S1"], "dest": "V_C2", "mode": "walk"}, "ocupado")


@check("§7/§11", "Los soldados en tránsito no atacan")
def transit_does_not_attack(api):
    m = Match(api)
    m.buy("sniper")
    m.move(["S1"], "V_C1", "walk")                                  # arrives at 20 s: the convoy passes by much earlier
    state = m.tick(19.75)
    assert state["soldiers"][0]["status"] == "MOVING" and hits(state) == []
