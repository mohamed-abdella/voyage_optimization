#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: rename_columns.py

Description: Rename Columns.

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class RenameColumns(BaseEstimator, TransformerMixin):
    """Rename Columns.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None):
        return self 

    def transform(self, X: DataFrame):
        """Rename Original Columns of the inpute Data.

        Parameters
        ----------
        X : DataFrame
        
        Returns
        -------
        DataFrame
          Original dataframe with modified column names.
        """
        X= X[2:] 
        column_names= ["position", "current_speed_over_ground", "average_speed_over_ground_last_24h", "average_speed_since_departure", "average_rpm_last_24h", 
          "slip", "wind_direction", "wind_force", "swell_direction", "swell_force", "current_direction", "current_speed(knots)", "current_adverse_favorable", 
          "uls_fo_bunker_consumption_last_24h_main_engine","uls_fo_bunker_consumption_last_24h_boiler", "uls_fo_bunker_consumption_last_24h_auxiliary", 
           "mgo_bunker_consumption_last_24h_main_engine", "mgo_bunker_consumption_last_24h_boiler", "mgo_bunker_consumption_last_24h_auxiliary", 
          "bunkers_rob_uls_fo<0.5%s", "bunkers_rob_vlsfo<0.5%s", "bunkers_rob_lsmgo<0.1%s", "fw_rob", "next_port_name", "next_port_dtg", "next_port_eta", "draft_current_fwd/aft", 
          "draft_arrival_fwd/aft", "suppliers_required_in_next_port"]
        X.columns= column_names
        X.index.name= "date"
        return X