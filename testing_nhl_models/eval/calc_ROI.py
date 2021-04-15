import requests
from tqdm import tqdm

def check_odds(bets, pred, threshold):
    best_odds = 0
    bet = None
    best_site = None
    for bet_site in bets:
        if (float(bets[bet_site]["over"].replace(",",".")) > 1/float(pred["pred_over"]["prediction"]) + threshold):
            #tmp = str(float(bets[bet_site]["over"].replace(",","."))) +  " > " + str(1/float(pred["pred_over"]["prediction"])) + " + " + str(threshold) + "(" + str(1/float(pred["pred_over"]["prediction"]) + threshold) + ")"
            #print(tmp)
            if (float(bets[bet_site]["over"].replace(",",".")) > best_odds):
                best_odds = float(bets[bet_site]["over"].replace(",","."))
                bet = "over"
                best_site = bet_site
        if (float(bets[bet_site]["under"].replace(",",".")) > 1/float(pred["pred_under"]["prediction"]) + threshold):
            if (float(bets[bet_site]["under"].replace(",",".")) > best_odds):
                best_odds = float(bets[bet_site]["under"].replace(",","."))
                bet = "under"
                best_site = bet_site
    return (bet, best_odds, best_site)

def verify_bets(bets):
    bet_result = []
    for gamePk, game_bets in tqdm(bets.items()):
        response_json = requests.get("https://statsapi.web.nhl.com/api/v1/game/"+str(gamePk)+"/boxscore").json()
        for player_bet in game_bets:
            if "ID"+player_bet["playerID"] in response_json["teams"]["home"]["players"]:
                num_shots = response_json["teams"]["home"]["players"]["ID"+player_bet["playerID"]]["stats"]["skaterStats"]["shots"]
            if "ID"+player_bet["playerID"] in response_json["teams"]["away"]["players"]:
                num_shots = response_json["teams"]["away"]["players"]["ID"+player_bet["playerID"]]["stats"]["skaterStats"]["shots"]
            
            if player_bet["bet"] == "over":
                player_bet["bet_win"] = (float(player_bet["over_under"]) < num_shots)
            else:                
                player_bet["bet_win"] = (float(player_bet["over_under"]) > num_shots)
            bet_result.append(player_bet)
    return bet_result

def calc_unit_bet_ROI(bet_result, unit_bet):
    money_betted = 0
    money_gained = 0
    for bet in bet_result:
        money_betted += unit_bet
        if(bet["bet_win"]):
            money_gained += bet["best_odds"]*unit_bet
    return (money_gained/money_betted)


def bet_site_acc(data):
    bets = {}
    for player_id, value in data.items():
        for game in value["games"]:
            if("bet365" in value["games"][game]["bets"]):
                if (float(value["games"][game]["bets"]["bet365"]["over"]) > float(value["games"][game]["bets"]["bet365"]["under"])):
                    bet = "under"
                else:
                    bet = "over"

                if value["games"][game]["gamePk"] not in bets:
                    bets[value["games"][game]["gamePk"]] = []
                bets[value["games"][game]["gamePk"]].append({"bet": bet, "over_under": value["games"][game]["bets"]["bet365"]["over_under"], "gamePk": value["games"][game]["gamePk"], \
                        "date": value["games"][game]["date"], "playerID": player_id})

    bet_result = verify_bets(bets)
    count = 0
    count_correct = 0
    for bet in bet_result:
        count += 1
        if(bet["bet_win"] == True):
            count_correct += 1
    print(count_correct/count)

def calc_bets_correct(data, model_name, threshold):
    bets = {}
    count = 0
    count_bets = 0
    for player_id, value in data.items():
        for game in value["games"]:
            #Check if we have a prediciton for that game
            if "predictions" in value["games"][game] and len(value["games"][game]["predictions"]) > 0:
                bet_sites = value["games"][game]["bets"]
                for over_under, prediciton in value["games"][game]["predictions"][model_name].items():
                    bet, best_odds, best_site = check_odds(bet_sites, prediciton, threshold)
                    if bet != None:
                        if value["games"][game]["gamePk"] not in bets:
                            bets[value["games"][game]["gamePk"]] = []
                        bets[value["games"][game]["gamePk"]].append({"bet": bet, "best_site": best_site, "best_odds": best_odds, "over_under": over_under, "gamePk": value["games"][game]["gamePk"], \
                        "date": value["games"][game]["date"], "playerID": player_id})
                        count_bets += 1

                    count += 1

    bet_result = verify_bets(bets)
    
    print(calc_unit_bet_ROI(bet_result, 2))
    print("Betted on {} players out of {} total player bets".format(count_bets, count))

