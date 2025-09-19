#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Name: visualize_models.py

Description: Create Visualization Plots to Verify Linear Assumption and Models Fit. 


Author: Abdella Mohamed
"""
from typing import Dict, List
from typing_extensions import Self
from pandas import DataFrame
from numpy import array, hstack
from matplotlib import pyplot as plt
from sklearn.metrics import PredictionErrorDisplay
import seaborn as sns 
import scipy as sp
import statsmodels.api as sm



class VisualizeModels:

    def __init__(self, actual: array, predictions: Dict) -> Self:
        """Visualize Multiple Models Fit and Assumption.

        Parameters
        ----------
        actual : array
            Response variable
        predictions : Dict
            Predicted values for each estimator used.

        Returns
        -------
        Self
            Class instance for plotting.
        """
        self.actual= actual  
        self.predictions= predictions
        
    def plot_prediction_vs_actual_and_residual(self) -> None:
        
        for estimator_name in self.predictions.keys():
            
            fig, axs = plt.subplots(ncols=2, figsize=(8, 4))
            PredictionErrorDisplay.from_predictions(
                y_true=self.actual,
                y_pred=self.predictions[estimator_name],
                kind="actual_vs_predicted",
                subsample=100,
                ax=axs[0],
                random_state=0,
            )
            axs[0].set_title("Actual vs. Predicted values")
            
            PredictionErrorDisplay.from_predictions(
                y_true= self.actual,
                y_pred=self.predictions[estimator_name],
                kind="residual_vs_predicted",
                subsample=100,
                ax=axs[1],
                random_state=0,
            )
            
            axs[1].set_title("Residuals vs. Predicted Values")
            fig.suptitle(f"{estimator_name} cross-validated predictions")
            plt.tight_layout()
            plt.show()

    def plot_residuals_normality(self) -> None:
        residuals= self._get_residuals()
        
        for estimator_name in residuals.keys():
        
            fig, ax= plt.subplots(ncols=2, figsize=(10, 5))
            
            sp.stats.probplot(residuals[estimator_name], plot=ax[0], fit=True)
            sns.kdeplot(residuals[estimator_name], ax=ax[1])
            fig.suptitle(f"{estimator_name} Residuals Normality")
            plt.tight_layout()
            plt.show()

    def plot_autocorrelation(self) -> None:
        residuals= self._get_residuals()
        
        for estimator_name in residuals.keys():

            plt.plot(residuals[estimator_name])
            plt.title(f"{estimator_name} Residuals")
            plt.show()

            sm.graphics.tsa.plot_acf(residuals[estimator_name], lags=40)
            plt.show()
            
            sm.graphics.tsa.plot_pacf(residuals[estimator_name], lags=40)
            plt.show()

    def plot_multicollinearity(self, X: array, y: array, target_name: str, feat_names: List) -> None:
        cols= feat_names.append(target_name)
        df = DataFrame(hstack((X, y.reshape(-1, 1))), columns=cols)
        plt.figure(figsize=(10,10))  
        p=sns.heatmap(df.corr(), annot=True,cmap='RdYlGn',square=True)  # seaborn has very simple solution for heatmap
        p

    def plot_models_score(self, scores: DataFrame) -> None:
        
        for avg, st in zip(*[iter(scores.columns)]*2):
            
            plt.figure(figsize=(20, 6))
            plt.bar(scores.index, scores.sort_values(by= avg, ascending=False, inplace=False)[avg], yerr=scores[st], capsize=5, color='skyblue')
            plt.xlabel('Estimator')
            plt.ylabel(avg)
            plt.title('5 Fold CV Performance with Standard Error')
            plt.show()
    
    def _get_residuals(self) -> Dict:
        residuals= dict()
        
        for estimator_name in self.predictions.keys():
            residuals[estimator_name]= self.actual - self.predictions[estimator_name]
        
        return residuals