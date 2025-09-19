#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: create_samples.py

Description: Create Samples for KFold and Select Features. 


Author: Abdella Mohamed
"""
from pandas import DataFrame
from typing_extensions import Self, Tuple
from sklearn.model_selection import KFold

class CreateSamples:
    def __init__(self, target_name: str, folds: int, seed: int) -> Self:
        """Create Samples for KFold Evaluation

        Parameters
        ----------
        target_name : str
            Name of the response variable.
        folds : int
            Number of Folds
        seed : int
            Random state seed for reproducibility.

        Returns
        -------
        Self
        """
        self.target_name= target_name
        self.folds= folds
        self.seed= seed
        
    def create_k_fold_samples(self, df: DataFrame) -> Tuple:
        """Create K Folds Samples

        Parameters
        ----------
        df : DataFrame
            Data to use for sampling.

        Returns
        -------
        Tuple
            (X, y, kfold) => (Features series, response series, KFold sklearn instance)
        """
        X= df.drop(self.target_name, axis=1).values
        y= df[self.target_name].values
        kfold= KFold(n_splits= self.folds, shuffle= True, random_state= self.seed)
        return (X, y, kfold)