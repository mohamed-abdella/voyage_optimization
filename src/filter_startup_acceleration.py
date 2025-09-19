#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: filter_startup_acceleration.py

Description: Filter startup acceleration.

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class FilterStartupAcceleration(BaseEstimator, TransformerMixin):
    """Filter startup acceleration

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame) -> DataFrame:
        """Transform datatype to object.    

        Parameters
        ----------
        X : DataFrame
            Dataframe with following NANs.
        
        Returns
        -------
        DataFrame   
            Original dataframe with the main engine fuel min above 15 mt/day.
        """
        return X[X.fuel_main_engine > 15]