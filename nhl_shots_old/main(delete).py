import data_processing.create_csv as csv
import old_bets.bet_io as bet_io
import Settings
import pred_models.pred_SVC_v1 as svc
import pred_models.pred_XGBoost_v1 as xgb
from tqdm import tqdm



# Get data from bet365
games = bet_io.get_from_file("2021-03-21")
print(len(games))
games.extend(bet_io.get_from_file("2021-03-20"))
print(len(games))
games.extend(bet_io.get_from_file("2021-03-19"))
print(len(games))
games.extend(bet_io.get_from_file("2021-03-18"))
print(len(games))
games.extend(bet_io.get_from_file("2021-03-17"))
print(len(games))
games.extend(bet_io.get_from_file("2021-03-16"))
print(len(games))

for game in games:
    Settings.bets_database.add_bet(game[0], game[1], game[2], game[3], game[4], game[5], game[6], game[7])

Settings.api.save_api_cache()
Settings.bets_database.save_to_json_file()

'''
all_games = Settings.bets_database.get_all_games()

for game in tqdm(all_games):
    for player in tqdm(game["players"]):
        player["file-path"] = csv.create_csv(game, "", "./temp2/pp_all.csv")

Settings.print_json(all_games)

Settings.api.save_api_cache()


total = []
# Call predictor to predict all csv files
for game in tqdm(all_games):
    for player in tqdm(game["players"]):
        file = player["file-path"]
        if file:
            full = {}
            over_under = player["known_over_under"]

            #Pred models
            pred_SVC = svc.pred_SVC(file, over_under)
            pred_xgb = xgb.pred_XGB(file, over_under)

            #Saving data

            #Player
            basic_data["player_name"] = player["name"]
            basic_data["over-under"] = over_under

            #Basic data
            basic_data = {}
            #Game
            basic_data["player_team"] = player["team_name"]
            basic_data["opp_team"] = game["home_team"] if player["team_name"] != game["home_team"] else game["away_team"]
            #basic_data["home_or_away"] = games[bet_game_id]["bet365-stat"][player_id]["ply_team_name"]
            basic_data["date"] = game["date"]
            full["basic_data"] = basic_data


            #Bets
            predictions = {}
            for k, v in player["bets"].items():
                pred = {}
                pred["odds_over"] = player["bets"][k]["over"]
                pred["odds_under"] = player["bets"][k]["under"]
                pred["over_under"] = player["bets"][k]["over_under"]
                predictions[str(k)] = pred
            full["predictions"] = predictions


            #SVC
            SVC = {}
            SVC["pred_over"] = pred_SVC["pred_over"]["prediction"]
            SVC["pred_under"] = pred_SVC["pred_under"]["prediction"]
            SVC["pred_over_acc"] = pred_SVC["pred_over"]["acc"]
            SVC["pred_under_acc"] = pred_SVC["pred_under"]["acc"]
            SVC["pred_odds_over"] = pred_SVC["pred_over"]["prediction_odds"]
            SVC["pred_odds_under"] = pred_SVC["pred_under"]["prediction_odds"]
            predictions["SVC"] = SVC

            #XGBoost
            XGB = {}
            XGB["pred_over"] = pred_xgb["pred_over"]["prediction"]
            XGB["pred_under"] = pred_xgb["pred_under"]["prediction"]
            XGB["pred_over_acc"] = pred_xgb["pred_over"]["acc"]
            XGB["pred_under_acc"] = pred_xgb["pred_under"]["acc"]
            XGB["pred_odds_over"] = pred_xgb["pred_over"]["prediction_odds"]
            XGB["pred_odds_under"] = pred_xgb["pred_under"]["prediction_odds"]
            predictions["XGBoost"] = XGB


            total.append(full)

'''
'''
# # Save all predictions into one csv (or excel) file
for stat in total:
    excel_io.save_data(stat)
'''