#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: fuse_voyage_with_cmems.py

Description: Fuse Voyage with Ocean data from CMEMS.

Author: Abdella Mohamed
"""
from sklearn.base import BaseEstimator, TransformerMixin
from xarray import Dataset
from pandas import DataFrame, Series, to_datetime
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class FuseVoyageWithCMEMS(BaseEstimator, TransformerMixin):
    """Fuse Voyage with Ocean data from CMEMS.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def __init__(self, ocean_to_merge: Dataset) -> Self:
        self.ocean_to_merge= ocean_to_merge
    
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame) -> DataFrame:
        """Fuse Voyage with Ocean data from CMEMS.

        Parameters
        ----------
        X : DataFrame
        
        Returns
        -------
        DataFrame
          Original dataframe with additional columns from CMEMS products.
        """
        ocean_columns= ['ist',
                        'mlotst',
                        'pbo',
                        'siage',
                        'sialb',
                        'siconc',
                        'sisnthick',
                        'sithick',
                        'sivelo',
                        'sob',
                        'tob',
                        'usi',
                        'vsi',
                        'zos',
                        'so',
                        'thetao',
                        'uo',
                        'vo',
                        'wo'
                        ]
        ocean_columns_init= { column: 0.0 for column in ocean_columns }
        
        X= X.assign(**ocean_columns_init)
        self.ocean_to_merge= self.ocean_to_merge.sel(depth=0.494, method="nearest", drop=True) #drop depth
        X.index= to_datetime(X.index).normalize()
        for date, row in X.iterrows():
            for variable in ocean_columns_init.keys():    
                X.at[date, variable]= self.ocean_to_merge[variable].sel(time=date, 
                                                      latitude=round(row["latitude"], 4),
                                                      longitude=round(row["longitude"], 4), 
                                                      method="nearest")
        return X
