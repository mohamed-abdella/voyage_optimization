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


class ExpandDraft(BaseEstimator, TransformerMixin):
    """Expand Draft.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame):
        """Expand Draft into draft forward and draft aft.       

        Parameters
        ----------
        X : DataFrame
            Dataframe with following column: `draft_current_fwd/aft`
        
        Returns
        -------
        DataFrame   
            - Original dataframe with additional columns `draft_forward` and `draft_aft`  
            - Following columns are dropped `draft_current_fwd/aft` and `draft_arrival_fwd/aft`
        """
        X[["draft_forward", "draft_aft"]]= (X["draft_current_fwd/aft"].str.split("/", expand=True)).astype(float)
        return X.drop(["draft_current_fwd/aft", "draft_arrival_fwd/aft"], axis=1)