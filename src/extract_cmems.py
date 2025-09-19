#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: extract_cmems.py

Description: Extract CMEMS Ocean Data.

Author: Abdella Mohamed
"""
from collections import namedtuple
from voyage_optimization.paper_1.utils.log_cfg import logger
from typing import List, NamedTuple
import copernicusmarine
from time import time, sleep
from typing_extensions import Self
from pathlib import Path
import voyage_optimization.paper_1
# #################################################################################################################################################
# ############################################################### Setup ###########################################################################
PACKAGE_ROOT=Path(voyage_optimization.paper_1.__file__).resolve().parent
DATASETS_ID= [
    "cmems_mod_glo_phy_anfc_0.083deg_P1D-m", #only this is 2D, the rest are 3D
    "cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m", 
    "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m", 
    "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m", 
    "cmems_mod_glo_phy-wcur_anfc_0.083deg_P1D-m", 
]
Boundary= namedtuple("Boundary", "min_lat max_lat min_lon max_lon")
BOUNDARY= Boundary(-36, 56, -43, 132)
Depth= namedtuple("Depth", "min_depth max_depth")
DEPTH= Depth(0, 0.5)
START_DATE= "2021-11-16"
END_DATE= "2022-11-21"
BUFFER= 60 #buffer 60 seconds between consecutive requests to avoid requests drop by the server.
DOWNLOAD_LOCATION= PACKAGE_ROOT / "data/test"
# #################################################################################################################################################
# ############################################################### Setup Ends ######################################################################
class ExtractCMEMS:

    def __init__(self, datasets_id: List, boundary: NamedTuple, depth: NamedTuple) -> Self:
        """Extract Ocean Data from CMEMS Store.

        Parameters
        ----------
        datasets_id : List
            Datasets List to consider.
        boundary : NamedTuple
            Geographical boundary for latitude and longitude in the form: `min_lat`, `max_lat`, `min_lon`, `max_lon`
        depth : NamedTuple
            Ocean depth in the form: `min_depth` and `max_depth`.
        
        Notes
        -----
        - Datasets considered in this iteration are from Global Ocean Physics Analysis and Forecast. More info => https://catalogue.marine.copernicus.eu/documents/PUM/CMEMS-GLO-PUM-001-024.pdf
        - Surface level info is considered only in this iteration which means keep depth to 0.5
        - Possible depth ranges 0.5 → 5727.9 m
        - 5 Daily datasets in total
        - Another product in other iterations could be used is the waves product -> https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_WAV_001_027/description however we use now the waves variables from era5 instead
        - help guide in case of https://help.marine.copernicus.eu/en/articles/6135460-how-to-configure-a-simple-opendap-access-directly-in-python#h_31bea32555 
        - Zscaler specifically Internet security have to be disabled.  
        - Data/test folder is assumed to be present under the package root folder for the data to be downloaded to. 
        """
        assert isinstance(datasets_id, list)
        #assert isinstance(boundary, NamedTuple)
        #assert isinstance(depth, NamedTuple)

        self.datasets_id= datasets_id
        self.min_lat= boundary.min_lat
        self.max_lat= boundary.max_lat
        self.min_lon= boundary.min_lon
        self.max_lon= boundary.max_lon
        self.min_depth= depth.min_depth
        self.max_depth= depth.max_depth

    def extract_data(self, start_date: str, end_date: str) -> None:
        """Extract Data.

        Parameters
        ----------
        start_date : str
            Start of slice.
        end_date : str
            End of slice.
        """
        assert isinstance(start_date, str)
        assert isinstance(end_date, str)
        tic= time()

        # Authenticate to CMEMS using username and password. 
        try:
            copernicusmarine.login(skip_if_user_logged_in=True)
        except Exception as ee:
            logger.error(ee)

        for dataset in self.datasets_id:
            logger.debug(f"Extracting Dataset: {dataset} from: {start_date} to {end_date}")
            try:
                copernicusmarine.subset(
                    dataset_id= dataset,
                    minimum_longitude=self.min_lon,
                    maximum_longitude=self.max_lon,
                    minimum_latitude=self.min_lat,
                    maximum_latitude=self.max_lat,
                    start_datetime=start_date, #1 year data
                    end_datetime=end_date,
                    minimum_depth=0,
                    maximum_depth=0.5,
                    force_download=True, 
                    output_filename = f"{dataset}.nc",
                    output_directory = DOWNLOAD_LOCATION)
                sleep(BUFFER)
            except Exception as ee:
                logger.error(ee)
            toc= time()
            logger.debug(f"Extracting Complete for : {dataset} from: {start_date} to {end_date}. Elapsed time: {toc-tic/60} minutes.")
        toc= time()
        logger.debug(f"All Extracting Done. Elapsed Time: {toc-tic/60} minutes.")
# #################################################################################################################################################
# ############################################################### Entrypoint ######################################################################
if __name__ == "__main__":
    extractor= ExtractCMEMS(DATASETS_ID, BOUNDARY, DEPTH)
    extractor.extract_data(START_DATE, END_DATE)