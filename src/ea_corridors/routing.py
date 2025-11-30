# ============================
# src/ea_corridors/routing.py
# ============================

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

import numpy as np
import pandas as pd
from geographiclib.geodesic import Geodesic

import searoute as sr  # type: ignore

from .models import Waypoint, CorridorVariant, RouteResult


@dataclass
class RoutingEngine:
    """
    Wraps great-circle and searoute-based sea-only routing.

    - GC distances via geographiclib (between macro-waypoints).
    - SEA distances via searoute on each leg.
    """

    units: str = "nm"

    def gc_nm(self, a: Waypoint, b: Waypoint) -> float:
        """Great-circle distance in nautical miles."""
        g = Geodesic.WGS84.Inverse(a.lat, a.lon, b.lat, b.lon)
        return g["s12"] / 1852.0

    def polyline_nm(self, points: List[Waypoint]) -> float:
        """Sum GC distances along a polyline."""
        d = 0.0
        for p, q in zip(points[:-1], points[1:]):
            d += self.gc_nm(p, q)
        return d

    def sea_leg(self, a: Waypoint, b: Waypoint) -> RouteResult:
        """Sea-only leg using searoute between two waypoints."""
        lon1, lat1 = a.lon, a.lat
        lon2, lat2 = b.lon, b.lat

        res = sr.searoute(
            origin=(lon1, lat1),
            destination=(lon2, lat2),
            units=self.units,
        )
        coords = res["route"]  # list of (lon, lat)
        poly = [Waypoint(lon=c[0], lat=c[1]) for c in coords]
        dist_nm = res["distance_nm"] if "distance_nm" in res else res["distance"]
        return RouteResult(
            scenario="",
            corridor="",
            variant="",
            method="SEA",
            distance_nm=dist_nm,
            polyline=poly,
        )

    def route_gc_chain(self, scen: CorridorVariant) -> RouteResult:
        """GC distance along macro-waypoint chain."""
        dist_nm = self.polyline_nm(scen.waypoints)
        return RouteResult(
            scenario=scen.name,
            corridor=scen.corridor,
            variant=scen.variant,
            method="GC",
            distance_nm=dist_nm,
            polyline=scen.waypoints,
        )

    def route_sea_only_chain(self, scen: CorridorVariant) -> RouteResult:
        """
        Sea-only route by stitching searoute legs between successive macro-wps.
        """
        full_poly: List[Waypoint] = [scen.waypoints[0]]
        total_nm = 0.0

        for a, b in zip(scen.waypoints[:-1], scen.waypoints[1:]):
            leg_res = self.sea_leg(a, b)
            total_nm += leg_res.distance_nm
            # avoid duplicating first point of each leg
            full_poly.extend(leg_res.polyline[1:])

        return RouteResult(
            scenario=scen.name,
            corridor=scen.corridor,
            variant=scen.variant,
            method="SEA",
            distance_nm=total_nm,
            polyline=full_poly,
        )

    def run_baseline_routes(
        self, scenarios: Dict[str, CorridorVariant]
    ) -> pd.DataFrame:
        """
        Compute GC and SEA distances for all scenarios.

        Returns
        -------
        df : pandas.DataFrame
            Columns: scenario, corridor, variant, method, distance_nm.
        """
        records = []

        for scen_key, scen in scenarios.items():
            gc_res = self.route_gc_chain(scen)
            sea_res = self.route_sea_only_chain(scen)

            records.append(
                dict(
                    scenario=scen_key,
                    corridor=scen.corridor,
                    variant=scen.variant,
                    method="GC",
                    distance_nm=gc_res.distance_nm,
                )
            )
            records.append(
                dict(
                    scenario=scen_key,
                    corridor=scen.corridor,
                    variant=scen.variant,
                    method="SEA",
                    distance_nm=sea_res.distance_nm,
                )
            )

        df = pd.DataFrame(records)
        df["distance_knm"] = df["distance_nm"] / 1000.0
        return df