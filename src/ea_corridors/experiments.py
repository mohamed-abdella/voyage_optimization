# ============================
# src/ea_corridors/experiments.py
# ============================

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd

from .config import SCENARIOS, SPEEDS, CORRIDOR_ORDER, EQUAL_SPEED
from .models import CorridorVariant
from .routing import RoutingEngine
from .energy import EnergyModel


@dataclass
class BaselineRunner:
    """
    Runs the baseline Rotterdam–Yokohama experiment (Cases 0–2).

    Produces a core DataFrame with distance + time + fuel + CO2 for each
    corridor/variant under corridor-typical speeds.
    """

    routing: RoutingEngine
    energy: EnergyModel

    def run(self, scenarios: Dict[str, CorridorVariant] = SCENARIOS) -> pd.DataFrame:
        # geometric part
        df = self.routing.run_baseline_routes(scenarios)

        # SEA-only subset for energy computations
        sea = df[df["method"] == "SEA"].copy()
        records = []

        for row in sea.itertuples():
            speed_kn = SPEEDS[row.corridor]
            res = self.energy.total_energy_result(
                scenario=row.scenario,
                corridor=row.corridor,
                variant=row.variant,
                distance_nm=row.distance_nm,
                speed_kn=speed_kn,
            )
            records.append(res.__dict__)

        energy_df = pd.DataFrame(records)

        # merge for convenience (distance_knm, etc.)
        merged = sea.merge(
            energy_df,
            on=["scenario", "corridor", "variant", "distance_nm"],
            how="left",
            suffixes=("", "_energy"),
        )
        merged["distance_knm"] = merged["distance_nm"] / 1000.0
        return merged

    def corridor_medians(self, baseline_df: pd.DataFrame) -> pd.DataFrame:
        """Case 1 style table: medians across variants per corridor."""
        grp = (
            baseline_df.groupby("corridor", observed=True)
            .agg(
                median_knm=("distance_knm", "median"),
                min_knm=("distance_knm", "min"),
                max_knm=("distance_knm", "max"),
                std_nm=("distance_nm", "std"),
            )
            .reindex(CORRIDOR_ORDER)
        )
        grp["cv_pct"] = grp["std_nm"] / (grp["median_knm"] * 1000.0) * 100.0
        return grp.reset_index()


@dataclass
class SensitivityRunner:
    """
    Runs endpoint (Busan) + equal-speed sensitivities.
    """

    routing: RoutingEngine
    energy: EnergyModel

    def endpoint_sensitivity(
        self,
        yokohama_df: pd.DataFrame,
        scenarios: Dict[str, CorridorVariant] = SCENARIOS,
        dest_override: str = "BUSAN",
    ) -> pd.DataFrame:
        """
        Recompute SEA-only distances with Busan as endpoint, then build
        Yokohama vs Busan comparison table for Case 4.
        """
        # Clone scenarios but replace final waypoint with BUSAN:
        from .config import BUSAN

        scen_busan: Dict[str, CorridorVariant] = {}
        for key, scen in scenarios.items():
            wps = list(scen.waypoints)
            wps[-1] = BUSAN
            scen_busan[key] = CorridorVariant(
                name=scen.name,
                corridor=scen.corridor,
                variant=scen.variant,
                waypoints=wps,
            )

        df_busan = self.routing.run_baseline_routes(scen_busan)
        sea_busan = df_busan[df_busan["method"] == "SEA"].copy()

        sea_yok = yokohama_df.copy()

        merged = sea_yok.merge(
            sea_busan[["scenario", "distance_nm"]],
            on="scenario",
            suffixes=("_yok", "_bus"),
        )

        merged["delta_nm"] = merged["distance_nm_bus"] - merged["distance_nm_yok"]
        merged["delta_pct"] = merged["delta_nm"] / merged["distance_nm_yok"] * 100.0

        merged["Yokohama (k nm)"] = merged["distance_nm_yok"] / 1000.0
        merged["Busan (k nm)"] = merged["distance_nm_bus"] / 1000.0
        merged["Delta (k nm)"] = merged["delta_nm"] / 1000.0
        merged["Delta (%)"] = merged["delta_pct"]

        return merged[
            [
                "corridor",
                "variant",
                "Yokohama (k nm)",
                "Busan (k nm)",
                "Delta (k nm)",
                "Delta (%)",
            ]
        ].sort_values(["corridor", "variant"])

    def equal_speed_sensitivity(self, sea_yok_df: pd.DataFrame) -> pd.DataFrame:
        """
        Recompute median days at a common speed for all corridors.
        """
        df = sea_yok_df.copy()
        df["time_days_corridor_speed"] = (
            df["distance_nm"] / df["corridor"].map(SPEEDS) / 24.0
        )
        df["time_days_equal_speed"] = df["distance_nm"] / EQUAL_SPEED / 24.0

        summary = (
            df.groupby("corridor", observed=True)
            .agg(
                dist_med_knm=("distance_nm", lambda x: np.median(x) / 1000.0),
                days_med_corr=("time_days_corridor_speed", "median"),
                days_med_equal=("time_days_equal_speed", "median"),
            )
            .reindex(CORRIDOR_ORDER)
            .reset_index()
        )
        return summary
