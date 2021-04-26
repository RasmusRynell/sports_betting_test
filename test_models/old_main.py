import json

import models.pred_LDA_SVC as pred_LDA_SVC
import models.pred_SVC as pred_SVC
import models.pred_decision_tree as decision_tree
from handler import api

from unidecode import unidecode
from tqdm import tqdm


api = api("https://statsapi.web.nhl.com/api/v1/", True, True)

def eval_models_acc():
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
                    bet_preds[game["bets"][bet_site]["over_under"]] = pred
            bet_preds["bets"] = game["bets"]
            player_pred[gamePk] = bet_preds
        player_bets[player_id] = player_pred

    print(player_bets)

def test(threshold_acc):
    f = open('preds.json',)
    all_preds = json.load(f)
    count = 0
    pred_result = {"1.5_wins" : 0, "1.5_loss" : 0, "2.5_wins" : 0, "2.5_loss" : 0, "3.5_wins" : 0, "3.5_loss" : 0}
    for player_id, games in all_preds.items():
        for gamePk, preds in games.items():
            response_json = api.send_request("game/"+str(gamePk)+"/boxscore")
            num_shots = None
            if "ID" + str(player_id) in response_json["teams"]["home"]["players"]:
                num_shots = response_json["teams"]["home"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]

            if "ID" + str(player_id) in response_json["teams"]["away"]["players"]:
                num_shots = response_json["teams"]["away"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]

            if num_shots != None:
                if "1.5" in preds:  
                    count += 1    
                    if float(preds["1.5"]["pred_under"]["prediction"]) > 0.5 + threshold_acc: 
                        if num_shots < 1.5:
                            pred_result["1.5_wins"] += 1
                        else:
                            pred_result["1.5_loss"] += 1
                    elif float(preds["1.5"]["pred_over"]["prediction"]) >= 0.5 + threshold_acc:
                        if num_shots > 1.5:
                            pred_result["1.5_wins"] += 1
                        else:
                            pred_result["1.5_loss"] += 1
                if "2.5" in preds:       
                    count += 1             
                    if float(preds["2.5"]["pred_under"]["prediction"]) >= 0.5 + threshold_acc:   
                        if num_shots < 2.5:
                            pred_result["2.5_wins"] += 1
                        else:
                            pred_result["2.5_loss"] += 1
                    elif float(preds["2.5"]["pred_over"]["prediction"]) >= 0.5 + threshold_acc:     
                        if num_shots > 2.5:
                            pred_result["2.5_wins"] += 1
                        else:
                            pred_result["2.5_loss"] += 1             
                if "3.5" in preds:   
                    count += 1 
                    if float(preds["3.5"]["pred_under"]["prediction"]) >= 0.5 + threshold_acc:     
                        if num_shots < 3.5:
                            pred_result["3.5_wins"] += 1
                        else:
                            pred_result["3.5_loss"] += 1
                    elif float(preds["3.5"]["pred_over"]["prediction"]) >= 0.5 + threshold_acc:                
                        if num_shots > 3.5:
                            pred_result["3.5_wins"] += 1
                        else:
                            pred_result["3.5_loss"] += 1 

    if pred_result["1.5_loss"] != 0:
        pred_result["1.5_acc"] = round(pred_result["1.5_wins"] / pred_result["1.5_loss"], 3)
    if pred_result["2.5_loss"] != 0:
        pred_result["2.5_acc"] = round(pred_result["2.5_wins"] / pred_result["2.5_loss"], 3)
    if pred_result["3.5_loss"] != 0:
        pred_result["3.5_acc"] = round(pred_result["3.5_wins"] / pred_result["3.5_loss"], 3)
    if (pred_result["1.5_loss"] + pred_result["2.5_loss"] + pred_result["3.5_loss"]) != 0:
        pred_result["tot_acc"] = round((pred_result["1.5_wins"] + pred_result["2.5_wins"] + pred_result["3.5_wins"]) \
            / (pred_result["1.5_loss"] + pred_result["2.5_loss"] + pred_result["3.5_loss"]), 3)
    pred_result["tot_bets"] = pred_result["1.5_wins"] + pred_result["2.5_wins"] + pred_result["3.5_wins"] + pred_result["1.5_loss"] + pred_result["2.5_loss"] + pred_result["3.5_loss"]
    if count != 0:
        pred_result["num_bet%"] = round(pred_result["tot_bets"] / count, 3)

    api.save()
    
    print(pred_result)

thresholds = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
for threshold in thresholds:
    print("Threshold: {}".format(threshold))
    test(threshold)
