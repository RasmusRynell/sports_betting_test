import data_processing.create_csv as csv
import user_io.bet_io as bet_io
import Settings
import pred_models.pred_SVC_v1 as svc
import pred_models.pred_XGBoost_v1 as xgb
from tqdm import tqdm



# Get data from bet365
games = bet_io.get_from_file("./data/old_bets/2021-03-20")
#Settings.print_json(games)
#[date, player, home_name, away_name, site, O, U, U/O-threshold(on finns)]
Settings.bets_database.add_bet("2021-03-25", "William Karlsson", "VGS Golden Knights", "LA Kings", "bet365", "1.62", "2.20", "1.5")

Settings.api.save_api_cache()
Settings.bets_database.save_to_json_file()

'''
games = bet365_io.get_from_clipboard()


for game_key in tqdm(games):
    for player_key in tqdm(games[game_key]["bet365-stat"]):
        games[game_key]["bet365-stat"][player_key]["name"] = player_key
        games[game_key]["bet365-stat"][player_key]["date"] = games[game_key]["Date-time"]
        games[game_key]["bet365-stat"][player_key]["ply_team_name"] = games[game_key]["bet365-stat"][player_key]["team"]
        games[game_key]["bet365-stat"][player_key]["opp_team_name"] = games[game_key]["team_one"] if\
        games[game_key]["bet365-stat"][player_key]["team"] == games[game_key]["team_two"] else games[game_key]["team_two"]

        # Generate one file with all players, (add to existing one)
        games[game_key]["bet365-stat"][player_key]["file-path"] = csv.create_csv(games[game_key]["bet365-stat"][player_key], "", "./temp2/pp_all.csv")

        # Generate one file for each player, (do not add to existing one!)
        #games[game_key]["bet365-stat"][player_key]["file-path"] = csv.create_csv(games[game_key]["bet365-stat"][player_key])
Settings.print_json(games)


print("Saving_cache")
Settings.api.save_api_cache()

total = []

# Call predictor to predict all csv files
for bet_game_id in tqdm(games):
    for player_id in tqdm(games[bet_game_id]["bet365-stat"]):
        file = games[bet_game_id]["bet365-stat"][player_id]["file-path"]
        if file:
            over_under = games[bet_game_id]["bet365-stat"][player_id]["over-under"]
            game = {}
            basic_data = {}
            predictions = {}
            bet365 = {}
            SVC =  {}
            XGB = {}

            print(file)

            #Pred models
            pred_SVC = svc.pred_SVC(file, over_under)
            pred_xgb = xgb.pred_XGB(file, over_under)

            #Saving data

            #Player
            basic_data["player_name"] = games[bet_game_id]["bet365-stat"][player_id]["name"]
            basic_data["over-under"] = over_under

            #Game
            basic_data["player_team"] = games[bet_game_id]["bet365-stat"][player_id]["ply_team_name"]
            basic_data["opp_team"] = games[bet_game_id]["bet365-stat"][player_id]["opp_team_name"]
            #basic_data["home_or_away"] = games[bet_game_id]["bet365-stat"][player_id]["ply_team_name"]
            basic_data["date"] = games[bet_game_id]["bet365-stat"][player_id]["date"]

            #Bet365
            bet365["bet365_odds_over"] = games[bet_game_id]["bet365-stat"][player_id]["over"]
            bet365["bet365_odds_under"] = games[bet_game_id]["bet365-stat"][player_id]["under"]

            #SVC
            SVC["pred_over"] = pred_SVC["pred_over"]["prediction"]
            SVC["pred_under"] = pred_SVC["pred_under"]["prediction"]
            SVC["pred_over_acc"] = pred_SVC["pred_over"]["acc"]
            SVC["pred_under_acc"] = pred_SVC["pred_under"]["acc"]
            SVC["pred_odds_over"] = pred_SVC["pred_over"]["prediction_odds"]
            SVC["pred_odds_under"] = pred_SVC["pred_under"]["prediction_odds"]

            #XGBoost
            XGB["pred_over"] = pred_xgb["pred_over"]["prediction"]
            XGB["pred_under"] = pred_xgb["pred_under"]["prediction"]
            XGB["pred_over_acc"] = pred_xgb["pred_over"]["acc"]
            XGB["pred_under_acc"] = pred_xgb["pred_under"]["acc"]
            XGB["pred_odds_over"] = pred_xgb["pred_over"]["prediction_odds"]
            XGB["pred_odds_under"] = pred_xgb["pred_under"]["prediction_odds"]

            game["basic_data"] = basic_data
            predictions["bet365"] = bet365
            predictions["SVC"] = SVC
            predictions["XGBoost"] = XGB
            game["predictions"] = predictions

            total.append(game)



# # Save all predictions into one csv (or excel) file
for stat in total:
    excel_io.save_data(stat)
    '''