#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: extract_era.py

Description: Extract ERA5 Climate Data.

Author: Abdella Mohamed
"""
from time import time 
from typing_extensions import Self
import voyage_optimization.paper_1
from voyage_optimization.paper_1.utils.log_cfg import logger
import cdsapi
from pathlib import Path
import voyage_optimization.paper_1


# #################################################################################################################################################
# ############################################################### Setup ###########################################################################

PACKAGE_ROOT=Path(voyage_optimization.paper_1.__file__).resolve().parent
PRODUCT_NAME= "reanalysis-era5-single-levels"
VARIABLES= [
            '100m_u_component_of_wind', '100m_v_component_of_wind', '10m_u_component_of_neutral_wind',
            '10m_u_component_of_wind', '10m_v_component_of_neutral_wind', '10m_v_component_of_wind',
            '10m_wind_gust_since_previous_post_processing', '2m_dewpoint_temperature', '2m_temperature',
            'air_density_over_the_oceans', 'coefficient_of_drag_with_waves', 'convective_snowfall',
            'convective_snowfall_rate_water_equivalent', 'free_convective_velocity_over_the_oceans', 'ice_temperature_layer_1',
            'ice_temperature_layer_2', 'ice_temperature_layer_3', 'ice_temperature_layer_4',
            'instantaneous_10m_wind_gust', 'large_scale_snowfall', 'large_scale_snowfall_rate_water_equivalent',
            'maximum_2m_temperature_since_previous_post_processing', 'maximum_individual_wave_height', 'mean_direction_of_total_swell',
            'mean_direction_of_wind_waves', 'mean_period_of_total_swell', 'mean_period_of_wind_waves',
            'mean_sea_level_pressure', 'mean_square_slope_of_waves', 'mean_wave_direction',
            'mean_wave_direction_of_first_swell_partition', 'mean_wave_direction_of_second_swell_partition', 'mean_wave_direction_of_third_swell_partition',
            'mean_wave_period', 'mean_wave_period_based_on_first_moment', 'mean_wave_period_based_on_first_moment_for_swell',
            'mean_wave_period_based_on_first_moment_for_wind_waves', 'mean_wave_period_based_on_second_moment_for_swell', 'mean_wave_period_based_on_second_moment_for_wind_waves',
            'mean_wave_period_of_first_swell_partition', 'mean_wave_period_of_second_swell_partition', 'mean_wave_period_of_third_swell_partition',
            'mean_zero_crossing_wave_period', 'minimum_2m_temperature_since_previous_post_processing', 'model_bathymetry',
            'normalized_energy_flux_into_ocean', 'normalized_energy_flux_into_waves', 'normalized_stress_into_ocean',
            'ocean_surface_stress_equivalent_10m_neutral_wind_direction', 'ocean_surface_stress_equivalent_10m_neutral_wind_speed', 'peak_wave_period',
            'period_corresponding_to_maximum_individual_wave_height', 'sea_surface_temperature', 'significant_height_of_combined_wind_waves_and_swell',
            'significant_height_of_total_swell', 'significant_height_of_wind_waves', 'significant_wave_height_of_first_swell_partition',
            'significant_wave_height_of_second_swell_partition', 'significant_wave_height_of_third_swell_partition', 'skin_temperature',
            'snow_albedo', 'snow_density', 'snow_depth',
            'snow_evaporation', 'snowfall', 'snowmelt',
            'surface_pressure', 'temperature_of_snow_layer', 'total_column_snow_water',
            'wave_spectral_directional_width', 'wave_spectral_directional_width_for_swell', 'wave_spectral_directional_width_for_wind_waves',
            'wave_spectral_kurtosis', 'wave_spectral_peakedness', 'wave_spectral_skewness',
        ]

AREA= [56, -43, -36, 132]
YEARS= [2021, 2022]
MONTHS= [[11, 12], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]] 
DOWNLOAD_LOCATION= PACKAGE_ROOT / "data/test"

# #################################################################################################################################################
# ############################################################### Setup Ends ######################################################################


class ExtractERA:


    def __init__(self, product_name, variables, area_counterclockwise) -> Self:
        """Extract Climate Data from ERA5 Store.

        Parameters
        ----------
        product_name : str
            Name of ERA5 Product.
        variables : List
            List of variables subset to extract.
        area_counterclockwise : List
            Geographical area to consider counterclockwise i.e North, West, South, East.

        Returns
        -------
        Self
            Instance with request meta.
        
        Notes
        -----
        - For establishing connection to ERA5. A config hidden file with the name .cdsapirc and enteries `url` and `key` have to be saved in home directory of user. For more please visit -> https://cds.climate.copernicus.eu/api-how-to 
        """
        assert isinstance(product_name, str)
        assert isinstance(variables, list)
        assert isinstance(area_counterclockwise, list)

        self.product_name= product_name
        self.variables= variables
        self.area_counterclockwise= area_counterclockwise # N W S E
        self.request_meta= ["product_type", "format", "variable", "grid", "area"]
        self.request_meta_values= ["reanalysis", "grib", self.variables, [0.25, 0.25], self.area_counterclockwise]
        self.request= { meta:value for meta, value in zip(self.request_meta, self.request_meta_values) }
        
    def extract_data_by_year_and_month(self, year: int, month: int, download_file_path: str) -> None:
        """Extract Monthly Data for all days in hourly frequency.

        Parameters
        ----------
        year : int
            year to consider
        month : int
            month to consider
        download_file_path : str
            file path

        Returns
        -------
        None
            Function with side effect only of data download to disk.
        
        Notes
        -----
        - we cant just start from mid of the days for a month and for another month all therefore extract for all months
        - time window meta is aligned in this function 

        """
        assert isinstance(year, int)
        assert isinstance(month, int)
        assert isinstance(download_file_path, str)

        self.request["year"]= str(year)
        self.request["month"]= str(month)
        self.request["day"]= [
                            '01', '02', '03', 
                            '04', '05', '06',
                            '07', '08', '09',
                            '10', '11', '12',
                            '13', '14', '15',
                            '16', '17', '18',
                            '19', '20', '21',
                            '22', '23', '24',
                            '25', '26', '27',
                            '28', '29', '30',
                        ]
        self.request["time"]= [
                            '00:00', '01:00', '02:00',
                            '03:00', '04:00', '05:00',
                            '06:00', '07:00', '08:00',
                            '09:00', '10:00', '11:00',
                            '12:00', '13:00', '14:00',
                            '15:00', '16:00', '17:00',
                            '18:00', '19:00', '20:00',
                            '21:00', '22:00', '23:00']
        
        try:
            client = cdsapi.Client()
            client.retrieve(name=self.product_name, request=self.request, target=f"{download_file_path}.{self.request['format']}")
        except Exception as ee:
            logger.error(ee)
# #################################################################################################################################################
# ############################################################### Entrypoint ######################################################################
if __name__ == "__main__":
    era_extractor= ExtractERA(PRODUCT_NAME, VARIABLES, AREA)

    tic= time()
    for year in YEARS:
        if year == 2021:
            months= MONTHS[0]
        else: #2022
            months= MONTHS[1]
        for month in months:
           logger.debug(f"Extracting for year: {year} and month: {month}")
           era_extractor.extract_data_by_year_and_month(year, month, download_file_path=f"{DOWNLOAD_LOCATION} / {year}{month}")
           toc= time()
           logger.debug(f"Extraction Done for year: {year} and month: {month}. Elapsed Time: {toc-tic/60} minutes")
           logger.debug(f"===========================================================================================")
    
    toc= time()
    logger.debug(f"All Extraction Done. Elapsed Time: {toc-tic/60} minutes")
