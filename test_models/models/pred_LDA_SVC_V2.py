
import pandas as pd
import numpy as np

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

        X_all = data.drop([pred_this],1)
        Y_all = data[pred_this]

        scaler = MinMaxScaler()
        X_all[X_all.columns] = scaler.fit_transform(X_all[X_all.columns]) 

        num_games_for_test = 50
        X_train = X_all[:-num_games_for_test]
        X_test = X_all[-num_games_for_test:]
        Y_train = Y_all[:-num_games_for_test]
        Y_test = Y_all[-num_games_for_test:]

        lda = LinearDiscriminantAnalysis(n_components=1)

        lda = lda.fit(X_train, Y_train)

        X_lda = lda.transform(X_all)

        X_lda_train = X_lda[:-num_games_for_test]
        X_lda_test = X_lda[-num_games_for_test:]

        clf_SVC = SVC(random_state=912, kernel='rbf', probability=True)
        clf_SVC.fit(X_lda_train, Y_train)
        pred_train = lda.predict(X_train)
        pred_test = clf_SVC.predict(X_lda_test)

        # clf_SVC.fit(X_train, Y_train)
        # pred = clf_SVC.predict(X_test)

        print("Training data")
        conf_matrix = confusion_matrix(Y_train, pred_train)
        tn, fp, fn, tp = confusion_matrix(Y_train, pred_train).ravel()
        print(tn, fp, fn, tp)
        print("Acc: {}".format(round((tn+tp)/(tn+fp+fn+tp), 3)))
        print(pred_this)
        print(conf_matrix)
        print()


        print("Test data")
        conf_matrix = confusion_matrix(Y_test, pred_test)
        tn, fp, fn, tp = confusion_matrix(Y_test, pred_test).ravel()
        print(tn, fp, fn, tp)
        print("Acc: {}".format(round((tn+tp)/(tn+fp+fn+tp), 3)))
        print(pred_this)
        print(conf_matrix)
        print()

