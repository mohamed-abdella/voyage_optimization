#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: derive_fuel_main_engine.py

Description: Derive Total Fuel of the Main Engine.


Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class DeriveFuelMainEngine(BaseEstimator, TransformerMixin):
    """Derive Total Fuel of the Main Engine.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame):
        """Derive Total Fuel of the Main Engine.       

        Parameters
        ----------
        X : DataFrame
            Dataframe with following columns: ['uls_fo_bunker_consumption_last_24h_main_engine', 'mgo_bunker_consumption_last_24h_main_engine']

        Returns
        -------
        DataFrame   
            Original dataframe with additional column `fuel_main_engine`.
        """
        columns_to_use= ['uls_fo_bunker_consumption_last_24h_main_engine', 'mgo_bunker_consumption_last_24h_main_engine']
        
        X["fuel_main_engine"]= X[[columns_to_use[0], columns_to_use[1]]].sum(axis=1)
        return X