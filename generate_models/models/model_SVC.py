
import pandas as pd
import numpy as np 
import scipy.stats as stats
from tqdm import tqdm

from models.eval_model import eval_model
from models.eval_model import print_eval

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.decomposition import PCA
from sklearn.metrics import make_scorer, accuracy_score, precision_score


from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier


def generate_model(file_name, pred_this, earliest_gamePk_index, average_odds, model_edge):
    data = pd.read_csv(file_name)
    data = data.replace(np.nan, 0)
    
    drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5", "shots_this_game_O4.5", "shots_this_game_U4.5","date"]
    
    drop_this = [x for x in drop_this if x != pred_this]
    data.drop(drop_this,1, inplace=True)

    pred_data = data.iloc[earliest_gamePk_index:].drop([pred_this],1)
    y_pred_data = data.iloc[earliest_gamePk_index:][pred_this]
    data = data.iloc[:earliest_gamePk_index]

    X_all = data.drop([pred_this],1)
    Y_all = data[pred_this]

    opts = ["normal", "GridSearchCV"]#, "RandomizedSearchCV"]
    evals = ["accuracy", "precision"]#, "f1", "recall", "roc_auc"]

    best_res = None
    best_model = None
    best_precision = 0
    for opt in (opts):
        for eval in evals:
            if(opt == "normal"):
                pipeline = make_pipeline(StandardScaler(), SVC(class_weight="balanced", probability=True))
                res = eval_model(pipeline, X_all, Y_all)

                if(float(res["precision accuracy"]) > best_precision):
                    best_precision = float(res["precision accuracy"])
                    best_model = pipeline
                    best_res = res

            elif(opt == "GridSearchCV"):
                model = SVC(class_weight="balanced", probability=True)
                param_grid = [
                    {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
                    {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
                ]
                if(eval == "accuracy"):
                    scorer = make_scorer(accuracy_score)
                elif(eval == "precision"):
                    scorer = make_scorer(precision_score, zero_division=0.0)
                rand_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=None, scoring=scorer)
                pipeline = make_pipeline(StandardScaler(), rand_search)   
                res = eval_model(pipeline, X_all, Y_all)

                if(float(res["precision accuracy"]) > best_precision):
                    best_precision = float(res["precision accuracy"])
                    best_model = pipeline
                    best_res = res
   

            elif(opt == "RandomizedSearchCV"):
                model = SVC(class_weight="balanced", probability=True)
                rand_list = {"C": stats.uniform(0.1, 1000), 
                    "kernel": ["rbf", "poly"],
                    "gamma": stats.uniform(0.01, 100)}

                if(eval == "accuracy"):
                    scorer = make_scorer(accuracy_score)
                elif(eval == "precision"):
                    scorer = make_scorer(precision_score, zero_division=0.0)

                rand_search = RandomizedSearchCV(model, param_distributions=rand_list, n_iter=20, n_jobs=None, cv=5, scoring=eval, refit=True)
                pipeline = make_pipeline(StandardScaler(), rand_search)   
                res = eval_model(pipeline, X_all, Y_all)

                if(float(res["precision accuracy"]) > best_precision):
                    best_precision = float(res["precision accuracy"])
                    best_model = pipeline
                    best_res = res 
    
    return { "model" : best_model, "precision" : best_precision }

    """                
    if (average_odds - 1/best_precision) - model_edge:
        y_pred = best_model.predict(pred_data)
        #y_pred_decision_function = best_model.decision_function(pred_data)
        #y_pred_proba = best_model.predict_proba(pred_data)
        model_pred = {}
        gamePks = pred_data[["gamePk"]].values
        for i in range(len(gamePks)):
            model_pred[gamePks[i][0]] = {}
            model_pred[gamePks[i][0]]["prediction"] = y_pred[i]
            #model_pred[gamePks[i][0]]["decision_function"] = round(y_pred_decision_function[i], 3)
            #model_pred[gamePks[i][0]]["proba"] = round(y_pred_proba[i][1], 3)
    else:
        model_pred = {}

    return {"pipeline" : best_model, "precision accuracy" : best_precision, "model accuracy" : best_res, "model predictions" : model_pred}
    """

