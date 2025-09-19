#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: geolocation_from_dmm_to_dd.py

Description: Convert Geolocation from Degrees Decimal Minutes (DMM) to Decimal Degrees (DD) Format. 

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class GeoLocationFromDMMToDD(BaseEstimator, TransformerMixin):
    """Convert Geolocation from Degrees Decimal Minutes (DMM) to Decimal Degrees (DD) Format. 

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None):
        return self 

    def transform(self, X: DataFrame):
        """Convert Geolocation from Degrees Decimal Minutes (DMM) to Decimal Degrees (DD) Format.     

        Parameters
        ----------
        X : DataFrame
            Dataframe with following column: `position`.
        
        Returns
        -------
        DataFrame   
            - Original dataframe with additional columns `latitude`, `longitude`, `latitude_direction` and `longitude_direction`
            - Following columns are dropped `position`
        """
        X[["latitude", "longitude"]]= X.position.str.split("\n", expand=True)
        X[["latitude_deg", "latitude_sec"]]= X.latitude.str.split("-", expand=True)
        X[["longitude_deg", "longitude_sec"]]= X.longitude.str.split("-", expand=True)
        
        X["latitude_direction"]= X.latitude_sec.str.extract("([a-zA-Z]+)", expand=False)
        X["longitude_direction"]= X.longitude_sec.str.extract("([a-zA-Z]+)", expand=False)
        
        X.latitude_sec= X.latitude_sec.str.split("N|S|E|W",expand=True)[0]
        X.longitude_sec= X.longitude_sec.str.split("N|S|E|W",expand=True)[0]
        
        X.longitude_sec= X.longitude_sec.astype(float)
        # correcting a value manually as it failing the conversion to float.
        #2022-01-13    16.5. => 16.5 (remove dot)
        X.latitude_sec["2022-01-13"]= '16.5'
        X.latitude_sec= X.latitude_sec.astype(float)
        # convert degree str to float
        X.longitude_deg= X.longitude_deg.astype(float)
        # convert degree str to float
        X.latitude_deg= X.latitude_deg.astype(float)
        X.longitude_deg= X.longitude_deg.astype(float)        

        # convert from degree, seconds format to decimal values 
        # formula= degree + seconds/60 
        X["latitude"]= X[["latitude_deg", "latitude_sec"]].apply(lambda x: x[0] + x[1]/60.0, axis=1)
        X["longitude"]= X[["longitude_deg", "longitude_deg"]].apply(lambda x: x[0] + x[1]/60.0, axis=1)
        # add - to indicate directions in lat, lon
        X.latitude= X.apply(lambda X: X.latitude * -1 if X.latitude_direction == "S" else X.latitude, axis=1)
        X.longitude= X.apply(lambda X: X.longitude * -1 if X.longitude_direction == "W" else X.longitude, axis=1)
        
        # clean up - remove intermediate columns 
        intermediate_columns_to_drop= ["position", "latitude_deg", "latitude_sec", "longitude_deg", "longitude_sec"]
        return X.drop(intermediate_columns_to_drop, axis=1)