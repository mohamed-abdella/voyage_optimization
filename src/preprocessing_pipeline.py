#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: preprocessing_pipeline.py

Description: Preprocessing and Fusing Pipeline.

Author: Abdella Mohamed
"""
##################################################################################
#  Import Libraries   
##################################################################################
from voyage_optimization.paper_1.preprocessing.rename_columns import RenameColumns
from voyage_optimization.paper_1.preprocessing.drop_rows import DropRows
from voyage_optimization.paper_1.preprocessing.date_from_geneva_to_utc import DateFromGenevaToUTC
from voyage_optimization.paper_1.preprocessing.filter_startup_acceleration import FilterStartupAcceleration
from voyage_optimization.paper_1.preprocessing.geolocation_from_dmm_to_dd import GeoLocationFromDMMToDD
from voyage_optimization.paper_1.preprocessing.expand_draft import ExpandDraft
from voyage_optimization.paper_1.preprocessing.derive_trim import DeriveTrim
from voyage_optimization.paper_1.preprocessing.derive_date_components import DeriveDateComponents
from voyage_optimization.paper_1.preprocessing.derive_fuel_main_engine import DeriveFuelMainEngine 
from voyage_optimization.paper_1.preprocessing.derive_total_fuel import DeriveTotalFuel
from voyage_optimization.paper_1.preprocessing.derive_voyage_segments import DeriveVoyageSegments
from voyage_optimization.paper_1.preprocessing.transform_to_float import TransformToFloat
from voyage_optimization.paper_1.preprocessing.transform_to_object import TransformToObject
from voyage_optimization.paper_1.preprocessing.transform_to_int import TransformToInt
from voyage_optimization.paper_1.preprocessing.interpolate_nans import InterpolateNANs
from voyage_optimization.paper_1.preprocessing.drop_columns import DropColumns
from voyage_optimization.paper_1.preprocessing.fuse_voyage_with_cmems import FuseVoyageWithCMEMS
from voyage_optimization.paper_1.preprocessing.fuse_voyage_with_era import FuseVoyageWithEra
from voyage_optimization.paper_1.preprocessing.outliers_remover import OutliersRemover
from voyage_optimization.paper_1.utils.log_cfg import logger
import voyage_optimization.paper_1

from sklearn.pipeline import Pipeline
from pathlib import Path 
import pandas as pd 
from xarray import open_mfdataset
##################################################################################
#  Constants  
##################################################################################
PACKAGE_ROOT=Path(voyage_optimization.paper_1.__file__).resolve().parent
DATA_INPUT= PACKAGE_ROOT / "data" / "raw"
DATA_OUTPUT= PACKAGE_ROOT / "data" / "processed"
CMEMS_FILES= [ff for ff in DATA_INPUT.glob(pattern="cmems*") ]
ERA_FILES= [ff for ff in DATA_INPUT.glob(pattern="era5*") ]
##################################################################################
#  Read Data   
##################################################################################
hercules= pd.read_excel(DATA_INPUT / "hercules.xlsx", index_col=0)
cmems= open_mfdataset(CMEMS_FILES)
era= open_mfdataset(ERA_FILES)
##################################################################################
#  Construct Pipeline   
##################################################################################
Preprocessing_Pipeline = Pipeline(steps=[
    ("Rename Columns", RenameColumns()), 
    ("Drop Rows", DropRows()), 
    ("Date From Geneva To UTC", DateFromGenevaToUTC()), 
    ("GeoLocation From DMM ToDD", GeoLocationFromDMMToDD()),
    ("Expand Draft", ExpandDraft()), 
    ("Derive Trim", DeriveTrim()), 
    ("Derive Date Components", DeriveDateComponents()), 
    ("Derive Fuel Main Engine", DeriveFuelMainEngine()), 
    ("Derive Total Fuel", DeriveTotalFuel()), 
    ("Derive Voyage Segments", DeriveVoyageSegments()), 
    ("Transform To Float", TransformToFloat()),
    ("Transform To Object", TransformToObject()),
    ("Transform To Int", TransformToInt()),
    ("Drop Columns", DropColumns()), 
    ("Fuse Voyage With CMEMS", FuseVoyageWithCMEMS(cmems)), 
    ("Fuse Voyage With ERA5", FuseVoyageWithEra(era)), 
    ("Interpolate NANs", InterpolateNANs()), 
    ("Outliers Remover in Response", OutliersRemover(target_name="total_fuel")), 
    ("Filter StartUp Acceleration", FilterStartupAcceleration())
])
##################################################################################
#  Run Pipeline   
##################################################################################
if __name__ == "__main__":
    df= Preprocessing_Pipeline.fit_transform(hercules)
    logger.debug(f"Read: {df.shape}")
    df.to_csv(f"{PACKAGE_ROOT}/data/test/preprocessed_data.csv")