import implementations.models.pred_decision_tree as DEC_TREE_V1
import implementations.models.pred_LDA_SVC as LDA_SVC_V1
import implementations.models.pred_SVC as SVC_V1
import implementations.models.pred_xgboost as XGBOOST_V1
import Settings
from tqdm import tqdm


def predict(model, playerId, gamePk):
    try:
        file = Settings.db.old_bets[str(playerId)]["file_path"]
    except:
        print("Error player does not have file_path saved")
        raise("Make a file for player")
    total = {}
    for over_under in get_different_over_under(Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]):
        if model == "SVC_V1.0":
           total[over_under] = SVC_V1.pred(file, str(over_under), int(gamePk))
        elif model == "LDA_SVC_V1.0":
           total[over_under] = LDA_SVC_V1.pred(file, str(over_under), int(gamePk))
        if model == "DEC_TREE_V1.0":
           total[over_under] = DEC_TREE_V1.pred(file, str(over_under), int(gamePk))
        elif model == "XGBOOST_V1.0":
            total[over_under] = XGBOOST_V1.pred(file, str(over_under), int(gamePk))
    return total


def analyze(models, games):
    for model in models:
        wins = 0
        loses = 0
        back = 0
        total_acc = 0

        for playerId, playerValues in tqdm(games.items()):
            for gamePk in playerValues["games"]:
                if Settings.db.games["games_information"][str(gamePk)]["status"] == "6" or Settings.db.games["games_information"][str(gamePk)]["status"] == "7":
                    if "predictions" in Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]:
                        if model in Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["predictions"]:
                            odds = get_best_odds_from_game(Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["bets"])
                            for over_under, values in odds.items():
                                bet_over, bet_under = bet_on_odds(values, Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["predictions"][str(model)][over_under])
                                if bet_over:
                                    total_acc += float(Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["predictions"][str(model)][over_under]["pred_over"]["acc"])
                                    if is_win(playerId, gamePk, True, over_under):
                                        wins += 1
                                        back += float(str(odds[over_under]["over"]["odds"]).replace(",", "."))
                                    else:
                                        loses += 1
                                if bet_under:
                                    total_acc += float(Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["predictions"][str(model)][over_under]["pred_under"]["acc"])
                                    if is_win(playerId, gamePk, False, over_under):
                                        wins += 1
                                        back += float(str(odds[over_under]["under"]["odds"]).replace(",", "."))
                                    else:
                                        loses += 1
        print("Model: ".format(model))
        print("Total: {}".format(wins+loses))
        print("Wins: {}".format(wins))
        print("Loses: {}".format(loses))
        print("ROI: {}".format(back/(wins+loses)))
        print("Winrate: {}".format(wins/(wins+loses)))
        print("Avr acc {}".format(total_acc/(wins+loses)))
    return wins+loses


def is_win(player_id, gamePk, over, goals):
    if over:
        return float(Settings.db.games["games_information"][str(gamePk)]["data"]["players"][str(player_id)]["shots"]) > float(goals)
    return float(Settings.db.games["games_information"][str(gamePk)]["data"]["players"][str(player_id)]["shots"]) < float(goals)


def get_best_odds_from_game(bets):
    res = {}
    for site, siteValues in bets.items():
        if str(siteValues["over_under"]) not in res:
            res[siteValues["over_under"]] = {"over": {"odds": 0, "site": None, "over_under": 0},
           "under": {"odds": 0, "site": None, "over_under": 0}}
        if float(str(res[siteValues["over_under"]]["over"]["odds"]).replace(",", ".")) < float(siteValues["over"].replace(",", ".")):
            res[siteValues["over_under"]]["over"]["odds"] = siteValues["over"]
            res[siteValues["over_under"]]["over"]["site"] = site
        if float(str(res[siteValues["over_under"]]["under"]["odds"]).replace(",", ".")) < float(siteValues["under"].replace(",", ".")):
            res[siteValues["over_under"]]["under"]["odds"] = siteValues["under"]
            res[siteValues["over_under"]]["under"]["over_under"] = site


    return res


def bet_on_odds(betting_odds, model_odds):
    how_sure = 0.5
    over = False
    under = False
    if float(model_odds["pred_over"]["prediction"]) > how_sure:
        over = True
    if float(model_odds["pred_under"]["prediction"]) > how_sure:
        under = True

    return (over, under)


def get_different_over_under(gameInfo):
    total = []
    for site, info in gameInfo["bets"].items():
        if info["over_under"] not in total:
            t = info["over_under"]
            if t[1:] == ".5":
                total.append(t)
            else:
                print("Did not work...")
                print(site)
                print(t)
                print(info)
    return total
