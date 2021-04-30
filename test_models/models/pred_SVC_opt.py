
import pandas as pd
import numpy as np
import scipy.stats as stats

from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import RandomizedSearchCV

def pred(file_name, pred, gamePk):    
    pred_this_over = "shots_this_game_O" + str(pred)
    pred_this_under = "shots_this_game_U" + str(pred)
    res = {}
    for i in range(2):
        if(i == 1):
            pred_this = pred_this_over
            pos_label = 1
        else:
            pred_this = pred_this_under
            pos_label = 0

        data = pd.read_csv(file_name)
        data = data.replace(np.nan, 0)

        drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5", "shots_this_game_O4.5", "shots_this_game_U4.5","date"]
        drop_this = [x for x in drop_this if x != pred_this]
        data.drop(drop_this,1, inplace=True)

        pred_this_game = data.loc[data["gamePk"] == gamePk]
        game_index = data.loc[data["gamePk"] == gamePk].index[0]
        data = data.iloc[:game_index]


        X_all = data.drop([pred_this],1)
        Y_all = data[pred_this]

        scaler = MinMaxScaler()
        X_all[X_all.columns] = scaler.fit_transform(X_all[X_all.columns])    

        X_train, X_test, y_train, y_test = train_test_split(X_all, Y_all, test_size=0.33, random_state=42)  

        print()
        print(pred_this)     
        model = SVC(random_state=912)
        rand_list = {"C": stats.uniform(0.1, 1000), 
                    "kernel": ["rbf", "poly"],
                    "gamma": stats.uniform(0.01, 100)}
        rand_search = RandomizedSearchCV(model, param_distributions=rand_list, n_iter=20, n_jobs=5, cv=5, scoring="accuracy", refit=True)
        rand_search.fit(X_train, y_train)
        print("Best score: {}".format(rand_search.best_score_))
        # print("Best parameters: {}".format(rand_search.best_params_))


        clf_SVC = SVC(random_state=912, kernel='rbf', C=242.14129069781376, gamma=8.51187842927671, probability=True)   
        clf_SVC.fit(X_train, y_train)
        pred = clf_SVC.predict(X_test)
        matrix = confusion_matrix(pred, y_test)
        # print(matrix)
        # print(matrix.diagonal()/matrix.sum(axis=1))
        # print()
        




