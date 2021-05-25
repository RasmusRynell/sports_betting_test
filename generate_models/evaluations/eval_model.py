import pandas as pd
import numpy as np 
import json
import os
from tqdm import tqdm

from joblib import dump, load

from handler import api

api = api("https://statsapi.web.nhl.com/api/v1/", True, True)

def get_num_shots(gamePk, player_id):
    response_json = api.send_request("game/"+str(gamePk)+"/boxscore")
    num_shots = None
    if "ID" + str(player_id) in response_json["teams"]["home"]["players"]:
        num_shots = response_json["teams"]["home"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]

    if "ID" + str(player_id) in response_json["teams"]["away"]["players"]:
        num_shots = response_json["teams"]["away"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]
    return num_shots

def find_best_odds(bet_sites):
    res = {}
    for name, bet_site in bet_sites.items():
        if not (str(bet_site["over_under"]) + "_over") in res:
            res[str(bet_site["over_under"]) + "_over"] = float(bet_site["over"].replace(",", "."))
            res[str(bet_site["over_under"]) + "_under"] = float(bet_site["under"].replace(",", "."))
        else:
            if res[str(bet_site["over_under"]) + "_over"]< float(bet_site["over"].replace(",", ".")):
                res[str(bet_site["over_under"]) + "_over"] = float(bet_site["over"].replace(",", "."))
            if res[str(bet_site["over_under"]) + "_under"]< float(bet_site["under"].replace(",", ".")):
                res[str(bet_site["over_under"]) + "_under"] = float(bet_site["under"].replace(",", "."))
    return res

def eval_player_model(player_csv, bets, model, target, player_average_odds, model_edge, decision_boundary_edge):
    try:
        clf_model = load(model)
        tmp = target.split("_")[-1][1:]
        if target.split("_")[-1][0] == "U":
            tmp += "_under"
        else:
            tmp += "_over"
        model_odds = round(1/float(clf_model["precision"]), 3)

        # variabales for tracking unit betting of the model
        money_betted = 0
        money_won = 0
        unit_size = 2

        if float(player_average_odds[tmp]) > model_odds + model_edge:
            data = pd.read_csv(player_csv)
            data = data.replace(np.nan, 0)
            drop_this = ["shots_this_game_total", "shots_this_game_O1.5", "shots_this_game_U1.5", "shots_this_game_O2.5", "shots_this_game_U2.5", "shots_this_game_O3.5", "shots_this_game_U3.5", "shots_this_game_O4.5", "shots_this_game_U4.5","date"]
            drop_this = [x for x in drop_this if x != target]
            data.drop(drop_this,1, inplace=True)

            for game in bets["games"]:
                best_odds = find_best_odds(bets["games"][game]["bets"])
                if tmp in best_odds:
                    pred_data = data.loc[data['gamePk'] == int(game)].drop([target],1)
                    y_pred = clf_model["model"].predict(pred_data)            
                    y_pred_decision_function = clf_model["model"].decision_function(pred_data)
                    if y_pred[0] == 1 and round(abs(y_pred_decision_function[0]), 3) > decision_boundary_edge:
                        money_betted += unit_size
                        num_shots = get_num_shots(game, bets["player_id"])
                        if target.split("_")[-1][0] == "U" and num_shots < float(target.split("_")[-1][1:]):
                            money_won += best_odds[tmp] * unit_size
                        if target.split("_")[-1][0] == "O" and num_shots > float(target.split("_")[-1][1:]):
                            money_won += best_odds[tmp] * unit_size

                        if bets["games"][game]["date"] == "2021-05-24":
                            print(model)
                            print(y_pred)

        if(money_betted == 0):
            res = "Player model: {}\nPrecision of model: {} with a edge of {}\nWith no games betted.\n".format(model, clf_model["precision"], \
                round(float(player_average_odds[tmp]) - model_odds, 3))
        else:
            res = "Player model: {}\nPrecision of model: {} with a edge of {}\nBetted: {} and won {} which is a ROI of {}".format(model, clf_model["precision"], \
                round(float(player_average_odds[tmp]) - model_odds, 3), money_betted, money_won, round(money_won/money_betted, 3))

        return {"msg":res, "betted":money_betted, "won":money_won}
    except:
        return {"msg":"No model for that bet", "betted":0, "won":0}

def eval_model(all_bets, all_models, model_type, model_edge=0.0, decision_boundary_edge=0.0):
    f = open('./data/player_ids.json',)
    player_ids = json.load(f)
    f.close()

    tot_money_betted = 0
    tot_money_won = 0

    for player_csv in (all_models):
        player_average_odds = all_models[player_csv]["average_odds"]
        player_path = "./generated_models/" + player_ids[all_models[player_csv]["player_id"]].replace(" ", "_") + "/" 
        if os.path.exists(player_path):
            player_path += str(model_type) + ".eval"
            with open(player_path, "w") as outfile:
                for target, model in all_models[player_csv][model_type].items():
                    res = eval_player_model(player_csv, all_bets[all_models[player_csv]["player_id"]], model, target, player_average_odds, model_edge, decision_boundary_edge)
                    tot_money_betted += res["betted"]
                    tot_money_won += res["won"]
                    outfile.write(str(res["msg"]) + "\n")


        #break
    if round(tot_money_won/tot_money_betted, 3) > 1.0:
        print("Used edge: {} and decision boundary: {}".format(model_edge, decision_boundary_edge))
        print("Bets placed = {}".format(tot_money_betted/2))
        print("Betted = {}\nWon = {}\nROI = {}\n".format(tot_money_betted, tot_money_won, round(tot_money_won/tot_money_betted, 3)))

