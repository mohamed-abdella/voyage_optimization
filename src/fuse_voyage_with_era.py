#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: fuse_voyage_with_era.py

Description: Fuse Voyage with Climate data from ERA5.

Author: Abdella Mohamed
"""
from sklearn.base import BaseEstimator, TransformerMixin
from xarray import Dataset
from pandas import DataFrame, Series, to_datetime
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class FuseVoyageWithEra(BaseEstimator, TransformerMixin):
    """Fuse Voyage with Climate data from ERA5.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def __init__(self, era_to_merge: Dataset) -> Self:
        self.era_to_merge= era_to_merge
    
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame) -> DataFrame:
        """Fuse Voyage with Climate data from ERA5.

        Parameters
        ----------
        X : DataFrame
        
        Returns
        -------
        DataFrame
          Original dataframe with additional columns from ERA5 products.
        """
        variables_name_init= {var: 0.0 for var in self.era_to_merge.data_vars.keys()}
        
        X= X.assign(**variables_name_init)
        X.index= to_datetime(X.index).normalize()
        for date, row in X.iterrows():
            for variable in variables_name_init.keys():    
                X.at[date, variable]= self.era_to_merge[variable].sel(time=date, 
                                                      latitude=round(row["latitude"], 4),
                                                      longitude=round(row["longitude"], 4), 
                                                      method="nearest")
        return X
