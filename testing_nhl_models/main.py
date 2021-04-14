import json

import models.pred_LDA_SVC as pred_LDA_SVC
import models.pred_SVC as pred_SVC
import models.pred_decision_tree as decision_tree
import models.pred_xgboost as pred_xgboost
import eval.calc_ROI as calc_ROI



def calculate_bet(name, gamePk, pred, best_odds_U, best_odds_O, file):
    print("Pred using LDA SVC:")
    print(pred_LDA_SVC.pred(file, pred, gamePk))
    #print("Pred using SVC:")
    #print(pred_SVC.pred(file, pred, gamePk))
    #print("Pred using decision_tree:")
    #print(decision_tree.pred(file, pred, gamePk))
    #print("Pred using xgboost:")
    #print(pred_xgboost.pred(file, pred, gamePk))

#calculate_bet("david perron", 2020020525, "2.5", 1, 1, "./data/td/pp_2020020122_david_perron.csv")

def eval_bets(file):
    with open(file, "r") as f:
        data = f.read()
    data = json.loads(data)
    calc_ROI.calc_bets_correct(data, "LDA_SVC_V1.0", 0)
    calc_ROI.calc_bets_correct(data, "SVC_V1.0", 0)
    calc_ROI.calc_bets_correct(data, "DEC_TREE_V1.0", 0)


eval_bets("./data/test.txt")