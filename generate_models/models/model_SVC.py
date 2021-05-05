
import pandas as pd
import numpy as np 
import scipy.stats as stats

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

from sklearn.svm import SVC


def generate_model(file_name, pred_this, earliest_gamePk_index):
    data = pd.read_csv(file_name)
    data = data.replace(np.nan, 0)
    drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5", "shots_this_game_O4.5", "shots_this_game_U4.5","date"]
    drop_this = [x for x in drop_this if x != pred_this]
    data.drop(drop_this,1, inplace=True)

    pred_data = data.iloc[earliest_gamePk_index:].drop([pred_this],1)
    data = data.iloc[:earliest_gamePk_index]

    
    X_all = data.drop([pred_this],1)
    Y_all = data[pred_this]
    num_training_samples = len(data)
    res = {}

    res["num_samples"] = num_training_samples
    
    pipeline = make_pipeline(StandardScaler(), SVC(class_weight="balanced"))
    score_acc = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring="accuracy").mean(), 3)
    score_f1 = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring="f1").mean(), 3)

    X_train, X_test, y_train, y_test = train_test_split(X_all, Y_all, test_size=0.33, random_state=42)
    svc_model = pipeline.fit(X_train, y_train)
    scaler = StandardScaler()
    X_all_scaled = scaler.fit_transform(X_all)

    pred = svc_model.predict(scaler.transform(X_test))
    matrix = confusion_matrix(y_test, pred)
    print(matrix)

    pred_data_scaled = scaler.transform(pred_data)
    pred_games = svc_model.predict(pred_data_scaled)
    res["SVC"] = {}
    res["SVC"]["acc"] = score_acc
    res["SVC"]["f1"] = score_f1
    res["SVC"]["predictions"] = str(pred_games)
    
    """
    model = SVC()
    param_grid = [
        {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
        {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
    ]
    rand_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=-1, scoring="accuracy")
    pipeline = make_pipeline(StandardScaler(), rand_search)
    score_acc_gridseach_opt_acc = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring="accuracy").mean(), 3)
    score_f1_gridseach_opt_acc = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring="f1").mean(), 3)
    
    svc_opt_acc_model = pipeline.fit(X_train, y_train)
    scaler = StandardScaler()
    X_all_scaled = scaler.fit_transform(X_all)

    pred = svc_model.predict(scaler.transform(X_test))
    matrix = confusion_matrix(y_test, pred)
    print(matrix)

    pred_data_scaled = scaler.transform(pred_data)
    pred_games = svc_model.predict(pred_data_scaled)
    res["SVC-opt-acc"] = {}
    res["SVC-opt-acc"]["acc"] = score_acc_gridseach_opt_acc
    res["SVC-opt-acc"]["f1"] = score_f1_gridseach_opt_acc
    res["SVC-opt-acc"]["predictions"] = str(pred_games)

    model = SVC(class_weight="balanced")
    param_grid = [
        {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
        {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
    ]
    rand_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=5, n_jobs=-1, scoring="roc_auc")
    pipeline = make_pipeline(StandardScaler(), rand_search)
    score_acc_gridseach_opt_f1 = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring="accuracy").mean(), 3)
    score_f1_gridseach_opt_f1 = round(cross_val_score(pipeline, X_all, Y_all, cv=5, n_jobs=-1, scoring="roc_auc").mean(), 3)
    
    svc_opt_f1_model = pipeline.fit(X_train, y_train)
    scaler = StandardScaler()
    X_all_scaled = scaler.fit_transform(X_all)

    pred = svc_model.predict(scaler.transform(X_test))
    matrix = confusion_matrix(y_test, pred)
    print(matrix)

    pred_data_scaled = scaler.transform(pred_data)
    pred_games = svc_model.predict(pred_data_scaled)
    res["SVC-opt-f1"] = {}
    res["SVC-opt-f1"]["acc"] = score_acc_gridseach_opt_f1
    res["SVC-opt-f1"]["f1"] = score_f1_gridseach_opt_f1
    res["SVC-opt-f1"]["predictions"] = str(pred_games)
    """
    return res