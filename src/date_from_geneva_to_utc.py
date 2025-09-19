#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: date_from_geneva_to_utc.py

Description: Convert Date from Geneva to UTC format.

Author: Abdella Mohamed
"""
import pandas as pd
from pandas import DataFrame, Series
from typing import List
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class DateFromGenevaToUTC(BaseEstimator, TransformerMixin):
    """Convert Date from Geneva to UTC format.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        """Add fit abstract to be compatible with sklearn pipelines."""
        return self

    def transform(self, X: DataFrame) -> DataFrame:
        X.index= pd.to_datetime(X.index)
        X.index= [datetime.replace(hour=12) for datetime in X.index] 
        X.index= X.index - pd.Timedelta(hours=2)
        X.index.name= "date"
        return X