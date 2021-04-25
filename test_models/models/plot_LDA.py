
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

def pred(file_name, pred):    
    pred_this = "shots_this_game_O" + str(pred)
    data = pd.read_csv(file_name)
    data = data.replace(np.nan, 0)

    drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5","date"]
    drop_this = [x for x in drop_this if x != pred_this]
    data.drop(drop_this,1, inplace=True)

    X_all = data.drop([pred_this],1)
    Y_all = data[pred_this]

    X_gamePk = X_all.gamePk

    scaler = MinMaxScaler()
    X_all[X_all.columns] = scaler.fit_transform(X_all[X_all.columns]) 

    lda = LinearDiscriminantAnalysis(n_components=1)
    lda = lda.fit(X_all, Y_all)
    X_lda = lda.transform(X_all)

    X_plot = []
    for i in X_lda:
        X_plot.append(i[0])




pred("./data/pp_alexander_ovechkin.csv", 3.5, )
