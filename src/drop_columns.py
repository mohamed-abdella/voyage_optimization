#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: drop_columns.py

Description: Drop Columns.

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class DropColumns(BaseEstimator, TransformerMixin):
    """Drop Columns.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame):
        """Drop columns.         

        Parameters
        ----------
        X : DataFrame
            Dataframe with following columns to drop: 
                - without use: `current_speed_over_ground`, `average_speed_since_departure`, `bunkers_rob_uls_fo<0.5%s`, `bunkers_rob_vlsfo<0.5%s`, `bunkers_rob_lsmgo<0.1%s`, `fw_rob`, `suppliers_required_in_next_port`
                - after usage: `uls_fo_bunker_consumption_last_24h_main_engine`, `mgo_bunker_consumption_last_24h_main_engine`, `uls_fo_bunker_consumption_last_24h_boiler`, `mgo_bunker_consumption_last_24h_boiler`, `uls_fo_bunker_consumption_last_24h_auxiliary`, `mgo_bunker_consumption_last_24h_auxiliary`
        Returns
        -------
        DataFrame   
            Original dataframe minus 13 columns removed.
        """
        columns_to_drop= [
            "current_speed_over_ground", 
            "average_speed_since_departure", 
            "bunkers_rob_uls_fo<0.5%s", 
            "bunkers_rob_vlsfo<0.5%s", 
            "bunkers_rob_lsmgo<0.1%s", 
            "fw_rob",
            "suppliers_required_in_next_port"
        ] 

        columns_to_drop_after_use= ['uls_fo_bunker_consumption_last_24h_main_engine', 
                                    'mgo_bunker_consumption_last_24h_main_engine', 
                                    'uls_fo_bunker_consumption_last_24h_boiler', 
                                    'mgo_bunker_consumption_last_24h_boiler',
                                    'uls_fo_bunker_consumption_last_24h_auxiliary', 
                                    'mgo_bunker_consumption_last_24h_auxiliary'
                                   ]
        
        # could be used and manipulated in next iterations 
        columns_to_drop_categorical= ['wind_direction', 'swell_direction', 'current_direction',
                                      'current_speed(knots)', 'current_adverse_favorable', 'next_port_name',
                                      'next_port_dtg', 'next_port_eta', 'latitude_direction',
                                      'longitude_direction', 'year', 'season', 'port_name_encode', 'voyages']

        columns_to_drop.extend(columns_to_drop_after_use)
        columns_to_drop.extend(columns_to_drop_categorical)

        return X.drop(columns_to_drop, axis=1)