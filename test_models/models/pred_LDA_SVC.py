
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

        columns = list(data.columns.values)

        drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5","date"]
        keep_this_player = ["gamePk", "player-stat-current_age-games-back-1","player-stat-rosterStatus-games-back-1","player-stat-primaryPositioncode-games-back-1","player-stat-code-games-back-1","player-stat-timeOnIce-games-back-1","player-stat-assists-games-back-1","player-stat-goals-games-back-1","player-stat-shots-games-back-1","player-stat-hits-games-back-1","player-stat-powerPlayGoals-games-back-1","player-stat-powerPlayAssists-games-back-1","player-stat-penaltyMinutes-games-back-1","player-stat-faceOffWins-games-back-1","player-stat-faceoffTaken-games-back-1","player-stat-takeaways-games-back-1","player-stat-giveaways-games-back-1","player-stat-shortHandedGoals-games-back-1","player-stat-shortHandedAssists-games-back-1","player-stat-blocked-games-back-1","player-stat-plusMinus-games-back-1","player-stat-evenTimeOnIce-games-back-1","player-stat-powerPlayTimeOnIce-games-back-1","player-stat-shortHandedTimeOnIce-games-back-1","player-stat-isHome-games-back-1","player-stat-gameType-games-back-1","player-stat-current_age-games-back-2","player-stat-rosterStatus-games-back-2","player-stat-primaryPositioncode-games-back-2","player-stat-code-games-back-2","player-stat-timeOnIce-games-back-2","player-stat-assists-games-back-2","player-stat-goals-games-back-2","player-stat-shots-games-back-2","player-stat-hits-games-back-2","player-stat-powerPlayGoals-games-back-2","player-stat-powerPlayAssists-games-back-2","player-stat-penaltyMinutes-games-back-2","player-stat-faceOffWins-games-back-2","player-stat-faceoffTaken-games-back-2","player-stat-takeaways-games-back-2","player-stat-giveaways-games-back-2","player-stat-shortHandedGoals-games-back-2","player-stat-shortHandedAssists-games-back-2","player-stat-blocked-games-back-2","player-stat-plusMinus-games-back-2","player-stat-evenTimeOnIce-games-back-2","player-stat-powerPlayTimeOnIce-games-back-2","player-stat-shortHandedTimeOnIce-games-back-2","player-stat-isHome-games-back-2","player-stat-gameType-games-back-2","player-stat-current_age-games-back-3","player-stat-rosterStatus-games-back-3","player-stat-primaryPositioncode-games-back-3","player-stat-code-games-back-3","player-stat-timeOnIce-games-back-3","player-stat-assists-games-back-3","player-stat-goals-games-back-3","player-stat-shots-games-back-3","player-stat-hits-games-back-3","player-stat-powerPlayGoals-games-back-3","player-stat-powerPlayAssists-games-back-3","player-stat-penaltyMinutes-games-back-3","player-stat-faceOffWins-games-back-3","player-stat-faceoffTaken-games-back-3","player-stat-takeaways-games-back-3","player-stat-giveaways-games-back-3","player-stat-shortHandedGoals-games-back-3","player-stat-shortHandedAssists-games-back-3","player-stat-blocked-games-back-3","player-stat-plusMinus-games-back-3","player-stat-evenTimeOnIce-games-back-3","player-stat-powerPlayTimeOnIce-games-back-3","player-stat-shortHandedTimeOnIce-games-back-3","player-stat-isHome-games-back-3","player-stat-gameType-games-back-3","player-stat-current_age-games-back-4","player-stat-rosterStatus-games-back-4","player-stat-primaryPositioncode-games-back-4","player-stat-code-games-back-4","player-stat-timeOnIce-games-back-4","player-stat-assists-games-back-4","player-stat-goals-games-back-4","player-stat-shots-games-back-4","player-stat-hits-games-back-4","player-stat-powerPlayGoals-games-back-4","player-stat-powerPlayAssists-games-back-4","player-stat-penaltyMinutes-games-back-4","player-stat-faceOffWins-games-back-4","player-stat-faceoffTaken-games-back-4","player-stat-takeaways-games-back-4","player-stat-giveaways-games-back-4","player-stat-shortHandedGoals-games-back-4","player-stat-shortHandedAssists-games-back-4","player-stat-blocked-games-back-4","player-stat-plusMinus-games-back-4","player-stat-evenTimeOnIce-games-back-4","player-stat-powerPlayTimeOnIce-games-back-4","player-stat-shortHandedTimeOnIce-games-back-4","player-stat-isHome-games-back-4","player-stat-gameType-games-back-4","player-stat-current_age-games-back-5","player-stat-rosterStatus-games-back-5","player-stat-primaryPositioncode-games-back-5","player-stat-code-games-back-5","player-stat-timeOnIce-games-back-5","player-stat-assists-games-back-5","player-stat-goals-games-back-5","player-stat-shots-games-back-5","player-stat-hits-games-back-5","player-stat-powerPlayGoals-games-back-5","player-stat-powerPlayAssists-games-back-5","player-stat-penaltyMinutes-games-back-5","player-stat-faceOffWins-games-back-5","player-stat-faceoffTaken-games-back-5","player-stat-takeaways-games-back-5","player-stat-giveaways-games-back-5","player-stat-shortHandedGoals-games-back-5","player-stat-shortHandedAssists-games-back-5","player-stat-blocked-games-back-5","player-stat-plusMinus-games-back-5","player-stat-evenTimeOnIce-games-back-5","player-stat-powerPlayTimeOnIce-games-back-5","player-stat-shortHandedTimeOnIce-games-back-5","player-stat-isHome-games-back-5","player-stat-gameType-games-back-5"]
        keep_this_team = ["gamePk", "player_team-stat-playerPlayed-games-back-1","player_team-stat-wins-games-back-1","player_team-stat-losses-games-back-1","player_team-stat-ot-games-back-1","player_team-stat-score-games-back-1","player_team-stat-goals-games-back-1","player_team-stat-pim-games-back-1","player_team-stat-shots-games-back-1","player_team-stat-powerPlayPercentage-games-back-1","player_team-stat-powerPlayGoals-games-back-1","player_team-stat-powerPlayOpportunities-games-back-1","player_team-stat-faceOffWinPercentage-games-back-1","player_team-stat-blocked-games-back-1","player_team-stat-takeaways-games-back-1","player_team-stat-giveaways-games-back-1","player_team-stat-hits-games-back-1","player_team-stat-isHome-games-back-1","player_team-stat-gameType-games-back-1","player_team-stat-GoalsPerGame-games-back-1","player_team-stat-goalsAgainstPerGame-games-back-1","player_team-stat-shotsPerGame-games-back-1","player_team-stat-shotsAgainstPerGame-games-back-1","player_team-stat-playerPlayed-games-back-2","player_team-stat-wins-games-back-2","player_team-stat-losses-games-back-2","player_team-stat-ot-games-back-2","player_team-stat-score-games-back-2","player_team-stat-goals-games-back-2","player_team-stat-pim-games-back-2","player_team-stat-shots-games-back-2","player_team-stat-powerPlayPercentage-games-back-2","player_team-stat-powerPlayGoals-games-back-2","player_team-stat-powerPlayOpportunities-games-back-2","player_team-stat-faceOffWinPercentage-games-back-2","player_team-stat-blocked-games-back-2","player_team-stat-takeaways-games-back-2","player_team-stat-giveaways-games-back-2","player_team-stat-hits-games-back-2","player_team-stat-isHome-games-back-2","player_team-stat-gameType-games-back-2","player_team-stat-GoalsPerGame-games-back-2","player_team-stat-goalsAgainstPerGame-games-back-2","player_team-stat-shotsPerGame-games-back-2","player_team-stat-shotsAgainstPerGame-games-back-2","player_team-stat-playerPlayed-games-back-3","player_team-stat-wins-games-back-3","player_team-stat-losses-games-back-3","player_team-stat-ot-games-back-3","player_team-stat-score-games-back-3","player_team-stat-goals-games-back-3","player_team-stat-pim-games-back-3","player_team-stat-shots-games-back-3","player_team-stat-powerPlayPercentage-games-back-3","player_team-stat-powerPlayGoals-games-back-3","player_team-stat-powerPlayOpportunities-games-back-3","player_team-stat-faceOffWinPercentage-games-back-3","player_team-stat-blocked-games-back-3","player_team-stat-takeaways-games-back-3","player_team-stat-giveaways-games-back-3","player_team-stat-hits-games-back-3","player_team-stat-isHome-games-back-3","player_team-stat-gameType-games-back-3","player_team-stat-GoalsPerGame-games-back-3","player_team-stat-goalsAgainstPerGame-games-back-3","player_team-stat-shotsPerGame-games-back-3","player_team-stat-shotsAgainstPerGame-games-back-3","player_team-stat-playerPlayed-games-back-4","player_team-stat-wins-games-back-4","player_team-stat-losses-games-back-4","player_team-stat-ot-games-back-4","player_team-stat-score-games-back-4","player_team-stat-goals-games-back-4","player_team-stat-pim-games-back-4","player_team-stat-shots-games-back-4","player_team-stat-powerPlayPercentage-games-back-4","player_team-stat-powerPlayGoals-games-back-4","player_team-stat-powerPlayOpportunities-games-back-4","player_team-stat-faceOffWinPercentage-games-back-4","player_team-stat-blocked-games-back-4","player_team-stat-takeaways-games-back-4","player_team-stat-giveaways-games-back-4","player_team-stat-hits-games-back-4","player_team-stat-isHome-games-back-4","player_team-stat-gameType-games-back-4","player_team-stat-GoalsPerGame-games-back-4","player_team-stat-goalsAgainstPerGame-games-back-4","player_team-stat-shotsPerGame-games-back-4","player_team-stat-shotsAgainstPerGame-games-back-4","player_team-stat-playerPlayed-games-back-5","player_team-stat-wins-games-back-5","player_team-stat-losses-games-back-5","player_team-stat-ot-games-back-5","player_team-stat-score-games-back-5","player_team-stat-goals-games-back-5","player_team-stat-pim-games-back-5","player_team-stat-shots-games-back-5","player_team-stat-powerPlayPercentage-games-back-5","player_team-stat-powerPlayGoals-games-back-5","player_team-stat-powerPlayOpportunities-games-back-5","player_team-stat-faceOffWinPercentage-games-back-5","player_team-stat-blocked-games-back-5","player_team-stat-takeaways-games-back-5","player_team-stat-giveaways-games-back-5","player_team-stat-hits-games-back-5","player_team-stat-isHome-games-back-5","player_team-stat-gameType-games-back-5","player_team-stat-GoalsPerGame-games-back-5","player_team-stat-goalsAgainstPerGame-games-back-5","player_team-stat-shotsPerGame-games-back-5","player_team-stat-shotsAgainstPerGame-games-back-5"]
        keep_this_opp = ["gamePk", "opp_team-stat-playerPlayed-games-back-1","opp_team-stat-wins-games-back-1","opp_team-stat-losses-games-back-1","opp_team-stat-ot-games-back-1","opp_team-stat-score-games-back-1","opp_team-stat-goals-games-back-1","opp_team-stat-pim-games-back-1","opp_team-stat-shots-games-back-1","opp_team-stat-powerPlayPercentage-games-back-1","opp_team-stat-powerPlayGoals-games-back-1","opp_team-stat-powerPlayOpportunities-games-back-1","opp_team-stat-faceOffWinPercentage-games-back-1","opp_team-stat-blocked-games-back-1","opp_team-stat-takeaways-games-back-1","opp_team-stat-giveaways-games-back-1","opp_team-stat-hits-games-back-1","opp_team-stat-isHome-games-back-1","opp_team-stat-gameType-games-back-1","opp_team-stat-GoalsPerGame-games-back-1","opp_team-stat-goalsAgainstPerGame-games-back-1","opp_team-stat-shotsPerGame-games-back-1","opp_team-stat-shotsAgainstPerGame-games-back-1","opp_team-stat-playerPlayed-games-back-2","opp_team-stat-wins-games-back-2","opp_team-stat-losses-games-back-2","opp_team-stat-ot-games-back-2","opp_team-stat-score-games-back-2","opp_team-stat-goals-games-back-2","opp_team-stat-pim-games-back-2","opp_team-stat-shots-games-back-2","opp_team-stat-powerPlayPercentage-games-back-2","opp_team-stat-powerPlayGoals-games-back-2","opp_team-stat-powerPlayOpportunities-games-back-2","opp_team-stat-faceOffWinPercentage-games-back-2","opp_team-stat-blocked-games-back-2","opp_team-stat-takeaways-games-back-2","opp_team-stat-giveaways-games-back-2","opp_team-stat-hits-games-back-2","opp_team-stat-isHome-games-back-2","opp_team-stat-gameType-games-back-2","opp_team-stat-GoalsPerGame-games-back-2","opp_team-stat-goalsAgainstPerGame-games-back-2","opp_team-stat-shotsPerGame-games-back-2","opp_team-stat-shotsAgainstPerGame-games-back-2","opp_team-stat-playerPlayed-games-back-3","opp_team-stat-wins-games-back-3","opp_team-stat-losses-games-back-3","opp_team-stat-ot-games-back-3","opp_team-stat-score-games-back-3","opp_team-stat-goals-games-back-3","opp_team-stat-pim-games-back-3","opp_team-stat-shots-games-back-3","opp_team-stat-powerPlayPercentage-games-back-3","opp_team-stat-powerPlayGoals-games-back-3","opp_team-stat-powerPlayOpportunities-games-back-3","opp_team-stat-faceOffWinPercentage-games-back-3","opp_team-stat-blocked-games-back-3","opp_team-stat-takeaways-games-back-3","opp_team-stat-giveaways-games-back-3","opp_team-stat-hits-games-back-3","opp_team-stat-isHome-games-back-3","opp_team-stat-gameType-games-back-3","opp_team-stat-GoalsPerGame-games-back-3","opp_team-stat-goalsAgainstPerGame-games-back-3","opp_team-stat-shotsPerGame-games-back-3","opp_team-stat-shotsAgainstPerGame-games-back-3","opp_team-stat-playerPlayed-games-back-4","opp_team-stat-wins-games-back-4","opp_team-stat-losses-games-back-4","opp_team-stat-ot-games-back-4","opp_team-stat-score-games-back-4","opp_team-stat-goals-games-back-4","opp_team-stat-pim-games-back-4","opp_team-stat-shots-games-back-4","opp_team-stat-powerPlayPercentage-games-back-4","opp_team-stat-powerPlayGoals-games-back-4","opp_team-stat-powerPlayOpportunities-games-back-4","opp_team-stat-faceOffWinPercentage-games-back-4","opp_team-stat-blocked-games-back-4","opp_team-stat-takeaways-games-back-4","opp_team-stat-giveaways-games-back-4","opp_team-stat-hits-games-back-4","opp_team-stat-isHome-games-back-4","opp_team-stat-gameType-games-back-4","opp_team-stat-GoalsPerGame-games-back-4","opp_team-stat-goalsAgainstPerGame-games-back-4","opp_team-stat-shotsPerGame-games-back-4","opp_team-stat-shotsAgainstPerGame-games-back-4","opp_team-stat-playerPlayed-games-back-5","opp_team-stat-wins-games-back-5","opp_team-stat-losses-games-back-5","opp_team-stat-ot-games-back-5","opp_team-stat-score-games-back-5","opp_team-stat-goals-games-back-5","opp_team-stat-pim-games-back-5","opp_team-stat-shots-games-back-5","opp_team-stat-powerPlayPercentage-games-back-5","opp_team-stat-powerPlayGoals-games-back-5","opp_team-stat-powerPlayOpportunities-games-back-5","opp_team-stat-faceOffWinPercentage-games-back-5","opp_team-stat-blocked-games-back-5","opp_team-stat-takeaways-games-back-5","opp_team-stat-giveaways-games-back-5","opp_team-stat-hits-games-back-5","opp_team-stat-isHome-games-back-5","opp_team-stat-gameType-games-back-5","opp_team-stat-GoalsPerGame-games-back-5","opp_team-stat-goalsAgainstPerGame-games-back-5","opp_team-stat-shotsPerGame-games-back-5","opp_team-stat-shotsAgainstPerGame-games-back-5"]
        keep_this = ["isHome"]
        
        for i in range(len(columns)):
            if columns[i] not in keep_this_player:
                drop_this.append(columns[i])

        print(len(drop_this))
        
        drop_this = [x for x in drop_this if x != pred_this]
        data.drop(drop_this,1, inplace=True)
        # pred_this_game = data.loc[data["gamePk"] == gamePk]
        # game_index = data.loc[data["gamePk"] == gamePk].index[0]
        # data = data.iloc[:game_index]

        X_all = data.drop([pred_this],1)
        Y_all = data[pred_this]

        scaler = MinMaxScaler()
        X_all[X_all.columns] = scaler.fit_transform(X_all[X_all.columns]) 

        lda = LinearDiscriminantAnalysis(n_components=1)
        lda = lda.fit(X_all, Y_all)
        X_lda = lda.transform(X_all)

        clf_SVC = SVC(random_state=912, kernel='rbf', probability=True)        
        # cross validation
        f_scores_test = cross_val_score(clf_SVC, X_lda, Y_all, scoring="f1", cv=5)
        f_test_error = round(f_scores_test.mean(),3)
        f_test_std = round(f_scores_test.std(), 3)

        #X_train, X_test, y_train, y_test = train_test_split(X_lda, Y_all, test_size=0.4, random_state=0)
        
        X_train = X_lda[:-50]
        y_train = Y_all[:-50]
        
        X_test = X_lda[-50:]
        y_test = Y_all[-50:]

        clf = SVC(kernel='rbf', C=1).fit(X_train, y_train)
        print("Train acc:")
        print(clf.score(X_train, y_train))
        print("Train data len: {}".format(len(X_train)))
        print("Test acc:")
        print(clf.score(X_test, y_test))
        print("Test data len: {}".format(len(X_test)))
        print()

        # scores_test = cross_val_score(clf_SVC, X_lda, Y_all, cv=5)
        # test_error = round(scores_test.mean(), 3)
        # test_std = round(scores_test.std(), 3)

        # clf_SVC.fit(X_lda, Y_all) 
        # pred_this_game = pred_this_game.drop([pred_this],1)
        # pred_this_game_LDA = lda.transform(pred_this_game)
        # Y_pred = clf_SVC.predict_proba(pred_this_game_LDA)        

        # if(pred_this == pred_this_over):
        #     res["pred_over"] = {"F1_acc":f_test_error, "F1_std":f_test_std, "acc":test_error, "std":test_std, "prediction":str(round(Y_pred[0][1], 3))}
        # else:
        #     res["pred_under"] = {"F1_acc":f_test_error, "F1_std":f_test_std, "acc":test_error, "std":test_std, "prediction":str(round(Y_pred[0][1], 3))}

    return res  
