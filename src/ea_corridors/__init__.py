# ============================
# src/ea_corridors/__init__.py
# ============================

"""
ea_corridors: Reproducible corridor-routing baseline for Europe–Asia trades.

This package exposes:
- Object model for corridors and waypoint variants.
- RoutingEngine for GC-chain and sea-only distances (via searoute).
- EnergyModel for indicative time, fuel, and CO2.
- Experiment runners for baseline and sensitivity analyses.
"""

from .config import CORRIDOR_ORDER, SPEEDS, ENERGY_PARAMS
from .models import Waypoint, CorridorVariant, RouteResult, EnergyResult
from .routing import RoutingEngine
from .energy import EnergyModel
from .experiments import (
    BaselineRunner,
    SensitivityRunner,
)

__all__ = [
    "CORRIDOR_ORDER",
    "SPEEDS",
    "ENERGY_PARAMS",
    "Waypoint",
    "CorridorVariant",
    "RouteResult",
    "EnergyResult",
    "RoutingEngine",
    "EnergyModel",
    "BaselineRunner",
    "SensitivityRunner",
]