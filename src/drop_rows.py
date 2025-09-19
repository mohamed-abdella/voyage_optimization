#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: drop_rows.py

Description: Drop Rows that are Completely Empty

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class DropRows(BaseEstimator, TransformerMixin):
    """Drop Rows that are Completely Empty.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame) -> DataFrame:
        """Drop Rows.         

        Parameters
        ----------
        X : DataFrame

        Returns
        -------
        DataFrame   
            Original dataframe minus X rows.
        
        Notes
        -----
        Droping rows where there are only operations change and no values in the fields which could be identified if the complete cells in the rows are empty
            - Loading Operation
            - Anchor
            - Bunkering Operation
            - Discharging Operation
            - VSL ANCHORED
            - Drifitng
        """
        rows_to_drop= X.index[X.isna().all(axis=1)].tolist()
        #print(f"Dropping {len(rows_to_drop)} rows") # add this as log info?
        return X.dropna(how="all")

        