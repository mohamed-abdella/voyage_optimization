#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: derive_date_components.py

Description: Derive Date Components from date

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class DeriveDateComponents(BaseEstimator, TransformerMixin):
    """Derive Date Components from date.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame) -> DataFrame:
        """Derive Date Components

        Parameters
        ----------
        X : DataFrame

        Returns
        -------
        DataFrame   
            Original dataframe with the additional columns: `year`, `month`, `day`, `season`.
        
        Notes
        -------
        - Season column is derived based on the heimsphere info and the month
        """
        X["year"]= X.index.year
        X["month"]= X.index.month
        X["day"]= X.index.day

        seasons_northernheimsphere= {1: "winter", 
                                     2: "winter", 
                                     3: "spring", 
                                     4: "spring", 
                                     5: "spring", 
                                     6: "summer", 
                                     7: "summer", 
                                     8: "summer", 
                                     9: "autumn", 
                                     10: "autumn", 
                                     11: "autumn", 
                                     12: "winter"
                                    }
        
        seasons_southernheimsphere= {1: "summer", 
                                     2: "summer", 
                                     3: "autumn", 
                                     4: "autumn", 
                                     5: "autumn", 
                                     6: "winter", 
                                     7: "winter", 
                                     8: "winter", 
                                     9: "spring", 
                                     10: "spring", 
                                     11: "spring", 
                                     12: "summer"
                                    }
        
        X["season"]= [ seasons_northernheimsphere[month] if heimsphere == "N" else seasons_southernheimsphere[month] for heimsphere, month in zip(X.latitude_direction, X.index.month) ]
        return X