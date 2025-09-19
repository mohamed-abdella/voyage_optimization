#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: outliers_remover.py

Description: Remove Outliers in the Response Column. 

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from numpy import hstack
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class OutliersRemover(BaseEstimator, TransformerMixin):
    def __init__(self, target_name: str, method: str = "iqr", tolerance: float = 1.5) -> Self:
        """Remove Outliers in the Response Column.

        Parameters
        ----------
        BaseEstimator : sklearn base inheritance for pipelines
        TransformerMixin : sklearn transformer inheritance for pipelines
        """
        self.target_name= target_name
        self.method= method
        self.tolerance= tolerance

    def fit(self, X: DataFrame, y: Series = None):
        return self

    def transform(self, X: DataFrame, y: Series = None):
        """Remove Outliers in the Response Column.

        Parameters
        ----------
        X : DataFrame
        
        Returns
        -------
        DataFrame
          Original dataframe with X rows droped as outliers in the response.
        """
        outliers_indices= self._identify_univariate_outliers(X)
        return X.drop(outliers_indices, axis="index")
        
    def _identify_univariate_outliers(self, X: DataFrame) -> list:
    
        if self.method in "iqr":
            q1= X[self.target_name].quantile(.25)
            q3= X[self.target_name].quantile(.75)
            iqr= q3 - q1
            lower_boundary= q1 - 1.5 * iqr
            upper_boundary= q3 + 1.5 * iqr
            outliers_df = X[(X[self.target_name] < lower_boundary) | (X[self.target_name] > upper_boundary)]
        return outliers_df.index