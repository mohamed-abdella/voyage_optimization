# ============================
# src/ea_corridors/config.py
# ============================

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .models import Waypoint, CorridorVariant


# ---- basic constants ----

# Origin/destination for main case:
ROTTERDAM = Waypoint(lon=4.14, lat=51.95)
YOKOHAMA = Waypoint(lon=139.65, lat=35.45)
BUSAN = Waypoint(lon=129.07, lat=35.1)  # approximate; refine if needed

CORRIDOR_ORDER = ["SUEZ", "NSR", "CAPE"]

# Corridor-typical speeds (knots)
SPEEDS: Dict[str, float] = {
    "NSR": 12.5,
    "SUEZ": 14.5,
    "CAPE": 14.0,
}

EQUAL_SPEED = 14.0  # for equal-speed sensitivity


@dataclass(frozen=True)
class EnergyParams:
    """Container for simple time/fuel/CO2 parameters."""
    P0_kw: float          # reference ME power
    U0_kn: float          # reference speed
    sfoc_me_g_per_kwh: float
    P_ae_kw: float
    sfoc_ae_g_per_kwh: float
    ef_co2_t_per_tfuel: float


ENERGY_PARAMS = EnergyParams(
    P0_kw=35000.0,
    U0_kn=14.5,
    sfoc_me_g_per_kwh=170.0,
    P_ae_kw=2000.0,
    sfoc_ae_g_per_kwh=185.0,
    ef_co2_t_per_tfuel=3.114,
)


# ---- waypoint philosophies (service / bluewater / coast) ----
# These are your macro-waypoints; keep them minimal here and
# adjust exactly to what you’ve converged on in the paper.

def wp(lon: float, lat: float) -> Waypoint:
    return Waypoint(lon=lon, lat=lat)


SCENARIOS: Dict[str, CorridorVariant] = {
    # SUEZ
    "SUEZ_VAR1_service": CorridorVariant(
        name="SUEZ_VAR1_service",
        corridor="SUEZ",
        variant="service",
        waypoints=[
            ROTTERDAM,
            wp(3.0, 51.0),
            wp(0.0, 48.0),
            wp(-5.0, 43.0),
            wp(-10.0, 35.0),
            wp(-5.0, 25.0),
            wp(0.0, 15.0),
            wp(10.0, 10.0),
            wp(20.0, 15.0),
            wp(25.0, 25.0),
            wp(32.0, 30.0),
            wp(32.0, 35.0),
            wp(26.0, 36.0),  # Suez vicinity
            wp(30.0, 28.0),
            wp(40.0, 20.0),
            wp(60.0, 15.0),
            wp(80.0, 20.0),
            wp(100.0, 25.0),
            wp(120.0, 30.0),
            YOKOHAMA,
        ],
    ),
    # Define SUEZ_VAR2_bluewater, SUEZ_VAR3_coast, CAPE_* and NSR_* similarly.
    # For brevity here, only one NSR example:

    "NSR_VAR1_service": CorridorVariant(
        name="NSR_VAR1_service",
        corridor="NSR",
        variant="service",
        waypoints=[
            ROTTERDAM,
            wp(5.0, 57.0),
            wp(15.0, 66.0),
            wp(35.0, 72.0),
            wp(65.0, 74.0),
            wp(95.0, 76.0),
            wp(135.0, 75.0),
            wp(170.0, 70.0),
            wp(-169.0, 66.0),  # across Bering
            wp(-150.0, 50.0),
            wp(150.0, 43.0),
            YOKOHAMA,
        ],
    ),
    # CAPE corridor example
    "CAPE_VAR1_service": CorridorVariant(
        name="CAPE_VAR1_service",
        corridor="CAPE",
        variant="service",
        waypoints=[
            ROTTERDAM,
            wp(-5.0, 45.0),
            wp(-15.0, 35.0),
            wp(-10.0, 15.0),
            wp(0.0, 0.0),
            wp(20.0, -15.0),
            wp(40.0, -30.0),
            wp(60.0, -20.0),
            wp(80.0, -10.0),
            wp(100.0, 0.0),
            wp(120.0, 20.0),
            YOKOHAMA,
        ],
    ),
}

# For Busan sensitivity you can reuse the same SCENARIOS but change destination
# in the experiment runner; no need for separate dict.
