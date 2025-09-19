#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: derive_voyage_segments.py

Description: Derive Voyage Segments

Author: Abdella Mohamed
"""
from pandas import DataFrame, Series
from typing_extensions import Self
from sklearn.base import BaseEstimator, TransformerMixin


class DeriveVoyageSegments(BaseEstimator, TransformerMixin):
    """Derive Voyage Segments.

    Parameters
    ----------
    BaseEstimator : sklearn base inheritance for pipelines
    TransformerMixin : sklearn transformer inheritance for pipelines
    """
    def fit(self, X: DataFrame, y: Series= None) -> Self:
        return self 

    def transform(self, X: DataFrame):
        """Derive Voyage Segments based on Ports Switch.      

        Parameters
        ----------
        X : DataFrame
            Dataframe with following columns: `next_port_name`
        
        Returns
        -------
        DataFrame   
            Original dataframe with additional columns `port_name_encode` and `voyages`.
        """
        encoder= dict()
        voyages= []
        new_voyage= 1
        
        ports= X.next_port_name.unique()
        
        for encode, port_name in enumerate(ports):
            encode += 1 # start from 1
            encoder[port_name]= encode
        
        def encode(port_name):
            return encoder[port_name]
        
        X["port_name_encode"]= X.next_port_name.apply(encode)
        
        for idx, encode in enumerate(X.port_name_encode):
            if idx != 0: # skip first element
                if X.port_name_encode[idx] != X.port_name_encode[idx-1]:
                    new_voyage += 1
                    voyages.append(new_voyage)
                else:
                    voyages.append(voyages[idx-1])
            else:
                voyages.append(new_voyage)
        X["voyages"]= voyages
        return X