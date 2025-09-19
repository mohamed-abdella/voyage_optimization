#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: derive_total_fuel.py

Description: Derive Total Fuel

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class DeriveTotalFuel(BaseEstimator, TransformerMixin):
    """Derive Total Fuel.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame):
        """Derive Total Fuel.      

        Parameters
        ----------
        X : DataFrame
            Dataframe with following columns: ['uls_fo_bunker_consumption_last_24h_main_engine', 'mgo_bunker_consumption_last_24h_main_engine', 'uls_fo_bunker_consumption_last_24h_boiler',  'mgo_bunker_consumption_last_24h_boiler', 'uls_fo_bunker_consumption_last_24h_auxiliary', 'mgo_bunker_consumption_last_24h_auxiliary']
        
        Returns
        -------
        DataFrame   
            Original dataframe with additional column `total_fuel`.
        """
        columns_to_use= ['uls_fo_bunker_consumption_last_24h_main_engine', 'mgo_bunker_consumption_last_24h_main_engine', 'uls_fo_bunker_consumption_last_24h_boiler', 'mgo_bunker_consumption_last_24h_boiler', 'uls_fo_bunker_consumption_last_24h_auxiliary', 'mgo_bunker_consumption_last_24h_auxiliary']

        X["total_fuel"]= X[[columns_to_use[0], columns_to_use[1], columns_to_use[2], columns_to_use[3], columns_to_use[4], columns_to_use[5]]].sum(axis=1)
        return X