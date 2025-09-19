#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: transform_to_int.py

Description: Transform datatype to int.

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class TransformToInt(BaseEstimator, TransformerMixin):
    """Transform datatype to object.

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
            Dataframe with following column: `position`.
        
        Returns
        -------
        DataFrame   
            Original dataframe with the following object columns transformed to float: `port_name_encode`, `year`, `month`, `day`
        """
        columns_object_to_int= ["wind_force", "swell_force", "month", "day"]
        X[columns_object_to_int]= X[columns_object_to_int].astype(int)
        return X