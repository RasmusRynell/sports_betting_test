import Settings
import implementations.data_handlers.csv_handler as csv_handler
import implementations.data_handlers.prediction_handler as prediction_handler
from tqdm import tqdm


def analyzePredictionsFromDates(startDate_date=None, endDate_date=None):
    players_analyze_for = getPlayersFromDates(startDate_date, endDate_date)

    predictions = ["SVC_V1.0", "LDA_SVC_V1.0", "DEC_TREE_V1.0"]#, "XGBOOST_V1.0"]
    return prediction_handler.analyze(predictions, players_analyze_for)


def generatePredictionsFromDates(startDate_date=None, endDate_date=None):
    players_to_generate_for = getPlayersFromDates(startDate_date, endDate_date)

    predictions = ["SVC_V1.0", "LDA_SVC_V1.0", "DEC_TREE_V1.0"]#, "XGBOOST_V1.0"]
    tot = 0
    for playerId, playerValues in tqdm(players_to_generate_for.items(), desc="player"):
        for gamePk in tqdm(playerValues["games"], desc="games"):
            for pred in predictions:
                if "predictions" not in Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]:
                    Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["predictions"] = {}
                if pred not in Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["predictions"] or\
                        Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["predictions"][pred] == {}:
                    Settings.db.old_bets[str(playerId)]["games"][str(gamePk)]["predictions"][pred] = prediction_handler.predict(pred, str(playerId), gamePk)
                #else:
                    #print("No need to do this one, its already been calculated")
                tot += 1
    return tot



def generateTrainingDataFromDates(startDate_date=None, endDate_date=None):
    tot = 0
    players_to_generate_for = getPlayersFromDates(startDate_date, endDate_date)

    for playerId, playerValues in tqdm(players_to_generate_for.items()):
        Settings.db.old_bets[str(playerId)]["file_path"] = csv_handler.create_csv({"player_id": playerId,
                                                                                   "player_name": playerValues["player_name"]}, "", "./data/td/pp_all.csv")
        tot += 1

    return tot



def getPlayersFromDates(startDate_date, endDate_date):
    result = {}
    for playerId, playerInfo in Settings.db.old_bets.items():
        for gamePk, gameInfo in playerInfo["games"].items():
            add = False
            if startDate_date == None and endDate_date == None:
                add = True
            else:
                currDate_date = Settings.string_to_standard_datetime(
                    gameInfo["date"] + "T00:00:00Z")
                if endDate_date == None:
                    if currDate_date == startDate_date:
                        add = True
                else:
                    if startDate_date <= currDate_date and currDate_date <= endDate_date:
                        add = True

            if add:
                if str(playerId) not in result:
                    result[str(playerId)] = {
                        "player_name": playerInfo["player_name"], "games": []}
                result[str(playerId)]["games"].append(gamePk)
    return result
