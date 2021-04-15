import json

import models.pred_LDA_SVC as pred_LDA_SVC
import models.pred_SVC as pred_SVC
import models.pred_decision_tree as decision_tree
import eval.calc_ROI as calc_ROI



def calculate_bet(name, gamePk, pred, best_odds_U, best_odds_O, file):
    print("Pred using LDA SVC:")
    print(pred_LDA_SVC.pred(file, pred, gamePk))

def eval_bets(file):
    with open(file, "r") as f:
        data = f.read()
    data = json.loads(data)
    models = ["LDA_SVC_V1.0", "SVC_V1.0", "DEC_TREE_V1.0"]
    for model in models:
        print("\n")
        print("Verifying bets for model: {}".format(model))
        for i in [float(j) / 10 for j in range(0, 10, 1)]:    
            print("With threshold {}:".format(i))
            calc_ROI.calc_bets_correct(data, model, i)

def bet_site_acc(file):
    with open(file, "r") as f:
        data = f.read()
    data = json.loads(data)

    calc_ROI.bet_site_acc(data)



#eval_bets("./data/to_alumnroot.txt")
#eval_bets("./data/pred_bets.txt")
#bet_site_acc("./data/pred_bets.txt")
