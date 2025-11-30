# ============================
# src/ea_corridors/energy.py
# ============================

from __future__ import annotations

from dataclasses import dataclass

from .config import ENERGY_PARAMS, EnergyParams
from .models import EnergyResult


@dataclass
class EnergyModel:
    """
    Simple physics-light time/fuel/CO2 model.

    Uses cubic speed–power scaling and constant SFOC, plus constant
    auxiliary load.
    """

    params: EnergyParams = ENERGY_PARAMS

    def voyage_time_days(self, distance_nm: float, speed_kn: float) -> float:
        return distance_nm / speed_kn / 24.0

    def main_engine_fuel_t(self, distance_nm: float, speed_kn: float) -> float:
        # cubic law: P ~ (U / U0)^3
        p_ratio = (speed_kn / self.params.U0_kn) ** 3
        p_kw = self.params.P0_kw * p_ratio
        t_h = distance_nm / speed_kn
        fuel_g = p_kw * t_h * self.params.sfoc_me_g_per_kwh
        return fuel_g / 1e6  # tonnes

    def aux_fuel_t(self, time_days: float) -> float:
        t_h = time_days * 24.0
        fuel_g = self.params.P_ae_kw * t_h * self.params.sfoc_ae_g_per_kwh
        return fuel_g / 1e6

    def total_energy_result(
        self, scenario: str, corridor: str, variant: str,
        distance_nm: float, speed_kn: float
    ) -> EnergyResult:
        time_days = self.voyage_time_days(distance_nm, speed_kn)
        fuel_main = self.main_engine_fuel_t(distance_nm, speed_kn)
        fuel_aux = self.aux_fuel_t(time_days)
        fuel_total = fuel_main + fuel_aux
        co2 = fuel_total * self.params.ef_co2_t_per_tfuel

        return EnergyResult(
            scenario=scenario,
            corridor=corridor,
            variant=variant,
            distance_nm=distance_nm,
            speed_kn=speed_kn,
            time_days=time_days,
            fuel_t_main=fuel_main,
            fuel_t_aux=fuel_aux,
            fuel_t_total=fuel_total,
            co2_t=co2,
        )