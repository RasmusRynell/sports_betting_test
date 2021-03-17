import data_processing.create_csv as create_csv
import user_io.bet365 as bet365_data
import Settings
import pred_models.pred_SVC_v1 as svc
import pred_models.pred_XGBoost_v1 as xgb


# Get data from bet365
games = bet365_data.get_from_clipboard()

# Add home or away team
for game in games:
    home = input("Is \"{}\" the home team (TRUE, True, T or t for True...) = ".format(games[game]["team_one"]))
    if (home == "TRUE") or (home == "True") or (home == "T") or (home == "t"):
        games[game]["home_team"] = games[game]["team_one"]
        games[game]["away_team"] = games[game]["team_two"]
    else:
        games[game]["home_team"] = games[game]["team_two"]
        games[game]["away_team"] = games[game]["team_one"]
print(games)


# Generate all csv files and save them
bets = []
for game in games:
    for player_name, values in games[game]["bet365-stat"].items():
        date = games[game]["Date-time"]
        player_team = values["team"]
        opp_team =  games[game]["home_team"] if games[game]["home_team"] != values["team"] else games[game]["away_team"]
        home_or_away = "Home" if games[game]["home_team"] == values["team"] else "Away"
        bet = [player_name, values["team"], opp_team, home_or_away]
        bet = [string.lower() for string in bet]        
        bets.append([bet, [values["over-under"], values["over"], values["under"], player_name, player_team, opp_team, home_or_away, date]])

files = create_csv.create_csv(bets, False)

print(files)
print(files[0][0])
print(files[0][1][0])
total = []

# Call predictor to predict all csv files
for file in files:
    game = {}
    player = {}
    game_info = {}
    predictions = {}
    bet365 = {}
    SVC =  {}
    XGB = {}

    #Pred models
    pred_SVC = svc.pred_SVC(file[0], file[1][0])
    pred_xgb = xgb.pred_XGB(file[0], file[1][0])

    #Saving data

    #Player
    player["name"] = file[1][3]
    player["over-under"] = file[1][0]
    #Game
    game_info["player_team"] = file[1][4]
    game_info["opp_team"] = file[1][5]
    game_info["home_or_away"] = file[1][6]
    game_info["date"] = file[1][7]
    #Bet365
    bet365["bet365_odds_over"] = file[1][1]
    bet365["bet365_odds_under"] = file[1][2]
    #SVC
    SVC["pred_over"] = pred_SVC["pred_over"]["prediction"]
    SVC["pred_under"] = pred_SVC["pred_under"]["prediction"]
    SVC["pred_over_acc"] = pred_SVC["pred_over"]["acc"]
    SVC["pred_under_acc"] = pred_SVC["pred_under"]["acc"]
    SVC["pred_odds_over"] = pred_SVC["pred_over"]["prediction_odds"]
    SVC["pred_odds_under"] = pred_SVC["pred_under"]["prediction_odds"]
    #XGBoost
    XGB["pred_over"] = pred_SVC["pred_over"]["prediction"]
    XGB["pred_under"] = pred_SVC["pred_under"]["prediction"]
    XGB["pred_over_acc"] = pred_SVC["pred_over"]["acc"]
    XGB["pred_under_acc"] = pred_SVC["pred_under"]["acc"]
    XGB["pred_odds_over"] = pred_SVC["pred_over"]["prediction_odds"]
    XGB["pred_odds_under"] = pred_SVC["pred_under"]["prediction_odds"]

    game["player"] = player
    game["game"] = game
    predictions["bet365"] = bet365
    predictions["SVC"] = SVC
    predictions["XGBoost"] = XGB
    predictions["predictions"] = predictions

    total.append(game)

#total = [svc.pred_SVC("./temp/pp_alexander_ovechkin.csv", 2.5)]
print(total)

for pred in total:
    Settings.print_json(pred["predictions"][])


# # Save all predictions into one csv (or excel) file
