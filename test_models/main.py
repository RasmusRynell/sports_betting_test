import json

import models.pred_LDA_SVC as pred_LDA_SVC
import models.pred_SVC as pred_SVC
import models.pred_decision_tree as decision_tree
from handler import api
from tqdm import tqdm
from unidecode import unidecode
import time

api = api("https://statsapi.web.nhl.com/api/v1/", True, True)

"""
TODO:
    - Show acc for each player
    - Show acc for each over/under (1.5, 2.5, 3.5)
    - Show average acc
    - Show average odds
    - Show account balance after simulation
    - Show acc on "over" and "under"

Orimliga svar:

CLAYTON KELLER
"8479343": {
    "avr_acc": 1.0,
    "loss": 14,
    "won": 5
}

Artemi Panarin
"8478550": {
    "avr_acc": 0.997,
    "loss": 7,
    "won": 7
}
"""


def generate_predictions():
    f = open('./data/player_ids.json',)
    player_ids = json.load(f)
    f = open('./data/all_bets.json',)
    all_bets = json.load(f)
    player_bets = {}
    for player_id in tqdm(all_bets):
        player_name = player_ids[player_id]
        player_pred = {}
        for gamePk in all_bets[player_id]["games"]:
            game = all_bets[player_id]["games"][gamePk]
            training_file = "pp_" + unidecode(player_name.replace(" ", "_")) + ".csv"
            bet_preds = {}
            for bet_site in game["bets"]:
                if game["bets"][bet_site]["over_under"] not in bet_preds:
                    pred = pred_LDA_SVC.pred("./data/td/"+training_file, game["bets"][bet_site]["over_under"], int(gamePk))
                    if "best_odds_under" not in pred["pred_under"]:
                        pred["pred_under"]["best_odds_under"] = game["bets"][bet_site]["under"].replace(",", ".")
                    if "best_odds_over" not in pred["pred_over"]:
                        pred["pred_over"]["best_odds_over"] = game["bets"][bet_site]["over"].replace(",", ".")
                    
                    pred["date"] = game["date"]
                    bet_preds[game["bets"][bet_site]["over_under"]] = pred

                if float(bet_preds[game["bets"][bet_site]["over_under"]]["pred_under"]["best_odds_under"]) < float(game["bets"][bet_site]["under"].replace(",", ".")):
                    bet_preds[game["bets"][bet_site]["over_under"]]["pred_under"]["best_odds_under"] = game["bets"][bet_site]["under"].replace(",", ".")
                if float(bet_preds[game["bets"][bet_site]["over_under"]]["pred_over"]["best_odds_over"]) < float(game["bets"][bet_site]["over"].replace(",", ".")):
                    bet_preds[game["bets"][bet_site]["over_under"]]["pred_over"]["best_odds_over"] = game["bets"][bet_site]["over"].replace(",", ".")

            player_pred[gamePk] = bet_preds
        player_bets[player_id] = player_pred
        
    print(str(player_bets).replace("'", '"'))  
    #print(json.dumps(player_bets, indent=4, sort_keys=True))


def get_num_shots(gamePk, player_id):
    response_json = api.send_request("game/"+str(gamePk)+"/boxscore")
    num_shots = None
    if "ID" + str(player_id) in response_json["teams"]["home"]["players"]:
        num_shots = response_json["teams"]["home"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]

    if "ID" + str(player_id) in response_json["teams"]["away"]["players"]:
        num_shots = response_json["teams"]["away"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]
    return num_shots


def find_bets(all_preds, confidence_threshold, accuracy_threshold, f1_threshold, acc_std_threshold, f1_std_threshold, edge_threshold):
    bets_per_player = {}
    bets_per_date = {}
    tot_bets = []
    for player_id, data in all_preds.items():
        for gamePk, preds in data.items():
            for over_under, pred in preds.items():
                if(float(pred["pred_under"]["F1_acc"]) >= f1_threshold and float(pred["pred_under"]["F1_std"]) <= f1_std_threshold and \
                    float(pred["pred_under"]["prediction"]) >= confidence_threshold and float(pred["pred_under"]["acc"]) >= accuracy_threshold \
                        and float(pred["pred_under"]["std"]) <= acc_std_threshold \
                        and float(pred["pred_under"]["best_odds_under"])>= (1/float(pred["pred_under"]["prediction"])+edge_threshold)):
                    pred["pred_under"]["gamePk"] = gamePk
                    pred["pred_under"]["player_id"] = player_id
                    pred["pred_under"]["over/under"] = over_under
                    pred["pred_under"]["bet"] = "under"
                    if player_id not in bets_per_player:
                        bets_per_player[player_id] = []
                    bets_per_player[player_id].append(pred["pred_under"])
                    if pred["date"] not in bets_per_date:
                        bets_per_date[pred["date"]] = []
                    bets_per_date[pred["date"]].append(pred["pred_under"])
                    tot_bets.append(pred["pred_under"])

                elif(float(pred["pred_over"]["F1_acc"]) >= f1_threshold and float(pred["pred_over"]["F1_std"]) <= f1_std_threshold and \
                    float(pred["pred_over"]["prediction"]) >= confidence_threshold and float(pred["pred_over"]["acc"]) >= accuracy_threshold \
                        and float(pred["pred_over"]["std"]) <= acc_std_threshold \
                        and float(pred["pred_over"]["best_odds_over"])>= (1/float(pred["pred_over"]["prediction"])+edge_threshold)): 
                    pred["pred_over"]["gamePk"] = gamePk
                    pred["pred_over"]["player_id"] = player_id
                    pred["pred_over"]["over/under"] = over_under
                    pred["pred_over"]["bet"] = "over"
                    if player_id not in bets_per_player:
                        bets_per_player[player_id] = []
                    bets_per_player[player_id].append(pred["pred_over"])
                    if pred["date"] not in bets_per_date:
                        bets_per_date[pred["date"]] = []
                    bets_per_date[pred["date"]].append(pred["pred_over"])
                    tot_bets.append(pred["pred_over"])

    return (bets_per_player, bets_per_date, tot_bets)


def verify_thresholds(bets, print_header):
    num_bets = 0
    tot_acc = 0
    tot_f1_acc = 0
    tot_odds = 0
    unit = 2
    unit_bet_won = 0
    unit_bet_spent = 0
    result_bets = {"over_win" : 0, "over_loss" : 0, "under_win" : 0, "under_loss" : 0}

    for bet in bets:
        num_bets += 1
        tot_acc += float(bet["acc"])
        tot_f1_acc += float(bet["F1_acc"])
        num_shots = get_num_shots(bet["gamePk"], bet["player_id"])
        if bet["bet"] == "over":
            tot_odds += float(bet["best_odds_over"])
            unit_bet_spent += unit
            if num_shots > float(bet["over/under"]):
                unit_bet_won += float(bet["best_odds_over"]) * unit
                if bet["over/under"] + "_won" not in result_bets:
                    result_bets[bet["over/under"] + "_won"] = 0
                result_bets[bet["over/under"] + "_won"] += 1
                result_bets["over_win"] += 1
            else:
                if bet["over/under"] + "_loss" not in result_bets:
                    result_bets[bet["over/under"] + "_loss"] = 0
                result_bets[bet["over/under"] + "_loss"] += 1
                result_bets["over_loss"] += 1

        elif bet["bet"] == "under":
            tot_odds += float(bet["best_odds_under"])
            unit_bet_spent += unit
            if num_shots < float(bet["over/under"]):
                unit_bet_won += float(bet["best_odds_under"]) * unit
                if bet["over/under"] + "_won" not in result_bets:
                    result_bets[bet["over/under"] + "_won"] = 0
                result_bets[bet["over/under"] + "_won"] += 1
                result_bets["under_win"] += 1
            else:
                if bet["over/under"] + "_loss" not in result_bets:
                    result_bets[bet["over/under"] + "_loss"] = 0
                result_bets[bet["over/under"] + "_loss"] += 1
                result_bets["under_loss"] += 1

    if num_bets != 0:
        print("------------------------------------------------------------------------")
        print(print_header)
        print("Number of bets placed: {}".format(num_bets))
        if num_bets != 0:
            print("Average model accuracy: {}".format(round(tot_acc/num_bets, 3)))
            print("Average model F1 accuracy: {}".format(round(tot_f1_acc/num_bets, 3)))
            print("Average odds: {}".format(round(tot_odds/num_bets, 3)))

        if (result_bets["over_loss"] + result_bets["under_loss"]) != 0:
            print("Total bet accuracy: {}".format(round((result_bets["over_win"] + result_bets["under_win"]) / (result_bets["over_loss"] + result_bets["under_loss"]), 3)))

        if "1.5_loss" in result_bets and "1.5_win" in result_bets and result_bets["1.5_loss"] != 0:
            print("Accuracy for 1.5 bets: {}".format(round(result_bets["1.5_won"]/result_bets["1.5_loss"], 3)))
        if "2.5_loss" in result_bets and "2.5_win" in result_bets and result_bets["2.5_loss"] != 0:
            print("Accuracy for 2.5 bets: {}".format(round(result_bets["2.5_won"]/result_bets["2.5_loss"], 3)))    
        if "3.5_loss" in result_bets and "3.5_win" in result_bets and result_bets["3.5_loss"] != 0:
            print("Accuracy for 3.5 bets: {}".format(round(result_bets["3.5_won"]/result_bets["3.5_loss"], 3)))

        print("Money with unit bet of {}: {}".format(unit, round(unit_bet_won-unit_bet_spent, 3)))
        print(result_bets)
        print("------------------------------------------------------------------------")
        print()

def verify_acc_per_player(bets):
    result_bets = {}

    for player_id, games in bets.items():
        if player_id not in result_bets:
            result_bets[player_id] = {}
            result_bets[player_id]["won"] = 0
            result_bets[player_id]["loss"] = 0
        tot_acc = 0
        for game in games:
            tot_acc += float(game["acc"])
            if (game["bet"] == "over" and float(game["over/under"]) < get_num_shots(game["gamePk"], player_id)) \
                or (game["bet"] == "under" and float(game["over/under"]) > get_num_shots(game["gamePk"], player_id)):
                result_bets[player_id]["won"] += 1
            else:
                if player_id == "8479343":
                    print(game)
                    print(get_num_shots(game["gamePk"], player_id))
                result_bets[player_id]["loss"] += 1
        result_bets[player_id]["avr_acc"] = round(tot_acc/len(games), 3)  
 
    #print(json.dumps(result_bets, indent=4, sort_keys=True))

def optimize_predictions(confidence_threshold, accuracy_threshold, f1_threshold, acc_std_threshold, f1_std_threshold, edge_threshold):
    f = open('preds2.json',)
    all_preds = json.load(f)
    bets_per_player, bets_per_date, tot_bets = find_bets(all_preds, confidence_threshold, accuracy_threshold, f1_threshold, acc_std_threshold, f1_std_threshold, edge_threshold)
    print_header = ("Confidence: {} | Accuracy: {} | F1 Accuracy: {} | Accuracy STD: {} | F1 STD: {} | Edge: {}".format(confidence_threshold, accuracy_threshold, f1_threshold, acc_std_threshold, f1_std_threshold, edge_threshold))
    #verify_thresholds(tot_bets, print_header)
    verify_acc_per_player(bets_per_player)


optimize_predictions(0.6,0,0,1,1,0)

pred = pred_LDA_SVC.pred("./data/td/pp_clayton_keller.csv", 1.5, 2020020461)
print(pred)

