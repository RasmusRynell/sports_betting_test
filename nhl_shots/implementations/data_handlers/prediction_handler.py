import Settings




def predict(model, player, gamePk):
    if model == "SVC_V1.0":
        return {'pred_under': {
                        'F1_acc': 0.433,
                        'F1_std': 0.119,
                        'acc': 0.584,
                        'std': 0.038,
                        'prediction': '0.152'},
                'pred_over': {
                        'F1_acc': 0.649,
                        'F1_std': 0.082,
                        'acc': 0.584,
                        'std': 0.038,
                        'prediction': '0.829'}
                        }
    elif model == "LDA_SVC_V1.0":
        return {"model": model,
                "gamePk": gamePk,
                "player": player}
    if model == "DEC_TREE_V1.0":
        return {"model": model,
                "gamePk": gamePk,
                "player": player}
    elif model == "XGBOOST_V1.0":
        return {"model": model,
                "gamePk": gamePk,
                "player": player}


def analyze(models, games)
    for model in models:

        wins = 0
        loses = 0

        for playerId, playerValues in tqdm(games.items()):
            for gamePk in playerValues["games"]:
                if model in Settings.db.old_bets[playerId]["games"][gamePk]["predictions"]:
                    odds = get_best_odds_from_game(Settings.db.old_bets[playerId]["games"][gamePk]["bets"])
                    for over_under, values in odds.items():
                        bet_over, bet_under = bet_on_odds(values, Settings.db.old_bets[playerId]["games"][gamePk]["predictions"][model])
                        if bet_over:
                            if is_win(player_id, gamePk, True, over_under):
                                wins += 1
                                back += int(odds["over"]["odds"])
                            else:
                                loses += 1
                        if bet_under:
                            if is_win(player_id, gamePk, False, over_under):
                                wins += 1
                                back += int(odds["under"]["odds"])
                            else:
                                loses += 1
                
                else:
                    print("Something is wrong ://")


def is_win(player_id, gamePk, over, goals):
    if over:
        return Settings.db.games["games_information"][str(gamePk)]["data"]["players"][str(player_id)]["shots"] > goals
    return Settings.db.games["games_information"][str(gamePk)]["data"]["players"][str(player_id)]["shots"] < goals


def get_best_odds_from_game(bets):
    res = {}
    for site, siteValues in bets.items():
        if str(siteValues["over_under"]) not in res:
            res[siteValues["over_under"]] = {"over": {"odds": 0, "site": None},
           "under": {"odds": 0, "site": None}}
        if res[siteValues["over_under"]]["over"]["odds"] < siteValues["over"]:
            res[siteValues["over_under"]]["over"]["odds"] = siteValues["over"]
            res[siteValues["over_under"]]["over"]["site"] = site
        if res[siteValues["over_under"]]["under"]["odds"] < siteValues["under"]:
            res[siteValues["over_under"]]["under"]["odds"] = siteValues["under"]
            res[siteValues["over_under"]]["under"]["site"] = site
    return res


def bet_on_odds(betting_odds, model_odds):
    over = False
    under = False
    if int(betting_odds["over"]) + limit < model_odds["over"]["odds"]:
        over = True
    if int(betting_odds["under"]) + limit < model_odds["under"]["odds"]:
        under = True
    return (over, under)
