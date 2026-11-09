"""Simulation domain entities and enums."""
from enum import Enum
from dataclasses import dataclass


class SimState(str, Enum):
    """Simulation lifecycle states."""
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    VICTORY_ELIMINATION = "VICTORY_ELIMINATION"
    VICTORY_RESISTANCE = "VICTORY_RESISTANCE"
    DEFEAT = "DEFEAT"


class SoldierType(str, Enum):
    """Types of defensive soldiers."""
    INFANTRY = "INFANTRY"
    SNIPER = "SNIPER"
    GUNNER = "GUNNER"


class EnemyType(str, Enum):
    """Types of convoy machines."""
    TANK = "TANK"
    TRUCK = "TRUCK"
    ROBOT_SOLDIER = "ROBOT_SOLDIER"

