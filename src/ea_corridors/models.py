# ============================
# src/ea_corridors/models.py
# ============================

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Dict


@dataclass(frozen=True)
class Waypoint:
    """Simple lat/lon waypoint (lon, lat order to match searoute)."""
    lon: float
    lat: float

    def as_tuple(self):
        return (self.lon, self.lat)


@dataclass(frozen=True)
class CorridorVariant:
    """A macro-waypoint chain representing one corridor philosophy."""
    name: str          # e.g. 'NSR_VAR1_service'
    corridor: str      # 'NSR', 'SUEZ', 'CAPE'
    variant: str       # 'service', 'bluewater', 'coast'
    waypoints: List[Waypoint]


@dataclass
class RouteResult:
    """Geometric results for a particular corridor/variant/method."""
    scenario: str           # matches CorridorVariant.name
    corridor: str
    variant: str
    method: Literal["GC", "SEA"]
    distance_nm: float
    polyline: List[Waypoint]


@dataclass
class EnergyResult:
    """Time/fuel/CO2 for one SEA route realization."""
    scenario: str
    corridor: str
    variant: str
    distance_nm: float
    speed_kn: float
    time_days: float
    fuel_t_main: float
    fuel_t_aux: float
    fuel_t_total: float
    co2_t: float