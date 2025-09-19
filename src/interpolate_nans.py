#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: interpolate_nans.py

Description: Interpolate NANs.

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class InterpolateNANs(BaseEstimator, TransformerMixin):
    """Interpolate Empty Cells.

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
            Original dataframe with the NANs filled using back-fill method for initial NANs and followed by linear interpolation.
        """
        return X.bfill().interpolate(method='linear')