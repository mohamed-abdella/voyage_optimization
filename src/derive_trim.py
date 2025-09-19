#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: derive_trim.py

Description: Derive Trim from Draft aft/forward.

Author: Abdella Mohamed
"""
from sklearn.base import BaseEstimator, TransformerMixin
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class DeriveTrim(BaseEstimator, TransformerMixin):
    """Derive Trim from Draft aft/forward.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame):
        """Derive Trim from Draft aft/forward.

        Parameters
        ----------
        X : DataFrame
            Dataframe with following columns: `draft_aft` and `draft_forward`.

        Returns
        -------
        DataFrame   
            Original dataframe with additional column `trim` based on the following formula: Trim= draft aft - draft forward.
        """
        X["trim"]= X["draft_aft"] - X["draft_forward"]
        return X

