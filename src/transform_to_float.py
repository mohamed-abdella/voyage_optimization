#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: transform_to_float.py

Description: Transform datatype to float.

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin

    
class TransformToFloat(BaseEstimator, TransformerMixin):
    """Transform datatype to float.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame) -> DataFrame:
        """Transform datatype to float    

        Parameters
        ----------
        X : DataFrame
        
        Returns
        -------
        DataFrame   
            Original dataframe with the following object columns transformed to float: `average_speed_over_ground_last_24h`, `average_rpm_last_24h`, `slip`, `fuel_main_engine`, `total_fuel`
        """
        columns_object_to_float= ["average_speed_over_ground_last_24h", 
                                  "average_rpm_last_24h", 
                                  "slip", 
                                  "fuel_main_engine", 
                                  "total_fuel"
                                 ]
        X[columns_object_to_float]= X[columns_object_to_float].astype(float)
        return X