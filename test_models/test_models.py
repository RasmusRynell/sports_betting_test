
import argh
import json
from tqdm import tqdm
from unidecode import unidecode

from handler import api

#Import all models
import models.models.pred_SVC as pred_SVC
import models.models.pred_SVC_opt as pred_SVC_opt
import models.models.pred_logistic_regression as pred_logistic_regression
import models.models.pred_KNN as pred_KNN


api = api("https://statsapi.web.nhl.com/api/v1/", True, True)

def get_num_shots(gamePk, player_id):
    response_json = api.send_request("game/"+str(gamePk)+"/boxscore")
    num_shots = None
    if "ID" + str(player_id) in response_json["teams"]["home"]["players"]:
        num_shots = response_json["teams"]["home"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]

    if "ID" + str(player_id) in response_json["teams"]["away"]["players"]:
        num_shots = response_json["teams"]["away"]["players"]["ID" + str(player_id)]["stats"]["skaterStats"]["shots"]
    return num_shots

def pred_for_date(all_bets, model, date, model_name):
    """
    For a given date using the given model predict all games that day and
    add the prediction to the json object containing all information for the bets and games.

    It returns a json containing all bets and games with predictions for games for the given date.
    """
    f = open('./data/player_ids.json',)
    player_ids = json.load(f)

    for player_id, games in tqdm(all_bets.items()):
        player_name = player_ids[player_id]
        for gamePk, game in games["games"].items():
            if game["date"] == str(date) or date == None:
                predictions = {}
                for bet_site in game["bets"]:
                    if game["bets"][bet_site]["over_under"] not in predictions:
                        training_file = "pp_" + unidecode(player_name.replace(" ", "_")) + ".csv"
                        pred = model.pred("./data/td/"+training_file, game["bets"][bet_site]["over_under"], int(gamePk))
                        predictions[game["bets"][bet_site]["over_under"]] = pred
                if "predictions" not in all_bets[player_id]["games"][gamePk]:
                    all_bets[player_id]["games"][gamePk]["predictions"] = {}
                all_bets[player_id]["games"][gamePk]["predictions"][model_name] = predictions
    return all_bets

def verify_bets(all_bets, conf_threshold, acc_threshold, bet_edge):
    f = open('./data/player_ids.json',)
    player_ids = json.load(f)

    bets_won = 0
    bets_lost = 0

    for player_id, games in (all_bets.items()):
        player_name = player_ids[player_id]
        for gamePk, game in games["games"].items():
            if "predictions" in game:
                for over_under, pred in game["predictions"].items():
                    shots_this_game = get_num_shots(gamePk, player_id)
                    if float(pred["pred_under"]["acc"]) >= acc_threshold:
                        if float(pred["pred_under"]["prediction"]) >= conf_threshold:
                            if float(over_under) < shots_this_game:
                                bets_won += 1
                            else:
                                bets_lost += 1
                        
                        elif float(pred["pred_over"]["prediction"]) >= conf_threshold:
                            if float(over_under) > shots_this_game:
                                bets_won += 1
                            else:
                                bets_lost += 1

    print("Bet accuracy: {}".format(round(bets_won/(bets_won+bets_lost), 3)))

def eval_models(SVC_OPT=False, SVC=False, log_reg=False, KNN=False, date=None, allDates=False):
    f = open("./data/all_bets.json",)
    all_bets = json.load(f)

    if (SVC):
        if (date):
            all_bets = pred_for_date(all_bets, pred_SVC, date, "SVC")
        if (allDates):
            date = None
            all_bets = pred_for_date(all_bets, pred_SVC, date, "SVC")
        pass

    if (SVC_OPT):
        if (date):
            all_bets = pred_for_date(all_bets, pred_SVC_opt, date, "SVC-OPT")
        if (allDates):
            date = None
            all_bets = pred_for_date(all_bets, pred_SVC_opt, date, "SVC-OPT")
        pass
        
    if (log_reg):
        if (date):
            all_bets = pred_for_date(all_bets, pred_logistic_regression, date, "log-reg")
        if (allDates):
            date = None
            all_bets = pred_for_date(all_bets, pred_logistic_regression, date, "log-reg")
        pass

    if (KNN):
        if (date):
            all_bets = pred_for_date(all_bets, pred_KNN, date, "KNN")
        if (allDates):
            date = None
        all_bets = pred_for_date(all_bets, pred_KNN, date, "KNN")
        pass
    
    print(all_bets)
if __name__ == "__main__":
    parser=argh.ArghParser()
    parser.add_commands([eval_models])
    parser.dispatch()

