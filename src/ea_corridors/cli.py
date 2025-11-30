# ============================
# src/ea_corridors/cli.py
# ============================

from __future__ import annotations

import argparse
import os

from .routing import RoutingEngine
from .energy import EnergyModel
from .experiments import BaselineRunner, SensitivityRunner
from .plotting import (
    plot_sea_distance_bars,
    plot_equal_speed_bars,
    plot_endpoint_dumbbell,
)
from .io import to_latex_table


def main():
    parser = argparse.ArgumentParser(
        description="Reproduce baseline corridor-routing experiments."
    )
    parser.add_argument(
        "--outdir", default="outputs", help="Directory for tables/ and figures/"
    )
    args = parser.parse_args()

    outdir = args.outdir
    tabdir = os.path.join(outdir, "tables")
    figdir = os.path.join(outdir, "figures")

    os.makedirs(tabdir, exist_ok=True)
    os.makedirs(figdir, exist_ok=True)

    routing = RoutingEngine()
    energy = EnergyModel()
    base = BaselineRunner(routing, energy)

    baseline_df = base.run()
    sea_df = baseline_df.copy()

    # Tables
    med_tbl = base.corridor_medians(sea_df)
    to_latex_table(med_tbl, os.path.join(tabdir, "BASELINE_corridor_medians.tex"))
    to_latex_table(
        sea_df[
            ["corridor", "variant", "distance_knm", "time_days", "fuel_t_total", "co2_t"]
        ],
        os.path.join(tabdir, "BASELINE_all.tex"),
    )

    # Plots
    plot_sea_distance_bars(
        sea_df[["scenario", "corridor", "variant", "distance_nm"]].assign(
            distance_knm=lambda d: d["distance_nm"] / 1000.0
        ),
        os.path.join(figdir, "BASELINE_sea_distance.png"),
    )

    sens = SensitivityRunner(routing, energy)
    delta_df = sens.endpoint_sensitivity(sea_df)
    eq_summary = sens.equal_speed_sensitivity(sea_df)

    to_latex_table(delta_df, os.path.join(tabdir, "DEST_DELTA_vs_baseline_SEA.tex"))
    plot_endpoint_dumbbell(delta_df, os.path.join(figdir, "DEST_endpoint_sensitivity.png"))
    plot_equal_speed_bars(eq_summary, os.path.join(figdir, "BASELINE_equal_speed_days_bars.png"))

    print(f"Baseline + sensitivity outputs written under {outdir}/")


if __name__ == "__main__":
    main()