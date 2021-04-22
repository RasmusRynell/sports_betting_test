import requests
from tqdm import tqdm
from eval.handler import api

api = api("https://statsapi.web.nhl.com/api/v1/", True, True)


def check_odds(bets, pred, over_under, threshold, acc_threshold, min_confidence):
    best_odds = 0
    bet = None
    best_site = None
    pred_odds = 0

    for bet_site in bets:
        if str(bets[bet_site]["over_under"]) == str(over_under):
            if (float(bets[bet_site]["over"].replace(",",".")) > 1/float(pred["pred_over"]["prediction"]) + threshold and \
                float(pred["pred_over"]["acc"]) > acc_threshold and float(pred["pred_over"]["prediction"]) > min_confidence):
                if (float(bets[bet_site]["over"].replace(",",".")) > best_odds):
                    best_odds = float(bets[bet_site]["over"].replace(",","."))
                    bet = "over"
                    best_site = bet_site
                    pred_odds = round(1/float(pred["pred_over"]["prediction"]), 3)
            if (float(bets[bet_site]["under"].replace(",",".")) > 1/float(pred["pred_under"]["prediction"]) + threshold and \
                float(pred["pred_under"]["acc"]) > acc_threshold and float(pred["pred_under"]["prediction"]) > min_confidence):
                if (float(bets[bet_site]["under"].replace(",",".")) > best_odds):
                    best_odds = float(bets[bet_site]["under"].replace(",","."))
                    bet = "under"
                    best_site = bet_site
                    pred_odds = round(1/float(pred["pred_under"]["prediction"]), 3)

    return (bet, best_odds, best_site, pred_odds)

def find_bets(data, model_name, threshold=0.0, acc_threshold=0.0, min_confidence=0.0):
    bets = {}
    count = 0
    count_bets = 0

    for player_id, value in data.items():
        for game in value["games"]:
            # Check if we have a prediction for this game
            if "predictions" in value["games"][game] and len(value["games"][game]["predictions"]) > 0:
                bet_sites_odds = value["games"][game]["bets"]
                for over_under, prediction in value["games"][game]["predictions"][model_name].items():
                    bet, best_odds, best_site, pred_odds = check_odds(bet_sites_odds, prediction, over_under, threshold, acc_threshold, min_confidence)
                    if bet != None:
                        if value["games"][game]["date"] not in bets:
                            bets[value["games"][game]["date"]] = []
                        bets[value["games"][game]["date"]].append({"bet": bet, "best_site": best_site, "best_odds": best_odds, "over_under": over_under, "pred_odds": pred_odds, \
                            "gamePk": value["games"][game]["gamePk"], "date": value["games"][game]["date"], "playerID": player_id})
                        count_bets += 1

                    count += 1

    return bets
                    
def verify_bets(bets):
    bet_result = {}

    for date, game_bets in tqdm(bets.items()):
        bet_result[date] = []
        for player_bet in game_bets:
            response_json = api.send_request("game/"+str(player_bet["gamePk"])+"/boxscore")
            if "ID"+player_bet["playerID"] in response_json["teams"]["home"]["players"]:
                num_shots = response_json["teams"]["home"]["players"]["ID"+player_bet["playerID"]]["stats"]["skaterStats"]["shots"]
            if "ID"+player_bet["playerID"] in response_json["teams"]["away"]["players"]:
                num_shots = response_json["teams"]["away"]["players"]["ID"+player_bet["playerID"]]["stats"]["skaterStats"]["shots"]
          
            if player_bet["bet"] == "over":
                player_bet["bet_win"] = (float(player_bet["over_under"]) < num_shots)
            else:                
                player_bet["bet_win"] = (float(player_bet["over_under"]) > num_shots)
            bet_result[date].append(player_bet)
    api.save()
    return bet_result    

def calc_Kelly_Critera(bet):
    bet["Kelly Critera"] = round(((1/bet["pred_odds"])-(1-1/bet["pred_odds"])/(bet["best_odds"]-1))*0.25, 3)
    return bet

def simulate_betting(verified_bets, current_pot):
    pot_each_day = []
    win_each_day = []
    bets = 0
    bets_won = 0
    for date in verified_bets:
        #print("Current pot: {}".format(current_pot))
        won_this_day = 0
        for bet in verified_bets[date]:
            calc_Kelly_Critera(bet)
            bet_size = current_pot*bet["Kelly Critera"]
            current_pot -= bet_size
            bets += 1
            if bet["bet_win"] == True:
                won_this_day += bet_size * bet["best_odds"]
                bets_won += 1

        #print("Won this day: {}".format(won_this_day))
        current_pot += won_this_day
        pot_each_day.append(current_pot)
        win_each_day.append(won_this_day)
    print(current_pot)
    print("Won {} bets out of {}".format(bets_won, bets))