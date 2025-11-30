# ============================
# src/ea_corridors/plotting.py
# (only a couple of key plot functions; see notebooks for more)
# ============================

from __future__ import annotations

import os
from typing import Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .config import CORRIDOR_ORDER


def plot_sea_distance_bars(
    sea_df: pd.DataFrame,
    outpath: str,
) -> None:
    """Case 1 style sea-only distance bar plot."""
    df = sea_df.copy()
    df["scenario_label"] = df["corridor"] + "_" + df["variant"]
    color_map = {"NSR": "tab:blue", "SUEZ": "tab:orange", "CAPE": "tab:green"}
    colors = df["corridor"].map(color_map)

    plt.figure(figsize=(8, 4))
    plt.bar(df["scenario_label"], df["distance_knm"], color=colors)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Sea-only distance (k nm)")
    plt.title("Sea-only distance by corridor and variant")
    plt.tight_layout()
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    plt.savefig(outpath, dpi=300)
    plt.close()


def plot_equal_speed_bars(
    eq_summary: pd.DataFrame,
    outpath: str,
) -> None:
    """Equal-speed sensitivity bar plot."""
    x = np.arange(len(eq_summary))
    w = 0.35

    plt.figure(figsize=(6.5, 3.8))
    plt.bar(x - w / 2, eq_summary["days_med_corr"], width=w, label="Corridor-typical")
    plt.bar(
        x + w / 2,
        eq_summary["days_med_equal"],
        width=w,
        label=f"Equal speed",
    )
    plt.xticks(x, eq_summary["corridor"])
    plt.ylabel("Median indicative duration (days)")
    plt.title("Equal-speed sensitivity (SEA-only distances)")
    plt.legend(frameon=False)
    plt.tight_layout()
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    plt.savefig(outpath, dpi=300)
    plt.close()


def plot_endpoint_dumbbell(
    delta_df: pd.DataFrame,
    outpath: str,
) -> None:
    """Case 4 Yokohama vs Busan dumbbell."""
    plt.figure(figsize=(8, 4))
    y = np.arange(len(delta_df))

    for i, row in delta_df.iterrows():
        x1 = row["Yokohama (k nm)"]
        x2 = row["Busan (k nm)"]
        plt.plot([x1, x2], [i, i], color="0.7", linewidth=2)
        plt.scatter(x1, i, marker="o", s=50, color="tab:blue", label="Yokohama" if i == 0 else None)
        plt.scatter(x2, i, marker="s", s=50, color="tab:orange", label="Busan" if i == 0 else None)

    labels = [f"{r.corridor}_{r.variant}" for r in delta_df.itertuples()]
    plt.yticks(y, labels)
    plt.xlabel("Sea-only distance (k nm)")
    plt.title("Endpoint sensitivity: Yokohama vs Busan (SEA-only)")
    plt.legend(frameon=False, loc="lower right")
    plt.tight_layout()
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    plt.savefig(outpath, dpi=300)
    plt.close()
