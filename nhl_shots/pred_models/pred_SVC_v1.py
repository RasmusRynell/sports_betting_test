import sys
import pandas as pd
import numpy as np

from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict

###############################################
def pred_SVC(file_name, pred):
    pred_this_over = "shots_this_game_O" + str(pred)
    pred_this_under = "shots_this_game_U" + str(pred)
    #res = {"file": file_name}
    res = {}
    for i in range(2):
        if(i == 1):
            pred_this = pred_this_over
            pos_label = 1
        else:
            pred_this = pred_this_under
            pos_label = 0

        data = pd.read_csv(file_name)

        drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5",]
        drop_this = [x for x in drop_this if x != pred_this]
        data.drop(drop_this,1, inplace=True)

        X_all = data.drop([pred_this],1)
        Y_all = data[pred_this]

        scaler = MinMaxScaler()
        X_all[X_all.columns] = scaler.fit_transform(X_all[X_all.columns])
        #This is the information about the game we want to predict.
        X_pred_info = X_all.head(1)
        Y_pred_info = Y_all.head(1)
        X_all = X_all.iloc[1:]
        Y_all = Y_all.iloc[1:]

        X_train, X_test, Y_train, Y_test = train_test_split(X_all, Y_all, test_size=50, random_state=2, stratify=Y_all)


        clf_SVC = SVC(random_state=912, kernel='rbf', probability=True)
        clf_SVC.fit(X_train, Y_train)

        # cross validation
        f_scores_test = cross_val_score(clf_SVC, X_test, Y_test, scoring="f1", cv=5)
        f_test_error = round(f_scores_test.mean(),3)
        f_test_std = round(f_scores_test.std(), 3)
        
        scores_test = cross_val_score(clf_SVC, X_test, Y_test, cv=5)
        test_error = round(scores_test.mean(), 3)
        test_std = round(scores_test.std(), 3)

        # Predict for our game
        Y_pred = clf_SVC.predict_proba(X_pred_info)
        Y_pred_odds = round(1/Y_pred[0][1], 2)
        #Fit using CV
        #fit = cross_val_predict(clf_SVC, X_train, Y_train, cv=5)
        

        if(pred_this == pred_this_over):
            res["pred_over"] = {"F1_acc":f_test_error, "F1_std":f_test_std, "acc":test_error, "std":test_std, "prediction":str(Y_pred), "prediction_odds":str(Y_pred_odds)}
        else:
            res["pred_under"] = {"F1_acc":f_test_error, "F1_std":f_test_std, "acc":test_error, "std":test_std, "prediction":str(Y_pred), "prediction_odds":str(Y_pred_odds)}
    return res
###############################################
"""
file_name = sys.argv[1]
pred = sys.argv[2]

res = pred_SVC(file_name, pred)
print(res)
"""