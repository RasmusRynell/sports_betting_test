

def check_odds(odds_over, odds_under, bets, threshold):
    best_bets = {}
    for bet_site in bets:
        if(float(bets[bet_site]["over"].replace(",", ".")) > odds_over + threshold): 
            if bets[bet_site]["over_under"] in bets:
                if(float(bets[bet_site]["over"].replace(",", ".")) > best_bets[bets[bet_site]["over_under"]]):
                    pass
            # bet = "over" 
            # if(float(bets[bet_site]["over"].replace(",", ".")) > best_odds):
            #     best_odds = float(bets[bet_site]["over"].replace(",", "."))
        if(float(bets[bet_site]["under"].replace(",", ".")) > odds_under + threshold): 
            pass
            # bet = "under" 
            # if(float(bets[bet_site]["under"].replace(",", ".")) > best_odds):
            #     best_odds = float(bets[bet_site]["under"].replace(",", "."))
    return bets

def calc_bets_correct(data, model_name, threshold):
    bets = {}
    count = 0
    for player_id, value in data.items():
        for game in value["games"]:
            pred = value["games"][game]["predictions"][model_name]
            odds_under = round(1/float(pred["pred_under"]["prediction"]), 3)
            odds_over = round(1/float(pred["pred_over"]["prediction"]), 3)
            bet, best_odds = check_odds(odds_over, odds_under, value["games"][game]["bets"], threshold)

            if bet != None:
                bets[game] = {"bet" : bet, "odds": best_odds}
            count += 1

    print(count)
    print(len(bets))

