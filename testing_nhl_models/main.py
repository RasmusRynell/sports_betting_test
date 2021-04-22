import json

import models.pred_LDA_SVC as pred_LDA_SVC
import models.pred_SVC as pred_SVC
import models.pred_decision_tree as decision_tree
import eval.calc_ROI as calc_ROI
import matplotlib.pyplot as plt

import eval.pred_eval as pred_eval


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
            calc_ROI.calc_bets_correct(data, model, i, 0, 0)

def simulate_bets(file):
    with open(file, "r") as f:
        data = f.read()
    data = json.loads(data)
    thresholds = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    procent_pots = [1]
    #calc_ROI.calc_bets_correct(data, "LDA_SVC_V1.0", 0.6, 1000, 1)
    plot_this_all = []
    for threshold in thresholds:
        for procent_pot in procent_pots:
            print("LDA SVC using threshold {} and procent pot {}:".format(threshold, procent_pot))
            plot_this_all.append(calc_ROI.calc_bets_correct(data, "LDA_SVC_V1.0", threshold, 1000, procent_pot))
            print()
    """
    count = 0   
    for i in thresholds:
        for j in procent_pots:
            x = range(0, len(plot_this_all[count]))
            y = []
            for k in plot_this_all[count]:
                y.append(k/1000)
            plt.plot(x, y, label="{}-{}".format(i,j))
            count += 1

    plt.ylabel("Money in account")
    plt.xlabel("Day")
    plt.legend()
    plt.show()
    """

def get_bets(file, date):
    with open(file, "r") as f:
        data = f.read()
    data = json.loads(data)
    bets = calc_ROI.get_bets(data, "LDA_SVC_V1.0", 0.6)
    for bet in bets:
        if bet["date"] == date:
            calc_ROI.calc_Kelly_Critera(bet)
            print(bet)    
    
def bet_site_acc(file):
    with open(file, "r") as f:
        data = f.read()
    data = json.loads(data)

    calc_ROI.bet_site_acc(data)


def test(file):   
    with open(file, "r") as f:
        data = f.read()
    data = json.loads(data)
    for t in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
        bets = pred_eval.find_bets(data, "LDA_SVC_V1.0", threshold=t)
        verified_bets = pred_eval.verify_bets(bets)
        pred_eval.simulate_betting(verified_bets, 1000)


test("./data/pred_2021-04-17.txt")
#get_bets("./data/pred_2021-04-17.txt", "2021-04-17")
