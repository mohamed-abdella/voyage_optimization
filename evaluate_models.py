from typing import Dict
from typing_extensions import Self
from pandas import DataFrame, Series
from numpy import array
from sklearn.model_selection import cross_val_score, cross_val_predict, KFold
from sklearn.metrics import make_scorer, root_mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR

# #################################################################################################################################################
# ############################################################### Setup ###########################################################################
SEED= 5

PIPELINES = {
    'ridge': Pipeline([
        ('estimator', Ridge())
    ]),
    'randomforest': Pipeline([
        ('estimator', RandomForestRegressor())
    ]),
    'svr': Pipeline([
    ('estimator', SVR(kernel="linear"))
    ]),
    'xgboost': Pipeline([
        ('estimator', XGBRegressor())
    ])
}
# #################################################################################################################################################
# ############################################################### End Setup #######################################################################


class EvaluateModels:

    def __init__(self, pipe_cfg: Dict, X: array, y: array, cv: KFold) -> Self:
        """Evaluate Multiple Models

        Parameters
        ----------
        pipe_cfg : dict
            sklearn pipelines with multiple estimators
        X : 2D Numpy Array 
            Full dataset without column names.
        y : 1D Numpy Array
            Response labels.
        cv : Sklearn Kfold instance
            Kfold split based on sklearn.model_selection._split.KFold
        """
        self.pipe_cfg= pipe_cfg
        self.X= X
        self.y= y
        self.cv= cv
        self.adj_r2_= list()
        self.scores_= dict()
        
    def get_scores(self) -> Dict:
        output= dict()
        
        for estimator_name, pipeline in self.pipe_cfg.items():
            self.scores_= dict()
            
            for metric_name, metric in self._get_metrics().items():
                
                self.scores_[metric_name]= self._get_score(estimator_name, metric)

                if metric_name in "r2":
                    for r2_score in self.scores_[metric_name]:
                        self.adj_r2_.append(self._get_adj_r2(r2_score))
                    self.scores_.update({"adj_r2": array(self.adj_r2_)})
                    # reset 
                    self.adj_r2_= list()
        
            # publish results 
            output[estimator_name]= self.scores_
                
        return output

    def get_predictions(self) -> Dict:
        output= dict()
        
        for estimator_name, pipeline in self.pipe_cfg.items():

            output[estimator_name]= self._get_prediction(estimator_name)

        return output

    def print_scores(self, scores: Dict) -> DataFrame:
        """Print scores

        Parameters
        ----------
        scores : Dict
            Dict of scores to visualize in a table as Dataframe

        Returns
        -------
        DataFrame
            Of models scores.
        """
        df= DataFrame.from_dict(scores).transpose()
        new_df= DataFrame(index=df.index.tolist())
        
        cols= df.columns.tolist()
        scores_mean= list()
        scores_std= list()
        
        for col in cols:
            for scores in df[col]:
                scores_mean.append(scores.mean())
                scores_std.append(scores.std())
        
        
            new_df[f"{col}_mean"]= Series(scores_mean, index= df.index)
            new_df[f"{col}_std"]= Series(scores_std, index= df.index)
            scores_mean= list()
            scores_std= list()
    
        return new_df.sort_values(by="adj_r2_mean", ascending=False)
    
    def _get_prediction(self, estimator: str):
        return cross_val_predict(self.pipe_cfg[estimator], self.X, self.y, cv=self.cv)


    def _get_score(self, estimator: str, metric: str):
        return cross_val_score(self.pipe_cfg[estimator], self.X, self.y, cv=self.cv, scoring=make_scorer(metric)) 

    def _get_adj_r2(self, r2: float) -> float:

        n= len(self.X) 
        p= self.X.shape[1]
        
        adj_r2= 1 - ((1 - r2) * (n - 1) / (n - p - 1))
        return adj_r2

    @staticmethod 
    def _get_metrics() -> Dict:
        return {"r2": r2_score, "rmse": root_mean_squared_error, "mae": mean_absolute_error}


