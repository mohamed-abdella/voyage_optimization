# arctic_routing/core.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict
import datetime as dt
import heapq

import numpy as np
import xarray as xr


# ============================================================
# 1. Basic configuration and grid
# ============================================================

@dataclass
class RoutingDomain:
    """Geographic domain for the pan-Arctic routing grid."""
    lat_min: float = 40.0
    lat_max: float = 85.0
    lon_min: float = -20.0   # 20°W
    lon_max: float = 180.0
    dlat: float = 0.5
    dlon: float = 0.5

    @property
    def lat_centers(self) -> np.ndarray:
        return np.arange(self.lat_min + 0.5 * self.dlat,
                         self.lat_max + 0.5 * self.dlat,
                         self.dlat)

    @property
    def lon_centers(self) -> np.ndarray:
        return np.arange(self.lon_min + 0.5 * self.dlon,
                         self.lon_max + 0.5 * self.dlon,
                         self.dlon)

    @property
    def shape(self) -> Tuple[int, int]:
        return self.lat_centers.size, self.lon_centers.size


@dataclass
class RoutingGrid:
    """Regular lat–lon grid used for routing."""
    lats_2d: np.ndarray
    lons_2d: np.ndarray
    domain: RoutingDomain

    @classmethod
    def from_domain(cls, domain: RoutingDomain) -> "RoutingGrid":
        lat_c = domain.lat_centers
        lon_c = domain.lon_centers
        lons_2d, lats_2d = np.meshgrid(lon_c, lat_c)
        return cls(lats_2d=lats_2d, lons_2d=lons_2d, domain=domain)


# ============================================================
# 2. Data management: GEBCO and CMEMS SIC
# ============================================================

@dataclass
class BathymetryField:
    """Bathymetry interpolated to routing grid."""
    depth: np.ndarray  # shape (ny, nx), GEBCO convention: negative over sea
    sea_mask: np.ndarray  # bool, same shape as depth


@dataclass
class SeaIceField:
    """Sea-ice concentration interpolated to routing grid for a specific date."""
    date: dt.date
    sic: np.ndarray   # shape (ny, nx), in [0, 1]


class DataManager:
    """
    Handles loading / regridding of GEBCO and CMEMS sea-ice
    onto the 0.5° routing grid.
    """

    def __init__(
        self,
        routing_grid: RoutingGrid,
        gebco_ds: xr.Dataset,
        sic_ds: xr.Dataset,
        gebco_var: str = "elevation",
        sic_var: str = "siconc",
        sic_time_dim: str = "time",
    ):
        """
        Parameters
        ----------
        routing_grid : RoutingGrid
            0.5° routing grid.
        gebco_ds : xr.Dataset
            GEBCO dataset with variable `gebco_var`, in degrees lat/lon.
        sic_ds : xr.Dataset
            CMEMS sea-ice dataset with variable `sic_var`, on some native grid.
        gebco_var : str
            Name of bathymetry variable in GEBCO dataset.
        sic_var : str
            Name of SIC variable in CMEMS dataset.
        sic_time_dim : str
            Name of time dimension in CMEMS dataset.
        """
        self.grid = routing_grid
        self.gebco_ds = gebco_ds
        self.sic_ds = sic_ds
        self.gebco_var = gebco_var
        self.sic_var = sic_var
        self.sic_time_dim = sic_time_dim

    # ---------------- Bathymetry ----------------

    def get_bathymetry(self) -> BathymetryField:
        """
        Interpolate GEBCO bathymetry to the routing grid
        using bilinear interpolation.
        """
        lat_c = self.grid.domain.lat_centers
        lon_c = self.grid.domain.lon_centers

        # Subset GEBCO first to avoid global interp
        gebco_sub = self.gebco_ds.sel(
            lat=slice(self.grid.domain.lat_min - 1, self.grid.domain.lat_max + 1),
            lon=slice(self.grid.domain.lon_min - 1, self.grid.domain.lon_max + 1),
        )

        # Interpolate; assume GEBCO has lat, lon coords
        depth_rg = gebco_sub[self.gebco_var].interp(
            lat=lat_c,
            lon=lon_c
        )

        depth_arr = depth_rg.values  # (ny, nx)
        sea_mask = depth_arr < 0.0

        return BathymetryField(depth=depth_arr, sea_mask=sea_mask)

    # ---------------- Sea-ice -------------------

    def get_sic_for_date(self, date: dt.date) -> SeaIceField:
        """
        Interpolate CMEMS sea-ice concentration to routing grid for a given date.
        Uses nearest time slice from the reanalysis.
        """
        lat_c = self.grid.domain.lat_centers
        lon_c = self.grid.domain.lon_centers

        # nearest time slice
        sic_sel = self.sic_ds.sel({self.sic_time_dim: np.datetime64(date)}, method="nearest")

        # Subset slightly larger area for safety
        sic_sub = sic_sel.sel(
            lat=slice(self.grid.domain.lat_min - 2, self.grid.domain.lat_max + 2),
            lon=slice(self.grid.domain.lon_min - 2, self.grid.domain.lon_max + 2),
        )

        sic_rg = sic_sub[self.sic_var].interp(
            lat=lat_c,
            lon=lon_c
        )

        sic_arr = sic_rg.values  # (ny, nx)

        # CMEMS often uses NaN south of domain; set to 0 (open water)
        sic_arr = np.where(np.isnan(sic_arr), 0.0, sic_arr)

        return SeaIceField(date=date, sic=sic_arr)


# ============================================================
# 3. Masks: sea, depth, ice, joint
# ============================================================

@dataclass
class Masks:
    sea: np.ndarray        # bool
    depth_safe: np.ndarray # bool
    ice_safe: np.ndarray   # bool
    joint_safe: np.ndarray # bool


class MaskFactory:
    """Static helpers to build feasibility masks."""

    @staticmethod
    def make_sea_mask(depth: np.ndarray) -> np.ndarray:
        return depth < 0.0

    @staticmethod
    def make_depth_mask(depth: np.ndarray, sea_mask: np.ndarray, h_min: float) -> np.ndarray:
        """
        depth: GEBCO convention (negative ocean, positive land/ice).
        h_min: minimum acceptable depth in meters (positive).
        Returns bool mask where ocean & |depth| >= h_min.
        """
        return sea_mask & (depth <= -h_min)

    @staticmethod
    def make_ice_mask(
        sic: np.ndarray,
        sea_mask: np.ndarray,
        C_thr: float,
    ) -> np.ndarray:
        """
        SIC threshold in fraction (e.g. 0.15 for 15%).
        """
        return sea_mask & (sic < C_thr)

    @staticmethod
    def make_joint_mask(
        depth: np.ndarray,
        sic: np.ndarray,
        sea_mask: np.ndarray,
        h_min: float,
        C_thr: float,
    ) -> np.ndarray:
        depth_mask = MaskFactory.make_depth_mask(depth, sea_mask, h_min)
        ice_mask = MaskFactory.make_ice_mask(sic, sea_mask, C_thr)
        return depth_mask & ice_mask


# ============================================================
# 4. Connected components (2D grid)
# ============================================================

@dataclass
class ComponentAnalysis:
    labels: np.ndarray  # int array of same shape
    n_components: int


def label_connected_components(mask: np.ndarray, connectivity: int = 8) -> ComponentAnalysis:
    """
    Label connected components in a 2D boolean mask.
    connectivity: 4 or 8.
    Returns labels and number of components.
    """
    ny, nx = mask.shape
    labels = np.zeros_like(mask, dtype=np.int32)
    current_label = 0

    if connectivity == 4:
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1),
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for i in range(ny):
        for j in range(nx):
            if not mask[i, j] or labels[i, j] != 0:
                continue

            current_label += 1
            # BFS / DFS
            stack = [(i, j)]
            labels[i, j] = current_label

            while stack:
                ci, cj = stack.pop()
                for di, dj in neighbors:
                    ni, nj = ci + di, cj + dj
                    if 0 <= ni < ny and 0 <= nj < nx:
                        if mask[ni, nj] and labels[ni, nj] == 0:
                            labels[ni, nj] = current_label
                            stack.append((ni, nj))

    return ComponentAnalysis(labels=labels, n_components=current_label)


# ============================================================
# 5. A* routing on the grid
# ============================================================

@dataclass
class RouteResult:
    path_indices: Optional[List[Tuple[int, int]]]  # list of (i,j)
    distance_nm: Optional[float]
    success: bool


def great_circle_distance_nm(
    lat1_deg: float, lon1_deg: float,
    lat2_deg: float, lon2_deg: float
) -> float:
    """
    Great-circle distance in nautical miles using spherical Earth approximation.
    """
    R_km = 6371.0
    deg2rad = np.pi / 180.0

    lat1 = lat1_deg * deg2rad
    lon1 = lon1_deg * deg2rad
    lat2 = lat2_deg * deg2rad
    lon2 = lon2_deg * deg2rad

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (np.sin(dlat / 2) ** 2 +
         np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2)
    c = 2 * np.arcsin(np.sqrt(a))
    dist_km = R_km * c
    return dist_km / 1.852  # km -> NM


class GridAStarRouter:
    """
    A* on a regular lat–lon grid with a feasibility mask.
    """

    def __init__(self, grid: RoutingGrid):
        self.grid = grid
        self.ny, self.nx = grid.lats_2d.shape

        # Pre-build neighbor offsets (8-connectivity)
        self.neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def _heuristic_nm(self, i: int, j: int, gi: int, gj: int) -> float:
        """Admissible heuristic: GC distance from node to goal."""
        return great_circle_distance_nm(
            self.grid.lats_2d[i, j],
            self.grid.lons_2d[i, j],
            self.grid.lats_2d[gi, gj],
            self.grid.lons_2d[gi, gj],
        )

    def _edge_cost_nm(self, i1: int, j1: int, i2: int, j2: int) -> float:
        """GC distance between adjacent grid cell centers."""
        return great_circle_distance_nm(
            self.grid.lats_2d[i1, j1],
            self.grid.lons_2d[i1, j1],
            self.grid.lats_2d[i2, j2],
            self.grid.lons_2d[i2, j2],
        )

    def route(
        self,
        feasible_mask: np.ndarray,
        start: Tuple[int, int],
        goal: Tuple[int, int],
    ) -> RouteResult:
        """
        Run A* on feasible_mask (bool) between start and goal indices (i,j).

        Returns RouteResult with path and distance in NM, or success=False if no path.
        """
        si, sj = start
        gi, gj = goal
        if not feasible_mask[si, sj] or not feasible_mask[gi, gj]:
            return RouteResult(path_indices=None, distance_nm=None, success=False)

        # A* bookkeeping
        open_set = []
        heapq.heappush(open_set, (0.0, (si, sj)))
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

        g_score = np.full_like(feasible_mask, np.inf, dtype=float)
        g_score[si, sj] = 0.0

        f_score = np.full_like(feasible_mask, np.inf, dtype=float)
        f_score[si, sj] = self._heuristic_nm(si, sj, gi, gj)

        visited = np.zeros_like(feasible_mask, dtype=bool)

        while open_set:
            _, (ci, cj) = heapq.heappop(open_set)
            if visited[ci, cj]:
                continue
            visited[ci, cj] = True

            if (ci, cj) == (gi, gj):
                # reconstruct path
                path = [(ci, cj)]
                while (ci, cj) != (si, sj):
                    ci, cj = came_from[(ci, cj)]
                    path.append((ci, cj))
                path.reverse()

                # compute distance
                dist_nm = 0.0
                for (i1, j1), (i2, j2) in zip(path[:-1], path[1:]):
                    dist_nm += self._edge_cost_nm(i1, j1, i2, j2)

                return RouteResult(path_indices=path, distance_nm=dist_nm, success=True)

            # explore neighbors
            for di, dj in self.neighbors:
                ni, nj = ci + di, cj + dj
                if not (0 <= ni < self.ny and 0 <= nj < self.nx):
                    continue
                if not feasible_mask[ni, nj]:
                    continue

                tentative_g = g_score[ci, cj] + self._edge_cost_nm(ci, cj, ni, nj)
                if tentative_g < g_score[ni, nj]:
                    came_from[(ni, nj)] = (ci, cj)
                    g_score[ni, nj] = tentative_g
                    h = self._heuristic_nm(ni, nj, gi, gj)
                    f_score[ni, nj] = tentative_g + h
                    heapq.heappush(open_set, (f_score[ni, nj], (ni, nj)))

        # no path found
        return RouteResult(path_indices=None, distance_nm=None, success=False)


# ============================================================
# 6. Diagnostics for routes and components
# ============================================================

@dataclass
class RouteDiagnostics:
    D_route_nm: Optional[float]
    D_gc_nm: float
    rho: Optional[float]
    min_depth_m: Optional[float] = None
    mean_depth_m: Optional[float] = None
    max_depth_m: Optional[float] = None


def great_circle_between_indices_nm(
    grid: RoutingGrid,
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> float:
    si, sj = start
    gi, gj = goal
    return great_circle_distance_nm(
        grid.lats_2d[si, sj],
        grid.lons_2d[si, sj],
        grid.lats_2d[gi, gj],
        grid.lons_2d[gi, gj],
    )


def compute_route_diagnostics(
    grid: RoutingGrid,
    bathy: BathymetryField,
    start: Tuple[int, int],
    goal: Tuple[int, int],
    route: RouteResult,
) -> RouteDiagnostics:
    """Compute D_route, D_GC, rho, and depth stats along route (if available)."""
    D_gc = great_circle_between_indices_nm(grid, start, goal)

    if not route.success or route.path_indices is None:
        return RouteDiagnostics(
            D_route_nm=None,
            D_gc_nm=D_gc,
            rho=None,
            min_depth_m=None,
            mean_depth_m=None,
            max_depth_m=None,
        )

    D_route = route.distance_nm
    rho = D_route / D_gc

    # depth stats along path
    depths = [bathy.depth[i, j] for (i, j) in route.path_indices]
    depths_arr = np.array(depths)
    # depths are negative (ocean); convert to meters (still negative, but we can keep as is)
    min_depth = float(depths_arr.min())
    mean_depth = float(depths_arr.mean())
    max_depth = float(depths_arr.max())

    return RouteDiagnostics(
        D_route_nm=D_route,
        D_gc_nm=D_gc,
        rho=rho,
        min_depth_m=min_depth,
        mean_depth_m=mean_depth,
        max_depth_m=max_depth,
    )


@dataclass
class IceConnectivitySummary:
    date: dt.date
    C_thr: float
    sea_fraction: float
    ice_safe_fraction: float
    n_components: int
    route_exists: bool
    D_route_nm: Optional[float]
    rho: Optional[float]


# ============================================================
# 7. Example high-level experiment helpers
# ============================================================

class ExperimentRunner:
    """
    Wrapper with convenience methods that reproduce
    the experiments from your paper:
    - sea-only baseline
    - depth thresholds
    - seasonal ice opening (fixed SIC threshold)
    - threshold sensitivity (fixed date, varying SIC)
    - joint depth+ice feasibility.
    """

    def __init__(
        self,
        data_manager: DataManager,
        bathy: BathymetryField,
        C_thr_default: float = 0.15,
        h_min_default: float = 20.0,
    ):
        self.dm = data_manager
        self.grid = data_manager.grid
        self.bathy = bathy
        self.C_thr_default = C_thr_default
        self.h_min_default = h_min_default

        # canonical OD indices: closest cell to your chosen coordinates
        self.start_idx = self._find_nearest_cell(40.5, -19.5)
        self.goal_idx = self._find_nearest_cell(69.5, 179.5)

        self.router = GridAStarRouter(self.grid)

    # ------------- utilities -------------

    def _find_nearest_cell(self, lat: float, lon: float) -> Tuple[int, int]:
        """Find closest grid cell to given lat/lon (deg)."""
        dlat = self.grid.lats_2d - lat
        dlon = self.grid.lons_2d - lon
        dist2 = dlat**2 + dlon**2
        idx_flat = np.argmin(dist2)
        ny, nx = self.grid.lats_2d.shape
        i = idx_flat // nx
        j = idx_flat % nx
        return int(i), int(j)

    # ------------- sea-only baseline -------------

    def run_sea_only_baseline(self) -> RouteDiagnostics:
        sea_mask = self.bathy.sea_mask
        route = self.router.route(sea_mask, self.start_idx, self.goal_idx)
        return compute_route_diagnostics(self.grid, self.bathy,
                                         self.start_idx, self.goal_idx, route)

    # ------------- depth thresholds -------------

    def depth_connectivity_curve(self, h_min_values: List[float]) -> Dict[float, Dict]:
        """
        For each h_min, compute:
          - fraction of sea that is depth-safe
          - number of components
          - whether OD in same component
        """
        result = {}
        sea_mask = self.bathy.sea_mask

        for h_min in h_min_values:
            depth_mask = MaskFactory.make_depth_mask(
                self.bathy.depth, sea_mask, h_min
            )
            sea_fraction = sea_mask.mean()
            depth_safe_fraction = depth_mask.mean()

            comp = label_connected_components(depth_mask)
            labels = comp.labels
            ncomp = comp.n_components

            si, sj = self.start_idx
            gi, gj = self.goal_idx
            lab_s = labels[si, sj]
            lab_g = labels[gi, gj]
            route_possible = (lab_s != 0) and (lab_s == lab_g)

            result[h_min] = dict(
                depth_safe_fraction=float(depth_safe_fraction),
                sea_fraction=float(sea_fraction),
                n_components=int(ncomp),
                route_possible=bool(route_possible),
            )

        return result

    # ------------- seasonal ice opening -------------

    def seasonal_ice_opening(
        self,
        dates: List[dt.date],
        C_thr: Optional[float] = None,
    ) -> List[IceConnectivitySummary]:
        if C_thr is None:
            C_thr = self.C_thr_default

        summaries: List[IceConnectivitySummary] = []
        sea_mask = self.bathy.sea_mask
        D_gc = great_circle_between_indices_nm(self.grid, self.start_idx, self.goal_idx)

        for date in dates:
            sic_field = self.dm.get_sic_for_date(date)
            ice_safe = MaskFactory.make_ice_mask(
                sic_field.sic, sea_mask, C_thr
            )

            sea_fraction = float(sea_mask.mean())
            ice_safe_fraction = float(ice_safe.mean())

            comp = label_connected_components(ice_safe)
            labels = comp.labels
            ncomp = comp.n_components

            si, sj = self.start_idx
            gi, gj = self.goal_idx
            lab_s = labels[si, sj]
            lab_g = labels[gi, gj]
            same_comp = (lab_s != 0) and (lab_s == lab_g)

            if same_comp:
                route = self.router.route(ice_safe, self.start_idx, self.goal_idx)
                if route.success:
                    D_route = float(route.distance_nm)
                    rho = float(D_route / D_gc)
                    route_exists = True
                else:
                    D_route = None
                    rho = None
                    route_exists = False
            else:
                route_exists = False
                D_route = None
                rho = None

            summaries.append(
                IceConnectivitySummary(
                    date=date,
                    C_thr=C_thr,
                    sea_fraction=sea_fraction,
                    ice_safe_fraction=ice_safe_fraction,
                    n_components=ncomp,
                    route_exists=route_exists,
                    D_route_nm=D_route,
                    rho=rho,
                )
            )

        return summaries

    # ------------- SIC threshold sensitivity (single date) -------------

    def threshold_sensitivity_single_date(
        self,
        date: dt.date,
        thresholds: List[float],
    ) -> List[IceConnectivitySummary]:
        sea_mask = self.bathy.sea_mask
        sic_field = self.dm.get_sic_for_date(date)
        D_gc = great_circle_between_indices_nm(self.grid, self.start_idx, self.goal_idx)

        results: List[IceConnectivitySummary] = []
        for C_thr in thresholds:
            ice_safe = MaskFactory.make_ice_mask(sic_field.sic, sea_mask, C_thr)

            sea_fraction = float(sea_mask.mean())
            ice_safe_fraction = float(ice_safe.mean())

            comp = label_connected_components(ice_safe)
            labels = comp.labels
            ncomp = comp.n_components

            si, sj = self.start_idx
            gi, gj = self.goal_idx
            lab_s = labels[si, sj]
            lab_g = labels[gi, gj]
            same_comp = (lab_s != 0) and (lab_s == lab_g)

            if same_comp:
                route = self.router.route(ice_safe, self.start_idx, self.goal_idx)
                if route.success:
                    D_route = float(route.distance_nm)
                    rho = float(D_route / D_gc)
                    route_exists = True
                else:
                    D_route = None
                    rho = None
                    route_exists = False
            else:
                route_exists = False
                D_route = None
                rho = None

            results.append(
                IceConnectivitySummary(
                    date=date,
                    C_thr=C_thr,
                    sea_fraction=sea_fraction,
                    ice_safe_fraction=ice_safe_fraction,
                    n_components=ncomp,
                    route_exists=route_exists,
                    D_route_nm=D_route,
                    rho=rho,
                )
            )

        return results

    # ------------- SIC threshold sensitivity (date × threshold matrix) -------------

    def threshold_sensitivity_matrix(
        self,
        dates: List[dt.date],
        thresholds: List[float],
    ) -> Dict[Tuple[dt.date, float], IceConnectivitySummary]:
        """
        Produces the date × threshold matrix that backs your heatmap:
        keys are (date, C_thr), values are IceConnectivitySummary.
        """
        out: Dict[Tuple[dt.date, float], IceConnectivitySummary] = {}
        for date in dates:
            res = self.threshold_sensitivity_single_date(date, thresholds)
            for summary in res:
                out[(summary.date, summary.C_thr)] = summary
        return out

    # ------------- Joint depth + ice mask -------------

    def joint_feasibility_snapshot(
        self,
        date: dt.date,
        h_min: Optional[float] = None,
        C_thr: Optional[float] = None,
    ) -> Tuple[np.ndarray, ComponentAnalysis, bool]:
        """
        Build joint depth+ice mask for a given date and thresholds,
        and return:
          - joint mask (bool)
          - component analysis
          - route_exists flag (OD in same joint-safe component)
        """
        if h_min is None:
            h_min = self.h_min_default
        if C_thr is None:
            C_thr = self.C_thr_default

        sic_field = self.dm.get_sic_for_date(date)
        sea_mask = self.bathy.sea_mask
        joint_mask = MaskFactory.make_joint_mask(
            self.bathy.depth, sic_field.sic, sea_mask, h_min, C_thr
        )

        comp = label_connected_components(joint_mask)
        labels = comp.labels
        si, sj = self.start_idx
        gi, gj = self.goal_idx
        lab_s = labels[si, sj]
        lab_g = labels[gi, gj]
        route_exists = (lab_s != 0) and (lab_s == lab_g)

        return joint_mask, comp, route_exists