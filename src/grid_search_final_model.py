#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: grid_search_final_model.py

Description: Grid Search Final Model to find best Parameters and Features 

Author: Abdella Mohamed
"""
from typing import Dict, List 
from pathlib import Path 
from typing_extensions import Self
from pandas import DataFrame, Series
from numpy import array
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
import voyage_optimization.paper_1
from sklearn.ensemble import RandomForestRegressor

# #################################################################################################################################################
# ############################################################### Grid Parameters #################################################################
PACKAGE_ROOT=Path(voyage_optimization.paper_1.__file__).resolve().parent
# Define the parameter grid
HYPER_PARAMETERS = {
    'rf__n_estimators': [50, 100, 200],       # Number of trees
    'rf__max_depth': [None, 10, 20, 30],      # Maximum depth of each tree
    'rf__min_samples_split': [2, 5, 10],      # Minimum samples to split a node
    'rf__min_samples_leaf': [1, 2, 4],        # Minimum samples at a leaf node
    'rf__bootstrap': [True, False]            # Use bootstrap sampling
}


class GridSearchFinalModel:

    def __init__(self, name: str, estimator, hyper_parameters: Dict, cv: KFold) -> Self:
        """Grid Search Model Hyper-parameters and Train Final Model

        Parameters
        ----------
        name : str
            Model Name
        estimator : _type_
            Sklearn Model Instance
        hyper_parameters : Dict
            Hyper-parameters to tune.
        cv : KFold
            SKlean Kfold instance for grid search cv.

        Returns
        -------
        Self
        """
        self.name= name
        self.estimator= estimator
        self.hyper_parameters= hyper_parameters
        self.cv= cv
        self.pipeline = Pipeline([(self.name, self.estimator)])
        self.grid_search = GridSearchCV(self.pipeline, self.hyper_parameters, scoring="neg_mean_squared_error", cv=self.cv)
        self.final_model= None 

    def get_best_parameters(self, X: array, y: array) -> Dict:
        """Find Best Parameters

        Parameters
        ----------
        X : array
            Sample Features Space.
        y : array
            Response.

        Returns
        -------
        Dict
            Final Best Parameters.
        """
        self.grid_search.fit(X, y)
        self.grid_search.best_params_= { k.split("__")[1]: v for k, v in self.grid_search.best_params_.items() } # unpack parameters 
        return self.grid_search.best_params_
    

    def get_search_runs(self) -> DataFrame:
        return DataFrame.from_dict(self.grid_search.cv_results_).sort_values(by="rank_test_score", ascending=True)

    def get_best_features(self, X: array, y: array, features_names: List) -> Series:
        if self.grid_search.best_params_:

            model= RandomForestRegressor(**self.grid_search.best_params_)
        else:
            model= RandomForestRegressor()

        model.fit(X, y)
        features_importance= model.feature_importances_
        return Series(features_importance, index=features_names)

    def fit_final_model_with_best_parameters_and_features(self, df: DataFrame, features_to_use: List, model_version: int) -> None: # fit and serialize final model to disk
        self.final_model= RandomForestRegressor(**self.grid_search.best_params_)
        X= df[features_to_use].values
        y= df["total_fuel"].values
        self.final_model.fit(X, y)
        self.final_model.save_model(f"{PACKAGE_ROOT}/data/test/{self.name}_{str(model_version)}.json")
