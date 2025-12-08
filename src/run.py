import xarray as xr
import datetime as dt

from core import (
    RoutingDomain, RoutingGrid, DataManager,
    ExperimentRunner
)

# 1) Build grid + load data
domain = RoutingDomain()
grid = RoutingGrid.from_domain(domain)

gebco_ds = xr.open_dataset("path/to/GEBCO_2024_subset.nc")
sic_ds   = xr.open_dataset("path/to/CMEMS_SIC_2018.nc")

dm = DataManager(grid, gebco_ds, sic_ds)
bathy = dm.get_bathymetry()

runner = ExperimentRunner(dm, bathy)

# 2) Baseline sea-only route
sea_only_diag = runner.run_sea_only_baseline()

# 3) Depth connectivity curve (for Fig. 4)
depth_results = runner.depth_connectivity_curve([20.0, 50.0, 200.0])

# 4) Seasonal ice opening (for Table 2 + Figs 5–6)
dates = [
    dt.date(2018, 6, 15),
    dt.date(2018, 7, 15),
    dt.date(2018, 8, 15),
    dt.date(2018, 9, 15),
]
seasonal_summaries = runner.seasonal_ice_opening(dates)

# 5) Threshold sensitivity (for Fig. 7, Fig. 8)
thresholds = [0.05, 0.10, 0.15, 0.30, 0.50]
sens_15sep = runner.threshold_sensitivity_single_date(dt.date(2018, 9, 15), thresholds)
sens_matrix = runner.threshold_sensitivity_matrix(dates, thresholds)

# 6) Joint mask snapshot (for Fig. 9)
joint_mask, joint_comp, joint_route_exists = runner.joint_feasibility_snapshot(
    dt.date(2018, 9, 15),
    h_min=20.0,
    C_thr=0.15
)